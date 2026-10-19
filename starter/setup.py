"""Configuration-only initialization and conservative selective template updates."""

import json
import shutil
from pathlib import Path

from .adopt import RECORD, SOURCE, add_payload
from .files import Plan, baseline, checked_root, encoded, git, write_files

SCOPES = {
    "explanation": "docs/agents/explanation.md",
    "git": "docs/agents/git-workflow.md",
    "workflow": "docs/agents/workflow.md",
    "standards": "CODING_STANDARDS.md",
}


def initialize(target: Path, python_seed: bool) -> None:
    target = checked_root(target)
    if target.exists() or target.is_symlink():
        raise ValueError("Initialization requires a new destination")
    if not target.parent.is_dir():
        raise ValueError("Destination parent must exist")
    target.mkdir()
    try:
        plan = Plan(target.resolve(), "")
        add_payload(plan)
        if python_seed:
            plan.change(
                "pyproject.toml",
                b'[project]\nname = "my-app"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n',
                "explicit Python seed",
            )
            plan.change(
                "src/app.py",
                b'def greet(name: str) -> str:\n    return f"Hello, {name}!"\n',
                "explicit Python seed",
            )
        write_files(target, plan.changes)
    except (ValueError, OSError):
        # This directory was exclusively created by this invocation.
        shutil.rmtree(target)
        raise


def plan_update(target: Path, scope: str, source_ref: str) -> Plan:
    if git(SOURCE.parent, "rev-parse", "HEAD") != source_ref:
        raise ValueError(
            "--source-ref must be the full commit of this starter checkout"
        )
    name = SCOPES[scope]
    if git(SOURCE.parent, "status", "--porcelain", "--", "starter"):
        raise ValueError("Use a committed starter checkout for versioned updates")
    plan = Plan(checked_root(target), baseline(target))
    raw = plan.inspect(RECORD)
    if raw is None:
        raise ValueError("Adopt this project before selective updates")
    record = json.loads(raw)
    prior = record["files"].get(name)
    if prior is None:
        raise ValueError(
            f"{name}: not installed by this starter; preserve existing project guidance"
        )
    local = plan.inspect(name)
    incoming = (SOURCE / "payload" / name).read_bytes()
    template_baseline = prior.encode()
    if incoming == template_baseline:
        return plan
    if local == incoming:
        pass
    elif local == template_baseline:
        plan.change(name, incoming, f"explicit {scope} update from {source_ref}")
    elif local is not None and local.count(template_baseline) == 1:
        plan.change(
            name,
            local.replace(template_baseline, incoming, 1),
            "update intact template, preserve surrounding project additions",
        )
    else:
        plan.conflicts.append(
            f"{name}: template and project both changed; manually merge the displayed upstream version"
        )
        return plan
    record["files"][name] = incoming.decode()
    record["source_commit"] = source_ref
    plan.change(RECORD, encoded(record), "record only selected template update")
    return plan
