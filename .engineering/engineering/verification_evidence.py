"""Decide whether stored verification evidence is valid, current and complete.

Decisions are pure functions of gathered evidence facts (verification_facts)
and the request: they read no files, start no processes and touch no clock or
environment. JSON arguments are frozen first, so plain and gathered values
compare alike.
"""

from collections.abc import Mapping
from typing import Any  # JSON evidence is validated by these decisions.

from .verification_facts import EvidenceFacts, StoredRecord, frozen_json, plain_json
from .verification_inputs import strings
from .verification_requirements import REVIEWERS, TIERS
from .verification_snapshot import identity, plan_shape

# Version 3 replaces maintainability with distinct native Standards and Spec proof.
SCHEMA = 3
# Native review axes, which also name the reviewed commit and comparison base.
AXES = ("standards", "spec")
SESSIONS = {
    "documentation": "Documentation tier: one behavioral review.",
    "ordinary": "Ordinary tier: native axes and behavioral inspection use separate fresh sessions.",
    "sensitive": "Sensitive tier: each role needs its own fresh session.",
}


def validate_report(report: Mapping[str, Any], token: str) -> None:
    """Validate explicit independent attestations; do not claim identity authentication."""
    report = frozen_json(report)
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
        strings(plain_json(report[field]), field, empty=True)


def validate_records(
    records: tuple[StoredRecord, ...],
) -> tuple[Mapping[str, Any], ...]:
    """Refuse unsupported or incomplete record structure instead of assuming proof.

    Records are the stored record, then the history its carried reports name.
    Returns the validated records: the stored one, then the history relied on.
    """
    return validate_record(records[0].data, records[1:])


def validate_record(
    data: Any, history: tuple[StoredRecord, ...]
) -> tuple[Mapping[str, Any], ...]:
    """Validate one record and, for carried reports, the history behind it."""
    data = frozen_json(data)
    if (
        type(data.get("schema_version")) is not int
        or data["schema_version"] != SCHEMA
        or not isinstance(data.get("inputs"), Mapping)
        or not isinstance(data.get("requirements"), Mapping)
        or not isinstance(data.get("reports"), Mapping)
        or not isinstance(data.get("checks"), tuple)
        or not isinstance(data.get("snapshot"), str)
    ):
        raise ValueError("Invalid or unsupported verification record; prepare again")
    plan = data["inputs"].get("plan")
    if not isinstance(plan, Mapping):
        raise ValueError("Invalid stored plan")
    plan_shape(plain_json(plan))
    stored = data["requirements"]
    if (
        set(stored) != {"floor", "paths", "checks", "roles"}
        or stored["floor"] not in TIERS
        or stored["roles"] != tuple(REVIEWERS[plan["tier"]])
    ):
        raise ValueError("Invalid stored requirements; prepare again")
    validated: tuple[Mapping[str, Any], ...] = (data,)
    previous = None
    for role, report in data["reports"].items():
        if not isinstance(report, Mapping):
            raise ValueError("Invalid stored report")
        validate_report(
            {key: value for key, value in report.items() if key != "carried_from"},
            data["snapshot"],
        )
        if "carried_from" in report:
            if not isinstance(data.get("previous_evidence"), str):
                raise ValueError("Carried report requires previous evidence")
            if previous is None:
                previous = readable(history)
                validated += validate_record(previous, history[1:])
            original = previous["reports"].get(role)
            if (
                report["carried_from"] != previous["snapshot"]
                or not isinstance(original, Mapping)
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
    for item in data["checks"]:
        if (
            not isinstance(item, Mapping)
            or set(item) != {"command", "exit_code", "stdout", "stderr"}
            or type(item["exit_code"]) is not int
            or not isinstance(item["stdout"], str)
            or not isinstance(item["stderr"], str)
        ):
            raise ValueError("Invalid recorded command result")
        strings(plain_json(item["command"]), "recorded command")
    return validated


def readable(history: tuple[StoredRecord, ...]) -> Mapping[str, Any]:
    """The next history record, or why carried proof cannot rely on it."""
    if history and history[0].cyclic:
        raise ValueError("Invalid cyclic verification history; prepare fresh evidence")
    if not history or history[0].data is None:
        raise ValueError(
            "Carried evidence history is unavailable; prepare again for fresh proof"
        )
    return history[0].data


def reject_unsupported_schema(data: Mapping[str, Any] | None) -> None:
    """Known older contracts are preserved as history; others are never touched."""
    if data is None:
        return
    version = data.get("schema_version")
    if type(version) is not int or version not in (1, 2, SCHEMA):
        raise ValueError(
            "Unsupported verification schema; use compatible tooling or archive the record before prepare again"
        )


def stale(facts: EvidenceFacts) -> bool:
    """Whether the current snapshot differs from the stored record's.

    The advisory base tip is excluded, so a moved comparison branch with the
    same merge base keeps evidence current.
    """
    data = frozen_json(facts.records[0].data)
    return facts.token != data["snapshot"] or identity(
        frozen_json(facts.inputs)
    ) != identity(data["inputs"])


def admit(facts: EvidenceFacts, report: Mapping[str, Any]) -> None:
    """Refuse a validated report that would share a session or lacks checks."""
    data, report = frozen_json(facts.records[0].data), frozen_json(report)
    reports = {**data["reports"], report["role"]: report}
    if shared := shared_reviewers(reports):
        raise ValueError(f"Independent roles require separate fresh sessions: {shared}")
    if report["role"] == "behavioral" and report["verdict"] == "PASS":
        checks = data["checks"]
        if (
            not checks
            or any(check["exit_code"] for check in checks)
            or tuple(check["command"] for check in checks)
            != data["inputs"]["plan"]["checks"]
        ):
            raise ValueError(
                "Behavioral PASS requires successful recorded authoritative checks"
            )


def outcome(data: Mapping[str, Any]) -> dict[str, Any]:
    """Summarize completeness without equating recorded proof with acceptance."""
    data = frozen_json(data)
    plan = data["inputs"]["plan"]
    roles = REVIEWERS[plan["tier"]]
    missing_roles = [role for role in roles if role not in data["reports"]]
    missing = list(missing_roles)
    shared = shared_reviewers(data["reports"])
    if shared:
        missing.append(f"separate sessions for independent review: {shared}")
    checks = data["checks"]
    if tuple(item["command"] for item in checks) != plan["checks"]:
        missing.append("authoritative checks")
    failed = any(item["exit_code"] != 0 for item in checks)
    failed |= any(report["verdict"] != "PASS" for report in data["reports"].values())
    status = "FAIL" if failed else "INCOMPLETE" if missing else "PASS"
    result: dict[str, Any] = plain_json(
        {
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
            "handoff": handoff(data, plan["tier"]) if missing else "",
            "meaning": "Recorded verification evidence only; not human acceptance or publication authorization.",
        }
    )
    return result


def handoff(data: Mapping[str, Any], tier: str) -> str:
    """Who obtains the missing proof: the implementer for carried reports' checks."""
    if any("carried_from" in report for report in data["reports"].values()):
        return (
            "Carried reports: the implementer may run verify check for this snapshot. "
            "Missing roles still require fresh independent review. "
        )
    return (
        "Fresh read-only reviewer: inspect the plan requirement and actual scope; "
        "record missing roles. No implementer self-review. " + SESSIONS[tier]
    )


def shared_reviewers(reports: Mapping[str, Any]) -> dict[str, list[str]]:
    """Reviewer identifiers that filed more than one role, with those roles."""
    roles: dict[str, list[str]] = {}
    for role, report in sorted(reports.items()):
        roles.setdefault(report["reviewer"], []).append(role)
    return {reviewer: names for reviewer, names in roles.items() if len(names) > 1}
