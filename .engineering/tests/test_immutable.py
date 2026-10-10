"""Shared immutable preparation fails loudly when a test writes to it."""

import pytest

from .immutable import unchanged


def edit(root):
    (root / "file.txt").write_text("changed\n")


def add(root):
    (root / "nested/new.txt").write_text("new\n")


def remove(root):
    (root / "nested/kept.txt").unlink()


def chmod(root):
    (root / "file.txt").chmod(0o755)


def relink(root):
    (root / "link").unlink()
    (root / "link").symlink_to("nested")


@pytest.mark.parametrize("mutate", [edit, add, remove, chmod, relink])
def test_writes_to_shared_preparation_fail(tmp_path, mutate):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested/kept.txt").write_text("kept\n")
    (tmp_path / "file.txt").write_text("original\n")
    (tmp_path / "file.txt").chmod(0o644)
    (tmp_path / "link").symlink_to("file.txt")
    with pytest.raises(AssertionError, match="shared preparation"):
        with unchanged(tmp_path) as root:
            mutate(root)
