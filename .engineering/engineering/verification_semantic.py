"""Validate native review attestations without invoking or adapting native skills."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any  # JSON evidence is validated at the command boundary.

from .ownership import digest
from .verification_evidence import AXES
from .verification_git import baseline_content, read_objects


def validate_semantic(
    root: Path, report: dict[str, Any], inputs: dict[str, Any]
) -> None:
    """Require the ordinary reviewed commit to cover the entire proposed diff."""
    if report["role"] not in AXES:
        return
    commit, base = native_ids(report)
    for value in (commit, base):
        try:
            resolved = (
                read_objects(root, "rev-parse", "--verify", f"{value}^{{commit}}")
                .decode()
                .strip()
            )
        except subprocess.CalledProcessError as exc:
            raise ValueError(
                "Native review commit is unavailable; prepare again and obtain both native axes"
            ) from exc
        if resolved != value:
            raise ValueError(
                "Native review identities must name commit objects, not tags"
            )
    merge = read_objects(root, "merge-base", base, commit).decode().strip()
    if merge != inputs["base"]:
        raise ValueError(
            "Native review comparison differs from the prepared merge base"
        )
    committed = {
        name: {"sha256": digest(raw), "executable": mode == "100755"}
        for name, mode, raw in baseline_content(root, commit)
    }
    baseline = {name for name, _, _ in baseline_content(root, inputs["base"])}
    reject_uncovered(committed, baseline, inputs)


def native_ids(report: Mapping[str, Any]) -> tuple[str, str]:
    """The reviewed commit and comparison base, required as full object IDs."""
    commit, base = report["reviewed_commit"], report["comparison_base"]
    for value in (commit, base):
        if not isinstance(value, str) or not re.fullmatch(
            r"[0-9a-f]{40}|[0-9a-f]{64}", value
        ):
            raise ValueError(
                "Native review requires full reviewed_commit and comparison_base IDs"
            )
    return commit, base


def reject_uncovered(
    committed: Mapping[str, Any], baseline: set[str], inputs: Mapping[str, Any]
) -> None:
    """Require the checkpoint to hold every proposed addition, deletion and mode.

    Committed fingerprints the reviewed commit; baseline names the base's files.
    """
    names = baseline | set(committed) | set(inputs["plan"]["paths"])
    if any(committed.get(name) != inputs["files"].get(name) for name in names):
        raise ValueError(
            "Native review does not cover proposed content; make a scoped checkpoint "
            "including additions, deletions and modes, then obtain both native axes"
        )
