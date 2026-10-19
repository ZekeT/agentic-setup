"""File failure recovery through the installation transaction boundary."""

from pathlib import Path

import pytest

from starter.files import write_files


def test_write_failure_restores_bytes_modes_and_new_directories(tmp_path, monkeypatch):
    original = tmp_path / "original.txt"
    original.write_bytes(b"keep this")
    original.chmod(0o640)
    original_write = Path.write_bytes

    def disk_full(path, data):
        if path.name == "fail.txt":
            raise OSError("disk full")
        return original_write(path, data)

    monkeypatch.setattr(Path, "write_bytes", disk_full)
    with pytest.raises(OSError, match="disk full"):
        write_files(
            tmp_path,
            {"original.txt": b"changed", "new/ok.txt": b"new", "new/fail.txt": b"fail"},
        )
    assert original.read_bytes() == b"keep this"
    assert original.stat().st_mode & 0o777 == 0o640
    assert not (tmp_path / "new").exists()
