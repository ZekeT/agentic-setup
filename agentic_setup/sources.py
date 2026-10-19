"""Resolve explicitly requested upstream snapshots outside the target workspace."""

import re
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .files import checked_root, git


@contextmanager
def skill_source(
    source: str, checkout: Path | None, revision: str | None
) -> Iterator[Path]:
    if revision is not None and not re.fullmatch(
        r"[0-9a-f]{40}|[0-9a-f]{64}", revision
    ):
        raise ValueError("--ref must be a full commit hash from a preview")
    if checkout is not None:
        checkout = checked_root(checkout)
        if revision is not None and git(checkout, "rev-parse", "HEAD") != revision:
            raise ValueError("--from checkout HEAD does not match --ref")
        yield checkout
        return
    with tempfile.TemporaryDirectory(prefix="agentic-skills-") as temporary:
        parent = Path(temporary)
        checkout = parent / "upstream"
        git(
            parent,
            "clone",
            "--quiet",
            "--no-checkout",
            "--single-branch",
            "--",
            f"https://github.com/{source}.git",
            str(checkout),
        )
        if revision is not None:
            git(checkout, "fetch", "--quiet", "origin", revision)
        git(checkout, "checkout", "--quiet", "--detach", revision or "HEAD")
        yield checkout
