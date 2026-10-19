"""Inspect legacy wiring and install a small, project-independent workflow."""

import json
import os
import re
from pathlib import Path
from typing import Any

from .files import Plan, digest, encoded, git

SOURCE = Path(__file__).resolve().parent
RECORD = ".starter/install.json"
REGION = re.compile(
    rb"(?m)^(?:<!-- |# )engineering:(integration|navigation):begin(?: -->)?\n.*?^(?:<!-- |# )engineering:\1:end(?: -->)?(?:\n|$)",
    re.S,
)
RETIRED = re.compile(
    rb"engineering\s+(?:verify|publish|doctor|maintainability|migrate)|engineering-(?:check|test|evals)|/ship\b|verification ledger|review tiers|\.engineering/(?:engineering|scripts|docs|bin)|(?:factory|harness):(integration|navigation)",
    re.I,
)
NATIVE_MAKE = b"""# Native Python checks retained from the previous starter. No installer runtime.
.PHONY: fmt check
fmt:
\tuv run ruff check --fix src tests
\tuv run ruff format src tests
check:
\tuv run ruff check src tests
\tuv run ruff format --check src tests
\tuv run mypy src
\tuv run pytest
"""


def legacy_changes(plan: Plan) -> None:
    catalog = json.loads((SOURCE / "legacy.json").read_text())["paths"]
    for name, known in catalog.items():
        raw = plan.inspect(name)
        if raw is None:
            continue
        if name == "Makefile":
            replacement = NATIVE_MAKE
        elif name == ".github/workflows/evals.yml":
            replacement = b"name: Native checks\non: [push, pull_request]\njobs:\n  checks:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: astral-sh/setup-uv@v5\n      - run: uv sync --all-extras\n      - run: make check\n"
        elif name == "docs/agents/issue-tracker.md":
            replacement = b"# Issue tracker: local Markdown\n\nUse the installed Matt setup-matt-pocock-skills/issue-tracker-local.md contract.\nKeep specs and tickets in .scratch/. Preserve current tickets and status semantics.\nUpdate task checkboxes and status as criteria are satisfied. Record test results\nand distinguish implementation, review, publication and team delivery. A PR into\na personal integration branch does not close a team delivery issue.\n"
        elif name == "CLAUDE.md":
            replacement = b"# Project instructions\n\nRead docs/agents/workflow.md and the existing project standards.\n"
        elif name == "AGENTS.md":
            replacement = b"# Project instructions\n\nRead CLAUDE.md and docs/agents/workflow.md.\n"
        else:
            replacement = None
        if digest(raw) in known["files"]:
            plan.change(
                name, replacement, "retire starter gates; retain native development"
            )
            continue
        matches = list(REGION.finditer(raw))
        if matches:
            updated = raw
            for match in reversed(matches):
                section = match[1].decode()
                if digest(match[0]) not in known["sections"].get(section, []):
                    plan.conflicts.append(
                        f"{name}: customized {section} section; merge project rules explicitly"
                    )
                    continue
                incoming = (
                    replacement
                    if section == "integration" and name.endswith(".md")
                    else b""
                )
                updated = (
                    updated[: match.start()]
                    + (incoming or b"")
                    + updated[match.end() :]
                )
            plan.change(
                name,
                updated,
                "disconnect recognized sections; preserve surrounding project content",
            )
        else:
            # Customized dormant implementations may stay, but never silently replace policy.
            plan.notes.append(
                f"PRESERVE {name}: customized legacy content; inspect active callers"
            )
            if name in {
                "CLAUDE.md",
                "AGENTS.md",
                "ENGINEERING.md",
                "REVIEW.md",
                "Makefile",
                "engineering",
            } or name.startswith(".claude/"):
                plan.conflicts.append(
                    f"{name}: customized active legacy configuration; reconcile before adoption"
                )


def active_files(root: Path) -> set[str]:
    """Limit inspection to instructions and command configuration, never application data."""
    names = {
        "CLAUDE.md",
        "AGENTS.md",
        "ENGINEERING.md",
        "REVIEW.md",
        "Makefile",
        "package.json",
        ".claude/settings.json",
        ".claude/settings.local.json",
    }
    tracked = git(
        root, "ls-files", "--cached", "--others", "--exclude-standard"
    ).splitlines()
    for name in tracked:
        p = Path(name)
        if p.name in {"CLAUDE.md", "AGENTS.md", "Makefile"} or name.startswith(
            (
                "docs/agents/",
                ".github/workflows/",
                ".claude/commands/",
                ".claude/hooks/",
            )
        ):
            names.add(name)
    return names


def inspect_wiring(plan: Plan) -> None:
    pending = list(active_files(plan.root))
    seen = set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        raw = plan.changes.get(name, plan.inspect(name))
        if raw is None:
            continue
        if RETIRED.search(raw):
            plan.conflicts.append(
                f"{name}: active retired wiring remains; review and disconnect only starter requirements"
            )
        if name.endswith(".md"):
            # Follow local Markdown links and Claude @imports within instruction scope.
            links = re.findall(rb"\]\(([^)#]+)(?:#[^)]*)?\)|(?:^|\s)@([^\s]+\.md)", raw)
            for pair in links:
                link = (pair[0] or pair[1]).decode()
                if "://" in link or link.startswith("#"):
                    continue
                path = (plan.root / name).parent / link
                normalized = Path(os.path.normpath(path))
                if normalized.is_relative_to(plan.root) and normalized.suffix == ".md":
                    relative = normalized.relative_to(plan.root).as_posix()
                    if relative in plan.changes and plan.changes[relative] is None:
                        plan.conflicts.append(
                            f"{name}: link to removed {relative}; reconcile instruction import"
                        )
                    elif normalized.exists():
                        pending.append(relative)


def add_payload(plan: Plan) -> None:
    prior_raw = plan.inspect(RECORD)
    prior: dict[str, Any] = (
        json.loads(prior_raw) if prior_raw else {"version": "4.0.0", "files": {}}
    )
    files = dict(prior["files"])
    for source in sorted((SOURCE / "payload").rglob("*")):
        if not source.is_file():
            continue
        name = source.relative_to(SOURCE / "payload").as_posix()
        before = plan.inspect(name)
        incoming = source.read_bytes()
        if name in files or before is not None:
            plan.notes.append(
                f"PRESERVE {name}: existing guidance; updates are explicit"
            )
            continue
        if name == "CODING_STANDARDS.md":
            alternatives = [
                "CONTRIBUTING.md",
                "docs/coding-standards.md",
                "docs/standards.md",
            ]
            existing = [p for p in alternatives if plan.inspect(p) is not None]
            if existing:
                plan.notes.append(
                    f"PRESERVE standards: reuse {existing[0]} (confirm equivalent coverage)"
                )
                continue
        plan.change(name, incoming, "missing essential workflow guidance")
        files[name] = incoming.decode()
    instruction = "CLAUDE.md" if plan.inspect("CLAUDE.md") is not None else "AGENTS.md"
    current = (
        plan.changes.get(instruction, plan.inspect(instruction))
        or b"# Project instructions\n"
    )
    if b"docs/agents/workflow.md" not in current:
        plan.change(
            instruction,
            current + b"\nRead docs/agents/workflow.md for development guidance.\n",
            "reference shared workflow without replacing team rules",
        )
    for name, text in {
        "docs/agents/issue-tracker.md": "# Issue tracker\n\nUse local Markdown under .scratch/<feature>/ by default. Run\n/setup-matt-pocock-skills to establish the existing tracker contract; preserve\nexisting tickets, formats and statuses. No remote issue publication is implied.\n",
        "docs/agents/domain.md": "# Domain documentation\n\nUse existing glossary and ADR locations. Run /setup-matt-pocock-skills\nto fill missing guidance; default to one GLOSSARY.md and docs/adr/.\nRead relevant context only. Unknown historical rationale remains unknown.\n",
        "docs/agents/checks.md": "# Native checks\n\nInspect the existing package scripts, Makefile and CI before running checks.\nRecord the agreed format/lint/type/test and application verification commands\nhere. No native check was selected automatically during installation.\n",
    }.items():
        if plan.inspect(name) is None:
            plan.change(
                name,
                text.encode(),
                "missing setup reference; confirm project-specific choices",
            )
            files[name] = text
    record = {
        "version": "4.0.0",
        "source": "https://github.com/ZekeT/agentic-starter",
        "files": files,
    }
    plan.change(
        RECORD,
        encoded(record),
        "installation-only template baselines; never checked during development",
    )


def plan_adoption(target: Path, minimal: bool) -> Plan:
    target = target.resolve()
    if (
        target == SOURCE.parent
        or target.is_relative_to(SOURCE.parent)
        or SOURCE.parent.is_relative_to(target)
    ):
        raise ValueError("Target must be outside the starter checkout")
    plan = Plan(target, git(target, "rev-parse", "HEAD"))
    for old_root in (".harness", ".factory"):
        if (target / old_root).exists():
            plan.conflicts.append(
                f"{old_root}: older layout requires a reviewed bounded transition; no automatic deletion"
            )
    version = plan.inspect(".engineering/TEMPLATE_VERSION")
    plan.notes.append(
        f"BASELINE {plan.baseline}; installed legacy version: {(version or b'unknown').decode().strip()}"
    )
    if minimal and plan.inspect(RECORD) is None:
        legacy_changes(plan)
    add_payload(plan)
    inspect_wiring(plan)
    # Disconnect callers before deleting their implementations.
    plan.changes = dict(sorted(plan.changes.items(), key=lambda item: item[1] is None))
    plan.notes.append(
        "PRESERVE application sources, dependencies, tests, specs, tickets, ADRs, installed Matt skills, Git remotes and security hooks"
    )
    plan.notes.append(
        "CHECK remote required CI checks manually; local adoption cannot edit branch protection"
    )
    return plan
