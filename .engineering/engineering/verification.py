"""Local verification evidence: prepare, check, record independent reports, reuse."""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .config import safe_path
from .ownership import encoded, json_object
from .source import git
from .transaction import write_files
from .verification_carry import carried_reports
from .verification_checkout import (
    checkout_requirements,
    materialize,
    validate_checkout,
)
from .verification_execution import evidence_lock, execute_checks
from .verification_inputs import STATE, strings
from .verification_requirements import REVIEWERS, TIERS
from .verification_semantic import AXES, validate_semantic
from .verification_snapshot import (
    identity,
    read_plan,
    snapshot,
    validate_plan,
)

# Version 3 replaces maintainability with distinct native Standards and Spec proof.
SCHEMA = 3
SESSIONS = {
    "documentation": "Documentation tier: one behavioral review.",
    "ordinary": "Ordinary tier: native axes and behavioral inspection use separate fresh sessions.",
    "sensitive": "Sensitive tier: each role needs its own fresh session.",
}


def add_parser(sub: Any) -> None:
    """Expose one small command family without a new application lifecycle."""
    parser = sub.add_parser(
        "verify", help="Prepare and reuse independent verification evidence"
    )
    parser.add_argument("operation", choices=["prepare", "check", "record", "status"])
    parser.add_argument("--change", required=True, help="Local evidence identifier")
    parser.add_argument("--plan", help="Repository-relative JSON plan (prepare only)")
    parser.add_argument("--snapshot", help="Prepared identity (check only)")
    parser.add_argument("--report", help="Independent JSON report (record only)")


def location(root: Path, change: str) -> str:
    """Require safe, ignored, untracked local evidence storage."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", change):
        raise ValueError("change must be a lowercase slug (maximum 80 characters)")
    name = f"{STATE}/{change}.json"
    safe_path(root, name)
    if git(root, "ls-files", "--", STATE):
        raise ValueError("Verification records must not be tracked")
    try:
        git(root, "check-ignore", "--quiet", "--", name)
    except ValueError as exc:
        raise ValueError(f"Ignore /{STATE}/ before preparing evidence") from exc
    return name


def read_record(
    root: Path, name: str, *, seen: frozenset[Path] = frozenset()
) -> dict[str, Any]:
    """Refuse unsupported or incomplete record structure instead of assuming proof."""
    path = safe_path(root, name)
    if path in seen:
        raise ValueError("Invalid cyclic verification history; prepare fresh evidence")
    seen = seen | {path}
    data = json_object(path.read_bytes())
    if (
        type(data.get("schema_version")) is not int
        or data["schema_version"] != SCHEMA
        or not isinstance(data.get("inputs"), dict)
        or not isinstance(data.get("requirements"), dict)
        or not isinstance(data.get("reports"), dict)
        or not isinstance(data.get("checks"), list)
        or not isinstance(data.get("snapshot"), str)
    ):
        raise ValueError("Invalid or unsupported verification record; prepare again")
    plan = data["inputs"].get("plan")
    if not isinstance(plan, dict):
        raise ValueError("Invalid stored plan")
    validate_plan(root, plan)
    stored = data["requirements"]
    if (
        set(stored) != {"floor", "paths", "checks", "roles"}
        or stored["floor"] not in TIERS
        or stored["roles"] != REVIEWERS[plan["tier"]]
    ):
        raise ValueError("Invalid stored requirements; prepare again")
    previous = None
    for role, report in data["reports"].items():
        if not isinstance(report, dict):
            raise ValueError("Invalid stored report")
        validate_report(
            {key: value for key, value in report.items() if key != "carried_from"},
            data["snapshot"],
        )
        if "carried_from" in report:
            history = data.get("previous_evidence")
            if not isinstance(history, str):
                raise ValueError("Carried report requires previous evidence")
            if previous is None:
                try:
                    previous = read_record(root, history, seen=seen)
                except OSError as exc:
                    raise ValueError(
                        "Carried evidence history is unavailable; prepare again for fresh proof"
                    ) from exc
            original = previous.get("reports", {}).get(role)
            if (
                report["carried_from"] != previous.get("snapshot")
                or not isinstance(original, dict)
                or report
                != {
                    **original,
                    "snapshot": data["snapshot"],
                    "carried_from": previous["snapshot"],
                }
            ):
                raise ValueError("Carried report differs from previous evidence")
        if report["role"] != role:
            raise ValueError("Stored reviewer role differs from report")
        if "carried_from" not in report:
            validate_semantic(root, report, data["inputs"])
    for item in data["checks"]:
        if (
            not isinstance(item, dict)
            or set(item) != {"command", "exit_code", "stdout", "stderr"}
            or type(item["exit_code"]) is not int
            or not isinstance(item["stdout"], str)
            or not isinstance(item["stderr"], str)
        ):
            raise ValueError("Invalid recorded command result")
        strings(item["command"], "recorded command")
    return data


def outcome(data: dict[str, Any]) -> dict[str, Any]:
    """Summarize completeness without equating recorded proof with acceptance."""
    plan = data["inputs"]["plan"]
    roles = REVIEWERS[plan["tier"]]
    missing_roles = [role for role in roles if role not in data["reports"]]
    missing = list(missing_roles)
    shared = shared_reviewers(data["reports"])
    if shared:
        missing.append(f"separate sessions for independent review: {shared}")
    checks = data["checks"]
    if [item["command"] for item in checks] != plan["checks"]:
        missing.append("authoritative checks")
    failed = any(item["exit_code"] != 0 for item in checks)
    failed |= any(report["verdict"] != "PASS" for report in data["reports"].values())
    status = "FAIL" if failed else "INCOMPLETE" if missing else "PASS"
    return {
        "status": status,
        "snapshot": data["snapshot"],
        "checkout": data.get("checkout"),
        "check_checkout": data.get("check_checkout"),
        "previous_evidence": data.get("previous_evidence"),
        "history_note": data.get("history_note"),
        "starter_source": {
            key: value
            for key, value in data["inputs"].get("starter_source", {}).items()
            if key != "manifest"
        },
        "tier": plan["tier"],
        "tier_reason": plan["tier_reason"],
        "floor": data["requirements"]["floor"],
        "required_roles": roles,
        "missing_roles": missing_roles,
        "shared_reviewers": shared,
        "missing": missing,
        "reports": data["reports"],
        "checks": checks,
        "handoff": (
            "Carried reports: the implementer may run verify check for this snapshot. "
            "Missing roles still require fresh independent review. "
        )
        if missing
        and any("carried_from" in report for report in data["reports"].values())
        else "Fresh read-only reviewer: inspect the plan requirement and actual scope; record missing roles. No implementer self-review. "
        + SESSIONS[plan["tier"]]
        if missing
        else "",
        "meaning": "Recorded verification evidence only; not human acceptance or publication authorization.",
    }


def shared_reviewers(reports: dict[str, Any]) -> dict[str, list[str]]:
    """Reviewer identifiers that filed more than one role, with those roles."""
    roles: dict[str, list[str]] = {}
    for role, report in sorted(reports.items()):
        roles.setdefault(report["reviewer"], []).append(role)
    return {reviewer: names for reviewer, names in roles.items() if len(names) > 1}


def validate_report(report: dict[str, Any], token: str) -> None:
    """Validate explicit independent attestations; do not claim identity authentication."""
    semantic_fields = (
        {"reviewed_commit", "comparison_base"} if report.get("role") in AXES else set()
    )
    if not semantic_fields <= set(report):
        raise ValueError("Native reports require reviewed_commit and comparison_base")
    if set(report) - semantic_fields != {
        "snapshot",
        "role",
        "reviewer",
        "independent",
        "verdict",
        "summary",
        "findings",
        "coverage_gaps",
    }:
        raise ValueError(
            "Report fields: snapshot, role, reviewer, independent, verdict, summary, findings, coverage_gaps"
        )
    if report["snapshot"] != token:
        raise ValueError("STALE report: snapshot differs; reverify current content")
    if report["role"] not in (*AXES, "behavioral", "security"):
        raise ValueError("Unknown reviewer role")
    if report["independent"] is not True:
        raise ValueError(
            "Independent review required; implementer self-review is not proof"
        )
    if report["verdict"] not in ("PASS", "FAIL", "CONCERNS"):
        raise ValueError("Report verdict must be PASS, FAIL or CONCERNS")
    for field in ("summary", "reviewer"):
        if not isinstance(report[field], str) or not report[field].strip():
            raise ValueError(f"Report {field} must be nonempty text")
    for field in ("findings", "coverage_gaps"):
        strings(report[field], field, empty=True)


def operate(root: Path, args: argparse.Namespace) -> int:
    """Serialize evidence readers and writers for the selected change."""
    name = location(root, args.change)
    with evidence_lock(root, name):
        return operate_locked(root, args, name)


def operate_locked(root: Path, args: argparse.Namespace, name: str) -> int:
    """Perform one evidence operation and emit a readable JSON result."""
    allowed = {
        "prepare": "plan",
        "check": "snapshot",
        "record": "report",
        "status": None,
    }
    for field in ("plan", "snapshot", "report"):
        if bool(getattr(args, field)) != (allowed[args.operation] == field):
            raise ValueError(
                f"{args.operation}: requires only --{allowed[args.operation]}"
                if allowed[args.operation]
                else "status accepts only --change"
            )
    path = safe_path(root, name)
    if args.operation == "prepare":
        plan = read_plan(root, args.plan)
        token, inputs = snapshot(root, plan)
        data: dict[str, Any] = {
            "schema_version": SCHEMA,
            "snapshot": token,
            "inputs": inputs,
            "checks": [],
            "reports": {},
        }
        previous = None
        if path.exists():
            previous = json_object(path.read_bytes())
            version = previous.get("schema_version")
            if type(version) is not int or version not in (1, 2, SCHEMA):
                raise ValueError(
                    "Unsupported verification schema; use compatible tooling or archive the record before prepare again"
                )
            # Known older contracts are preserved as history, never relabelled.
            reusable = previous.get("schema_version") == SCHEMA
            if reusable:
                try:
                    previous = read_record(root, name)
                except (ValueError, OSError, subprocess.CalledProcessError) as exc:
                    reusable = False  # Unverifiable history is preserved, never reused.
                    data["history_note"] = f"Previous evidence was not reused: {exc}"
            if (
                reusable
                and previous["snapshot"] == token
                and identity(previous["inputs"]) == identity(inputs)
            ):
                try:
                    validate_checkout(
                        safe_path(root, previous.get("checkout", "")), inputs
                    )
                except (ValueError, OSError):
                    pass  # A fresh checkout requires fresh independent proof.
                else:
                    data = {**previous, "inputs": inputs}
        if "checkout" not in data:
            folder = Path(tempfile.mkdtemp(prefix=f"{args.change}-", dir=path.parent))
            checkout = folder / "checkout"
            try:
                data["requirements"] = materialize(root, checkout, inputs)
            except (ValueError, OSError):
                shutil.rmtree(folder)
                raise
            data["checkout"] = str(checkout.relative_to(root))
            if previous is not None:
                history = str((folder / "previous.json").relative_to(root))
                write_files(root, {history: encoded(previous)})
                data["previous_evidence"] = history
                if reusable:
                    data["reports"] = carried_reports(root, previous, data)
        else:
            reused = safe_path(root, data["checkout"])
            validate_checkout(reused, inputs)
            data["requirements"] = checkout_requirements(root, reused, inputs)
        write_files(root, {name: encoded(data)})
    else:
        if not path.exists():
            print(
                json.dumps(
                    {
                        "status": "INCOMPLETE",
                        "missing": ["prepare and independent verification"],
                    }
                )
            )
            return 1
        data = read_record(root, name)
        token, inputs = snapshot(root, data["inputs"]["plan"])
        if token != data["snapshot"] or identity(inputs) != identity(data["inputs"]):
            print(
                json.dumps(
                    {
                        "status": "STALE",
                        "handoff": "Prepare current inputs and obtain fresh independent verification.",
                    }
                )
            )
            return 1
        checkout = safe_path(root, data.get("checkout", ""))
        validate_checkout(checkout, inputs)
        # Report the floor current rules give this scope, not the prepared one.
        data["requirements"] = checkout_requirements(root, checkout, inputs)
        if args.operation == "check":
            if args.snapshot != token:
                raise ValueError("STALE check request: obtain the current snapshot")
            execute_checks(root, name, data)
        elif args.operation == "record":
            report = json_object(safe_path(root, args.report).read_bytes())
            validate_report(report, token)
            validate_semantic(root, report, inputs)
            reports = {**data["reports"], report["role"]: report}
            if shared := shared_reviewers(reports):
                raise ValueError(
                    f"Independent roles require separate fresh sessions: {shared}"
                )
            if report["role"] == "behavioral" and report["verdict"] == "PASS":
                if (
                    not data["checks"]
                    or any(c["exit_code"] for c in data["checks"])
                    or [c["command"] for c in data["checks"]]
                    != data["inputs"]["plan"]["checks"]
                ):
                    raise ValueError(
                        "Behavioral PASS requires successful recorded authoritative checks"
                    )
            data["reports"][report["role"]] = report
            write_files(root, {name: encoded(data)})
    result = outcome(data)
    print(json.dumps(result, indent=2))
    if args.operation == "status":
        return int(result["status"] != "PASS")
    if args.operation == "check":
        return int(any(item["exit_code"] for item in data["checks"]))
    return 0
