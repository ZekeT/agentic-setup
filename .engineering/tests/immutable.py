"""Detect writes to preparation that tests share as immutable input."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def tree(root: Path) -> dict[str, tuple[str, bytes, int]]:
    """Every entry's kind, bytes or link target, and mode."""
    entries = {}
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries[name] = ("link", str(path.readlink()).encode(), 0)
        elif path.is_dir():
            entries[name] = ("dir", b"", path.stat().st_mode & 0o777)
        else:
            entries[name] = ("file", path.read_bytes(), path.stat().st_mode & 0o777)
    return entries


@contextmanager
def unchanged(root: Path) -> Iterator[Path]:
    """Yield shared preparation; fail teardown if any test wrote to it."""
    before = tree(root)
    yield root
    assert tree(root) == before, f"A test wrote to shared preparation: {root}"
