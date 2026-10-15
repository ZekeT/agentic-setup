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
from .verification_evidence import (
    SCHEMA,
    admit,
    outcome,
    reject_unsupported_schema,
    stale,
    validate_records,
    validate_report,
)
from .verification_execution import evidence_lock, execute_checks
from .verification_facts import (
    EvidenceFacts,
    StoredRecord,
    frozen_json,
    plain_json,
    stored_history,
)
from .verification_inputs import STATE
from .verification_semantic import validate_semantic
from .verification_snapshot import read_plan, snapshot, validate_plan


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


def read_record(root: Path, name: str) -> dict[str, Any]:
    """Valid stored evidence, refusing unsupported or incomplete structure."""
    data = json_object(safe_path(root, name).read_bytes())
    verified(root, name, data)
    return data


def verified(root: Path, name: str, data: dict[str, Any]) -> tuple[StoredRecord, ...]:
    """Validate a stored record and its history, then what only the repository shows.

    Plan paths must still be safe, and each fresh native report's commit must
    still cover the content its record captured.
    """
    records = stored_history(root, name, data)
    for record in validate_records(records):
        validate_plan(root, plain_json(record["inputs"]["plan"]))
        for report in record["reports"].values():
            if "carried_from" not in report:
                validate_semantic(root, report, record["inputs"])
    return records


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
        data = prepare(root, args, name)
    elif not path.exists():
        print(
            json.dumps(
                {
                    "status": "INCOMPLETE",
                    "missing": ["prepare and independent verification"],
                }
            )
        )
        return 1
    else:
        data = json_object(path.read_bytes())
        records = verified(root, name, data)
        token, inputs = snapshot(root, data["inputs"]["plan"])
        facts = EvidenceFacts(token, frozen_json(inputs), records)
        if stale(facts):
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
            admit(facts, report)
            data["reports"][report["role"]] = report
            write_files(root, {name: encoded(data)})
    result = outcome(data)
    print(json.dumps(result, indent=2))
    if args.operation == "status":
        return int(result["status"] != "PASS")
    if args.operation == "check":
        return int(any(item["exit_code"] for item in data["checks"]))
    return 0


def prepare(root: Path, args: argparse.Namespace, name: str) -> dict[str, Any]:
    """Store current inputs, reusing current proof or carrying it after a rebase."""
    path = safe_path(root, name)
    plan = read_plan(root, args.plan)
    token, inputs = snapshot(root, plan)
    data: dict[str, Any] = {
        "schema_version": SCHEMA,
        "snapshot": token,
        "inputs": inputs,
        "checks": [],
        "reports": {},
    }
    previous = json_object(path.read_bytes()) if path.exists() else None
    reject_unsupported_schema(previous)
    records: tuple[StoredRecord, ...] = ()
    # Known older contracts are preserved as history, never relabelled.
    if previous is not None and previous["schema_version"] == SCHEMA:
        try:
            records = verified(root, name, previous)
        except (ValueError, OSError, subprocess.CalledProcessError) as exc:
            # Unverifiable history is preserved, never reused.
            data["history_note"] = f"Previous evidence was not reused: {exc}"
    facts = EvidenceFacts(token, frozen_json(inputs), records)
    if previous is not None and records and not stale(facts):
        try:
            validate_checkout(safe_path(root, previous.get("checkout", "")), inputs)
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
            if records:
                data["reports"] = carried_reports(root, previous, data)
    else:
        reused = safe_path(root, data["checkout"])
        validate_checkout(reused, inputs)
        data["requirements"] = checkout_requirements(root, reused, inputs)
    write_files(root, {name: encoded(data)})
    return data
