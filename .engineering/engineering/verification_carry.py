"""Conservative report reuse after an unrelated advancement of the merge base."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .config import safe_path
from .source import git
from .verification_checkout import validate_checkout
from .verification_facts import frozen_json, plain_json
from .verification_inputs import paths_from_git

DEPENDENCIES = ".engineering/state/dependencies.json"


def carried_reports(
    root: Path, previous: dict[str, Any], current: dict[str, Any]
) -> dict[str, Any]:
    """Carry reports only when Git shows the base advanced without scoped changes."""
    if not carry_candidate(previous, current):
        return {}
    old, new = previous["inputs"], current["inputs"]
    try:
        git(root, "merge-base", "--is-ancestor", old["base"], new["base"])
        validate_checkout(safe_path(root, previous.get("checkout", "")), old)
        upstream = paths_from_git(
            root,
            "diff",
            "--name-only",
            "--no-renames",
            "-z",
            old["base"],
            new["base"],
            "--",
        )
    except (ValueError, OSError):
        upstream = None
    return carried(previous, current, upstream)


def carry_candidate(previous: Mapping[str, Any], current: Mapping[str, Any]) -> bool:
    """Whether reports may carry: a new base, but the same plan, probes and requirements."""
    previous, current = frozen_json(previous), frozen_json(current)
    old, new = previous["inputs"], current["inputs"]
    if old["base"] == new["base"] or not previous["reports"]:
        return False
    if any(old[key] != new[key] for key in ("plan", "tools", "root", "runtime")):
        return False
    if old.get("starter_source") != new.get("starter_source"):
        return False
    return bool(previous["requirements"] == current["requirements"])


def carried(
    previous: Mapping[str, Any],
    current: Mapping[str, Any],
    upstream: set[str] | None,
) -> dict[str, Any]:
    """Carry only unchanged scoped patches onto a descendant base.

    Upstream holds the paths changed between the bases, None unless the old
    base is an ancestor of the new one. With identical baseline blobs and final
    bytes/modes on every scoped path, each path's own patch is identical,
    including additions and deletions.
    """
    previous, current = frozen_json(previous), frozen_json(current)
    old, new = previous["inputs"], current["inputs"]
    selected = set(new["plan"]["paths"]) | set(new["plan"]["inputs"]) | {DEPENDENCIES}
    if upstream is None or upstream & selected:
        return {}
    if any(old["files"].get(path) != new["files"].get(path) for path in selected):
        return {}
    reports: dict[str, Any] = plain_json(
        {
            role: {
                **report,
                "snapshot": current["snapshot"],
                "carried_from": previous["snapshot"],
            }
            for role, report in previous["reports"].items()
        }
    )
    return reports
