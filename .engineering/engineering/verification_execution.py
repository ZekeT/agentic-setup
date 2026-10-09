"""Serialized evidence access and disposable check execution."""

from __future__ import annotations

import fcntl
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any  # JSON evidence is validated at the command boundary.

from .config import safe_path
from .ownership import encoded
from .transaction import write_files
from .verification_checkout import validate_checkout
from .verification_snapshot import run_command, snapshot


@contextmanager
def evidence_lock(root: Path, name: str) -> Iterator[None]:
    """Fail promptly on concurrent evidence access; OS releases interrupted locks."""
    lock = safe_path(root, name + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError(
                "Verification evidence is busy; serialize operations and retry"
            ) from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def execute_checks(root: Path, name: str, data: dict[str, Any]) -> None:
    """Run the declared suite on a disposable copy, retaining factual output."""
    inputs = data["inputs"]
    captured = safe_path(root, data["checkout"])
    folder = Path(tempfile.mkdtemp(prefix="checks-", dir=captured.parent))
    checkout = folder / "checkout"
    shutil.copytree(captured, checkout, symlinks=True)
    data["check_checkout"] = str(checkout.relative_to(root))
    data["checks"] = []
    carried = any("carried_from" in report for report in data["reports"].values())
    if not carried:
        data["reports"].pop("behavioral", None)
    write_files(root, {name: encoded(data)})
    for command in inputs["plan"]["checks"]:
        result = run_command(checkout, command, timeout=1800)
        try:
            validate_checkout(checkout, inputs)
            validate_checkout(captured, inputs)
            after, _ = snapshot(root, inputs["plan"])
            if after != data["snapshot"]:
                raise ValueError(
                    "STALE: checks mutated verification inputs; prepare and reverify"
                )
        except (ValueError, OSError):
            data["checks"] = []
            data["reports"].pop("behavioral", None)
            write_files(root, {name: encoded(data)})
            raise
        data["checks"].append(result)
        if result["exit_code"]:
            data["reports"].pop("behavioral", None)
        write_files(root, {name: encoded(data)})
