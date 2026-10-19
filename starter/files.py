"""Bounded file operations and reversible application of an inspected plan."""

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


def digest(raw: bytes | None) -> str:
    return hashlib.sha256(raw if raw is not None else b"<absent>").hexdigest()


def path_at(root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError(f"Unsafe path: {name}")
    if any(p == ".git" or p == ".env" or p.startswith(".env.") for p in relative.parts):
        raise ValueError(f"Protected path: {name}")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Symlink refused: {name}")
    return current


def read(root: Path, name: str) -> bytes | None:
    path = path_at(root, name)
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(f"Expected regular file: {name}")
    return path.read_bytes()


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True
    )
    if result.returncode:
        raise ValueError(result.stderr.strip())
    return result.stdout.strip()


def encoded(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()


@dataclass
class Plan:
    root: Path
    baseline: str
    observed: dict[str, bytes | None] = field(default_factory=dict)
    changes: dict[str, bytes | None] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)

    def inspect(self, name: str) -> bytes | None:
        if name not in self.observed:
            self.observed[name] = read(self.root, name)
        return self.observed[name]

    def change(self, name: str, content: bytes | None, reason: str) -> None:
        before = self.inspect(name)
        if before != content:
            self.changes[name] = content
            action = (
                "DELETE" if content is None else "ADD" if before is None else "UPDATE"
            )
            self.notes.append(f"{action} {name}: {reason}")

    def token(self) -> str:
        return digest(
            encoded(
                {
                    "root": str(self.root),
                    "baseline": self.baseline,
                    "before": {n: digest(b) for n, b in self.observed.items()},
                    "after": {n: digest(b) for n, b in self.changes.items()},
                    "conflicts": self.conflicts,
                }
            )
        )

    def apply(self, expected: str) -> None:
        if self.conflicts:
            raise ValueError("Resolve listed conflicts before applying")
        if expected != self.token():
            raise ValueError(
                "Stale preview: inspect a new preview and use its --expect value"
            )
        if git(self.root, "rev-parse", "HEAD") != self.baseline:
            raise ValueError("Git baseline changed; preview again")
        for name, before in self.observed.items():
            if read(self.root, name) != before:
                raise ValueError(f"Stale content: {name}")
        # Existing changed content must be recoverable from this exact commit.
        for name in self.changes:
            if self.observed[name] is not None:
                if git(self.root, "status", "--porcelain", "--", name):
                    raise ValueError(
                        f"Commit affected local edits before apply: {name}"
                    )
                if not git(self.root, "ls-files", "--", name):
                    raise ValueError(
                        f"Untracked content must be preserved manually: {name}"
                    )
        write_files(self.root, self.changes)


def write_files(root: Path, changes: dict[str, bytes | None]) -> None:
    """Rollback bytes and modes on ordinary write failures; leave unrelated files alone."""
    originals = {n: read(root, n) for n in changes}
    modes = {
        n: path_at(root, n).stat().st_mode & 0o777
        for n, b in originals.items()
        if b is not None
    }
    touched: list[str] = []
    created: list[Path] = []
    try:
        for name, raw in changes.items():
            path = path_at(root, name)
            parent = path.parent
            missing = []
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir()
                created.append(directory)
            touched.append(name)
            if raw is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(raw)
    except (OSError, ValueError):
        for name in reversed(touched):
            path = path_at(root, name)
            if originals[name] is None:
                path.unlink(missing_ok=True)
            else:
                original = originals[name]
                assert original is not None
                path.write_bytes(original)
                os.chmod(path, modes[name])
        for directory in reversed(created):
            directory.rmdir()
        raise
