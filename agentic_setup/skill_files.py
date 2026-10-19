"""Bounded skill snapshots, including only canonical Claude aliases."""

import base64
import os
import stat
from pathlib import Path
from typing import Any

from .files import path_at

Snapshot = dict[str, dict[str, Any]]
MAX_BYTES = 32 * 1024 * 1024


def entry_path(root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.as_posix() != name or not name or relative.is_absolute():
        raise ValueError(f"Noncanonical skill path: {name}")
    # Validate all components but allow inspection of a supported leaf alias.
    path_at(Path("/"), name)
    return (
        path_at(root, relative.parent.as_posix()) / relative.name
        if len(relative.parts) > 1
        else root / relative.name
    )


def alias_target(name: str) -> str:
    parts = Path(name).parts
    if len(parts) != 3 or parts[:2] != (".claude", "skills"):
        raise ValueError(f"Unsupported skill symlink: {name}")
    return f"../../.agents/skills/{parts[2]}"


def capture(root: Path, roots: list[str]) -> Snapshot:
    result: Snapshot = {}
    pending = list(reversed(sorted(roots)))
    total = 0
    while pending:
        name = pending.pop()
        path = entry_path(root, name)
        if path.is_symlink():
            target = os.readlink(path)
            if target != alias_target(name):
                raise ValueError(f"Unsupported skill symlink: {name}")
            result[name] = {"kind": "link", "target": target}
        elif not path.exists():
            result[name] = {"kind": "absent"}
        else:
            info = path.stat()
            mode = stat.S_IMODE(info.st_mode)
            if mode > 0o777:
                raise ValueError(f"Special permission bits refused: {name}")
            if stat.S_ISDIR(info.st_mode):
                result[name] = {"kind": "directory", "mode": mode}
                pending.extend(
                    f"{name}/{p.name}" for p in sorted(path.iterdir(), reverse=True)
                )
            elif stat.S_ISREG(info.st_mode):
                total += info.st_size
                if total > MAX_BYTES:
                    raise ValueError("Skill snapshot exceeds 32 MiB")
                result[name] = {
                    "kind": "file",
                    "mode": mode,
                    "data": base64.b64encode(path.read_bytes()).decode(),
                }
            else:
                raise ValueError(f"Special skill file refused: {name}")
        if len(result) > 5000:
            raise ValueError("Skill snapshot exceeds 5000 entries")
    return result


def contents(node: dict[str, Any] | None) -> bytes | None:
    if not node or node["kind"] in {"absent", "directory"}:
        return None
    if node["kind"] == "link":
        return f"Symlink -> {node['target']}\n".encode()
    return base64.b64decode(node["data"], validate=True)


def validate(snapshot: Any, roots: list[str]) -> Snapshot:
    if (
        not isinstance(snapshot, dict)
        or not set(roots) <= snapshot.keys()
        or len(snapshot) > 5000
    ):
        raise ValueError("Invalid skill snapshot roots")
    total = 0
    for name, node in snapshot.items():
        if not isinstance(name, str) or not isinstance(node, dict):
            raise ValueError("Invalid skill snapshot entry")
        entry_path(Path("/"), name)
        if not any(name == root or name.startswith(root + "/") for root in roots):
            raise ValueError(f"Skill path outside approved scope: {name}")
        if (
            name not in roots
            and snapshot.get(str(Path(name).parent), {}).get("kind") != "directory"
        ):
            raise ValueError(f"Invalid snapshot parent: {name}")
        kind = node.get("kind")
        if not isinstance(kind, str):
            raise ValueError(f"Invalid snapshot kind: {name}")
        if kind == "absent":
            valid = set(node) == {"kind"} and name in roots
        elif kind == "link":
            valid = set(node) == {"kind", "target"} and node["target"] == alias_target(
                name
            )
        elif kind in {"file", "directory"}:
            fields = {"kind", "mode", "data"} if kind == "file" else {"kind", "mode"}
            valid = (
                set(node) == fields
                and type(node.get("mode")) is int
                and 0 <= node["mode"] <= 0o777
            )
            if kind == "file":
                if not isinstance(node.get("data"), str):
                    raise ValueError(f"Invalid file content: {name}")
                total += len(contents(node) or b"")
        else:
            valid = False
        if not valid or total > MAX_BYTES:
            raise ValueError(f"Invalid skill snapshot: {name}")
    return snapshot


def materialize(root: Path, snapshot: Snapshot) -> None:
    directories = []
    for name, node in sorted(
        snapshot.items(), key=lambda item: (len(Path(item[0]).parts), item[0])
    ):
        path = entry_path(root, name)
        kind = node["kind"]
        if kind == "absent":
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if kind == "directory":
            path.mkdir(exist_ok=True)
            directories.append((path, node["mode"]))
        elif kind == "file":
            path.write_bytes(contents(node) or b"")
            path.chmod(node["mode"])
        else:
            path.symlink_to(node["target"])
    for path, mode in reversed(directories):
        path.chmod(mode)
