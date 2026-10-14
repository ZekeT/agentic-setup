"""Read regular Git blobs for isolated verification and pinned starter sources."""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Iterator, Mapping
from functools import lru_cache
from pathlib import Path

from .verification_inputs import STATE, source_path

# A full object ID always names the same bytes, so one operation reads it once;
# a reference such as HEAD can move and is read again every time.
OBJECT_ID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
# Regular baseline blobs by path: (mode, bytes).
Baseline = Mapping[str, tuple[str, bytes]]


def git_environment() -> dict[str, str]:
    """Keep Git bound to the selected repository and its original objects."""
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment.update(
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_NO_REPLACE_OBJECTS="1",
        GIT_TERMINAL_PROMPT="0",
        GIT_SSH_COMMAND="ssh -oBatchMode=yes -oStrictHostKeyChecking=yes",
        # Detached auto-maintenance outlives the command and races temp cleanup.
        GIT_CONFIG_COUNT="2",
        GIT_CONFIG_KEY_0="maintenance.auto",
        GIT_CONFIG_VALUE_0="false",
        GIT_CONFIG_KEY_1="gc.auto",
        GIT_CONFIG_VALUE_1="0",
    )
    return environment


def read_objects(root: Path, *args: str, batch: bytes | None = None) -> bytes:
    """Read object plumbing without inherited repository/configuration overrides."""
    return subprocess.run(
        ["git", "-C", str(root), *args],
        env=git_environment(),
        input=batch,
        capture_output=True,
        timeout=60,
        check=True,
    ).stdout


@lru_cache(maxsize=8)
def addressed_objects(root: Path, *args: str, batch: bytes | None = None) -> bytes:
    """Reuse a read named only by object IDs; failures are never reused."""
    return read_objects(root, *args, batch=batch)


def baseline_files(root: Path, base: str) -> dict[str, tuple[str, str]]:
    """Read regular baseline blobs; never check out links or run Git filters."""
    entries = {}
    read = addressed_objects if OBJECT_ID.fullmatch(base) else read_objects
    for entry in read(root, "ls-tree", "-r", "-z", base).split(b"\0"):
        if not entry:
            continue
        metadata, raw_name = entry.split(b"\t", 1)
        mode, kind, oid = metadata.decode().split()
        name = raw_name.decode(errors="surrogateescape")
        source_path(root, name)
        if mode not in ("100644", "100755") or kind != "blob":
            raise ValueError(f"Unsupported baseline verification input: {name}")
        if name == STATE or name.startswith(STATE + "/"):
            raise ValueError("Verification records must not be tracked")
        entries[name] = (mode, oid)
    return entries


def baseline_content(root: Path, base: str) -> Iterator[tuple[str, str, bytes]]:
    """Read validated blobs in one plumbing call, without filters or archive rules."""
    entries = baseline_files(root, base)
    raw_objects = addressed_objects(
        root,
        "cat-file",
        "--batch",
        batch="".join(oid + "\n" for _, oid in entries.values()).encode(),
    )
    offset = 0
    for name, (mode, _) in entries.items():
        end = raw_objects.index(b"\n", offset)
        size = int(raw_objects[offset:end].split()[-1])
        offset = end + 1
        yield name, mode, raw_objects[offset : offset + size]
        offset += size + 1


def baseline_blobs(root: Path, base: str) -> Baseline:
    """Validated baseline blobs by path, from the same batched reads."""
    return {name: (mode, raw) for name, mode, raw in baseline_content(root, base)}
