"""Read-only advice about an explicitly selected workspace."""

import json
import shlex
from pathlib import Path
from typing import Any

from .adopt import REGION, SOURCE, metadata_directory
from .discovery import native_commands, standards
from .files import Plan, checked_root, digest, git, path_at
from .skills import BUNDLES, skill_locations
from .templates import compare_template


def record_at(plan: Plan, name: str) -> dict[str, Any]:
    raw = plan.inspect(name)
    if raw is None:
        return {}
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f"Invalid metadata object: {name}")
    return value


def convention_report(plan: Plan, record: dict[str, Any]) -> list[str]:
    files = record.get("files", {})
    if not isinstance(files, dict) or not all(
        isinstance(name, str) and isinstance(text, str) for name, text in files.items()
    ):
        raise ValueError(
            "Invalid installation metadata: files must map paths to template text"
        )
    lines = ["Conventions (file comparison, not a code-quality assessment):"]
    for source in sorted((SOURCE / "payload").rglob("*")):
        if not source.is_file():
            continue
        name = source.relative_to(SOURCE / "payload").as_posix()
        local = plan.inspect(name)
        previous = files[name].encode() if name in files else None
        comparison = compare_template(local, previous, source.read_bytes())
        lines.append(f"  {comparison.status.value}: {name}")
    existing = standards(plan)
    lines.append(
        "Standards found: " + (", ".join(existing) or "none in inspected locations")
    )
    instructions = [
        name for name in ("CLAUDE.md", "AGENTS.md") if plan.inspect(name) is not None
    ]
    lines.append("Agent instructions: " + (", ".join(instructions) or "missing"))
    if not any(
        b"docs/agents/workflow.md" in (plan.inspect(name) or b"")
        for name in instructions
    ):
        lines.append(
            "  No direct workflow reference found; inspect existing instruction imports."
        )
    for name in (
        "docs/agents/checks.md",
        "docs/agents/domain.md",
        "docs/agents/issue-tracker.md",
    ):
        lines.append(
            f"  {'present' if plan.inspect(name) is not None else 'missing'}: {name}"
        )
    return lines


def skill_report(plan: Plan, metadata: str) -> list[str]:
    records = record_at(plan, f"{metadata}/skills.json")
    for name, record in records.items():
        if not isinstance(record, dict) or not all(
            isinstance(record.get(key), str) for key in ("source", "commit")
        ):
            raise ValueError(f"Invalid skill revision record: {name}")
    installed = skill_locations(plan)
    selected = {
        name: (source, revision)
        for source, revision, names in BUNDLES.values()
        for name in names
    }
    lines = ["Skills (recorded revisions; installed contents not verified):"]
    for name in sorted(installed.keys() | records.keys()):
        locations = installed.get(name, [])
        record = records.get(name)
        if not locations:
            status = "recorded but missing"
        elif record is None:
            status = "unrecorded revision"
        else:
            status = f"recorded {record['source']}@{record['commit']}"
            expected = selected.get(name)
            if expected:
                status += (
                    "; matches bundled selection"
                    if expected == (record["source"], record["commit"])
                    else "; differs from bundled selection (not necessarily outdated)"
                )
        lines.append(f"  {name}: {status}")
        lines.extend(f"    {location}" for location in locations)
        if len(locations) > 1:
            lines.append(
                f"  Duplicate exposed skill name: {name}; reconcile before installing."
            )
    for bundle, (_, _, names) in BUNDLES.items():
        missing = [name for name in names if name not in installed]
        if missing:
            lines.append(f"  Bundle {bundle}, not found: {', '.join(missing)}")
    lines.append(
        "Upstream freshness: not checked; bundle choices are optional, not compliance requirements."
    )
    return lines


def legacy_report(plan: Plan) -> tuple[list[str], bool, bool]:
    catalog = json.loads((SOURCE / "legacy.json").read_text())["paths"]
    known: list[str] = []
    customized: list[str] = []
    for name, hashes in catalog.items():
        if not (name.startswith(".engineering/") or name == "engineering"):
            continue
        raw = plan.inspect(name)
        if raw is not None:
            (known if digest(raw) in hashes["files"] else customized).append(name)
    markers = [
        name
        for name in ("CLAUDE.md", "AGENTS.md", "ENGINEERING.md")
        if REGION.search(plan.inspect(name) or b"")
    ]
    older = [
        name for name in (".factory", ".harness") if path_at(plan.root, name).exists()
    ]
    lines = []
    if known:
        lines.append("Legacy: recognized Agentic Starter installation")
        lines.append(
            f"  {len(known)} known legacy files; {len(customized)} customized remnants."
        )
    elif customized or markers:
        lines.append(
            "Legacy: possible customized Agentic Starter remnants; review the adoption preview."
        )
    else:
        lines.append("Legacy: no recognized v2 files or integration markers found.")
    version = plan.inspect(".engineering/TEMPLATE_VERSION")
    if version:
        lines.append("  Recorded legacy version: " + version.decode().strip())
    if markers:
        lines.append("  Integration markers: " + ", ".join(markers))
    if older:
        lines.append(
            "Legacy: "
            + ", ".join(older)
            + " requires manual reconciliation; automatic adoption is blocked."
        )
    return lines, bool(known or customized or markers), bool(older)


def inspect_target(target: Path) -> str:
    target = checked_root(target)
    lines = [
        f"Target: {target}",
        "Read-only inspection; no target commands executed or online checks.",
    ]
    if not target.exists():
        lines.append("Setup: new destination")
        if target.parent.is_dir():
            lines.append(f"Next: agentic init {shlex.quote(str(target))}")
        else:
            lines.append("Next: create the destination parent, then run agentic init.")
        return "\n".join(lines)
    if not target.is_dir():
        raise ValueError("Target must be a workspace directory or a new destination")
    plan = Plan(target, "")
    git_root = None
    try:
        git_root = Path(git(target, "rev-parse", "--show-toplevel")).resolve()
    except ValueError as exc:
        if "not a git repository" not in str(exc):
            raise
    if git_root is None:
        lines.append(
            "Git: no repository; run git init and commit the baseline before adoption or skill installation."
        )
    elif git_root != target:
        lines.append(
            f"Git: target is inside {git_root}; adoption requires the project root."
        )
    else:
        try:
            plan.baseline = git(target, "rev-parse", "HEAD")
        except ValueError:
            lines.append(
                "Git: no commit; commit the baseline before adoption or skill installation."
            )
        else:
            lines.append(f"Git baseline: {plan.baseline}")
    metadata = metadata_directory(plan)
    record = record_at(plan, f"{metadata}/install.json")
    lines.append(
        "Setup: installed conventions" if record else "Setup: existing workspace"
    )
    if plan.inspect(f"{metadata}/install.json") is not None:
        version = record.get("version")
        if not isinstance(record.get("files"), dict):
            raise ValueError("Invalid installation metadata: files must be an object")
        if not isinstance(version, str):
            raise ValueError("Invalid installation metadata: version must be text")
        lines.append(f"Installed version: {version}; metadata: {metadata}")
    legacy_lines, legacy, older = legacy_report(plan)
    lines.extend(legacy_lines)
    lines.extend(convention_report(plan, record))
    if record:
        lines.append(
            "For available template changes: use agentic update with --only explanation/git/workflow/standards and --source-ref FULL_COMMIT. Review conflicts manually; missing installed files need restoration or reconciliation."
        )
    lines.extend(skill_report(plan, metadata))
    lines.append(native_commands(plan).strip())
    if (
        target == SOURCE.parent
        or target.is_relative_to(SOURCE.parent)
        or SOURCE.parent.is_relative_to(target)
    ):
        lines.append(
            "Next: select a target outside the Agentic Setup checkout; consumer template comparisons are not maintainer requirements."
        )
    elif git_root is not None and git_root != target:
        lines.append(f"Next: agentic inspect {shlex.quote(str(git_root))}")
    elif older or (legacy and record):
        lines.append(
            "Next: reconcile legacy remnants manually before further setup; installed conventions do not imply legacy files were removed."
        )
    else:
        minimal = " --minimal" if legacy else ""
        lines.append(
            f"Next: agentic adopt {shlex.quote(str(target))}{minimal} (preview missing setup; preserve project rules)"
        )
    return "\n".join(lines)
