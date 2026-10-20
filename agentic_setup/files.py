"""Bounded file operations and reversible application of an inspected plan."""

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


def digest(raw: bytes | None) -> str:
    return hashlib.sha256(raw if raw is not None else b"<absent>").hexdigest()


def checked_root(root: Path) -> Path:
    absolute = root.absolute()
    # macOS exposes these system aliases; arbitrary user symlinks are refused.
    aliases = {Path("/tmp"): Path("/private/tmp"), Path("/var"): Path("/private/var")}
    for part in (absolute, *absolute.parents):
        if part.is_symlink() and aliases.get(part) != part.resolve():
            raise ValueError(f"Symlink refused: {part}")
    return absolute.resolve()


def baseline(root: Path) -> str:
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root.resolve():
        raise ValueError("Target must be the Git project root")
    return git(root, "rev-parse", "HEAD")


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
    inputs: dict[str, str] = field(default_factory=dict)
    resolved: set[str] = field(default_factory=set)
    recovery_root: Path | None = None

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
                    "inputs": self.inputs,
                    "resolved": sorted(self.resolved),
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
        deleted = git(
            self.root,
            "diff",
            "--name-only",
            "--diff-filter=D",
            "HEAD",
            "--",
            *self.observed,
        )
        if deleted:
            raise ValueError(f"Commit affected local edits before apply: {deleted}")
        # Existing changed content must be recoverable from this exact commit.
        for name in self.changes:
            tracked = bool(git(self.root, "ls-files", "--", name))
            explicit_local = name in self.resolved and self.recovery_root is not None
            if tracked or not explicit_local:
                if git(self.root, "status", "--porcelain", "--", name):
                    raise ValueError(
                        f"Commit affected local edits before apply: {name}"
                    )
            if self.observed[name] is not None and not tracked and not explicit_local:
                raise ValueError(
                    f"Untracked content requires an explicit resolution: {name}"
                )
        if self.recovery_root is not None:
            save_recovery(self)
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


def save_recovery(plan: Plan) -> None:
    """Save captured originals outside the target before a resolved plan can write."""
    assert plan.recovery_root is not None
    folder = checked_root(plan.recovery_root / plan.token())
    if folder == plan.root or folder.is_relative_to(plan.root):
        raise ValueError("Recovery folder must be outside the target workspace")
    if folder.exists():
        raise ValueError(
            "Recovery snapshot already exists; inspect it before retrying apply"
        )
    folder.mkdir(parents=True, mode=0o700)
    files = {}
    for name, after in plan.changes.items():
        before = plan.observed[name]
        mode = None
        if before is not None:
            mode = path_at(plan.root, name).stat().st_mode & 0o777
            saved = path_at(folder / "before", name)
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(before)
            os.chmod(saved, 0o600)
        files[name] = {
            "before_sha256": digest(before) if before is not None else None,
            "after_sha256": digest(after) if after is not None else None,
            "before_mode": mode,
        }
    (folder / "manifest.json").write_bytes(
        encoded(
            {
                "target": str(plan.root),
                "baseline": plan.baseline,
                "preview": plan.token(),
                "files": files,
            }
        )
    )
