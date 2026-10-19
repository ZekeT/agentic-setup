"""Validate explicit project decisions without writing to the target workspace."""

import json
import re
from pathlib import Path
from typing import Any

from .files import Plan, checked_root, digest, encoded, path_at, read


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def external_file(plan: Plan, path: Path) -> bytes:
    path = checked_root(path)
    path_at(Path(path.anchor), path.relative_to(path.anchor).as_posix())
    if path == plan.root or path.is_relative_to(plan.root):
        raise ValueError("Resolution inputs must be outside the target workspace")
    raw = read(path.parent, path.name)
    if raw is None:
        raise ValueError(f"Missing resolution input: {path}")
    plan.inputs[str(path)] = digest(raw)
    return raw


def resolve_content(
    plan: Plan, folder: Path, operation: dict[str, Any], proposed: bytes | None
) -> bytes | None:
    action = operation["action"]
    if action == "delete":
        return None
    if action == "replace_file":
        replacement = operation["replacement"]
        if not isinstance(replacement, str) or not replacement:
            raise ValueError("Replacement must be a relative file path")
        return external_file(plan, path_at(folder, replacement))
    if proposed is None:
        raise ValueError(f"{action} requires proposed file contents")
    text = proposed.decode("utf-8")
    if action == "replace_text":
        old, new = operation["old"], operation["new"]
        if not isinstance(old, str) or not old or not isinstance(new, str):
            raise ValueError(
                "replace_text requires nonempty old text and string new text"
            )
        if text.count(old) != 1:
            raise ValueError("replace_text must match exactly once in proposed content")
        return text.replace(old, new, 1).encode()
    pointer = operation["pointer"]
    if not isinstance(pointer, list) or not all(
        isinstance(key, str) for key in pointer
    ):
        raise ValueError("json_remove pointer must be a list of object keys")
    document = json.loads(text, object_pairs_hook=unique_object)
    array = document
    for key in pointer:
        if not isinstance(array, dict) or key not in array:
            raise ValueError("json_remove pointer does not identify an existing array")
        array = array[key]
    if not isinstance(array, list):
        raise ValueError("json_remove must identify an array")
    matches = [
        index
        for index, value in enumerate(array)
        if encoded(value) == encoded(operation["value"])
    ]
    if len(matches) != 1:
        raise ValueError("json_remove must match exactly one array entry")
    del array[matches[0]]
    return encoded(document)


def apply_resolutions(plan: Plan, path: Path, allowed: set[str]) -> None:
    path = checked_root(path)
    document = json.loads(external_file(plan, path), object_pairs_hook=unique_object)
    if not isinstance(document, dict) or set(document) != {
        "version",
        "target",
        "operations",
    }:
        raise ValueError(
            "Resolution plan requires exactly version, target and operations"
        )
    if type(document["version"]) is not int or document["version"] != 1:
        raise ValueError("Unsupported resolution plan version")
    if document["target"] != str(plan.root):
        raise ValueError("Resolution plan target does not match this workspace")
    if not isinstance(document["operations"], list) or not document["operations"]:
        raise ValueError("Resolution operations must be a nonempty list")
    fields = {
        "delete": set(),
        "replace_text": {"old", "new"},
        "json_remove": {"pointer", "value"},
        "replace_file": {"replacement"},
    }
    common = {"path", "action", "reason", "expected_sha256"}
    for operation in document["operations"]:
        if not isinstance(operation, dict):
            raise ValueError("Resolution operation must be an object")
        action = operation.get("action")
        if not isinstance(action, str) or action not in fields:
            raise ValueError("Unsupported resolution action")
        if set(operation) != common | fields[action]:
            raise ValueError(f"Invalid fields for resolution action {action}")
        name, reason = operation["path"], operation["reason"]
        if not isinstance(name, str) or not name or Path(name).as_posix() != name:
            raise ValueError("Resolution path must be a canonical relative file path")
        path_at(plan.root, name)
        if name in plan.resolved:
            raise ValueError(f"Duplicate resolution path: {name}")
        if name not in allowed or name.startswith((".agentic-setup/", ".starter/")):
            raise ValueError(
                f"Resolution path is outside inspected configuration: {name}"
            )
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Resolution requires a nonempty reason")
        expected = operation["expected_sha256"]
        if expected is not None and (
            not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected)
        ):
            raise ValueError(f"Invalid expected_sha256: {name}")
        before = plan.inspect(name)
        if expected != (digest(before) if before is not None else None):
            raise ValueError(
                f"Stale resolution for {name}; inspect current contents and preview again"
            )
        if action == "delete" and before is None:
            raise ValueError(f"Delete resolution requires an existing file: {name}")
        proposed = plan.changes.get(name, before)
        after = resolve_content(plan, path.parent, operation, proposed)
        plan.changes.pop(name, None)
        prefixes = tuple(
            f"{verb} {name}:" for verb in ("ADD", "UPDATE", "DELETE", "PRESERVE")
        )
        plan.notes = [note for note in plan.notes if not note.startswith(prefixes)]
        plan.conflicts = [
            conflict
            for conflict in plan.conflicts
            if not conflict.startswith(f"{name}: customized ")
        ]
        plan.resolved.add(name)
        plan.notes.append(f"RESOLVE {name}: {action}; {reason}")
        plan.change(name, after, f"explicit resolution: {reason}")
    plan.recovery_root = path.parent / "backups"
