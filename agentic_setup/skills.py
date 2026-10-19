"""Selected skill bundles and read-only installation discovery."""

import json
import os
import re
from typing import Any

from .files import Plan, path_at
from .skill_files import alias_target

BUNDLES = {
    "matt": (
        "mattpocock/skills",
        "4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d",
        [
            "setup-matt-pocock-skills",
            "ask-matt",
            "grill-with-docs",
            "grilling",
            "grill-me",
            "domain-modeling",
            "codebase-design",
            "writing-for-agents",
            "to-spec",
            "to-tickets",
            "implement",
            "tdd",
            "code-review",
            "diagnosing-bugs",
            "research",
            "prototype",
            "wayfinder",
            "implement-spec",
            "pr",
            "retro",
        ],
    ),
    "show-me": (
        "humanlayer/skills",
        "3c2629142c5d437428269b1b722b08c0b87f574d",
        ["show-me"],
    ),
    "verification": (
        "backnotprop/pstack",
        "6f131f137de64fdaf928278c0fd9ecec520ccbee",
        ["create-verification-skill", "maintain-verification-skill"],
    ),
}


def skill_locations(plan: Plan) -> dict[str, list[str]]:
    """Validate each directory before probing for its skill declaration."""
    locations: dict[str, list[str]] = {}
    for folder in (
        ".claude/skills",
        ".agents/skills",
        ".cursor/skills",
        ".codex/skills",
        ".pi/skills",
    ):
        directory = path_at(plan.root, folder)
        if not directory.exists():
            continue
        for child in sorted(directory.iterdir()):
            relative = child.relative_to(plan.root).as_posix()
            if child.is_symlink():
                if os.readlink(child) != alias_target(relative):
                    raise ValueError(f"Symlink refused: {relative}")
                canonical = path_at(plan.root, f".agents/skills/{child.name}/SKILL.md")
                if not canonical.is_file():
                    raise ValueError(f"Dangling skill alias: {relative}")
                continue
            if not path_at(plan.root, relative).is_dir():
                continue
            skill = f"{relative}/SKILL.md"
            raw = plan.inspect(skill)
            if raw is None:
                continue
            match = re.search(rb'^name:\s*[\'"]?([a-zA-Z0-9-]+)', raw, re.M)
            name = match[1].decode().lower() if match else child.name.lower()
            locations.setdefault(name, []).append(skill)
    return locations


def external_records(plan: Plan) -> dict[str, Any]:
    raw = plan.inspect("skills-lock.json")
    if raw is None:
        return {}
    value = json.loads(raw)
    if (
        not isinstance(value, dict)
        or set(value) != {"version", "skills"}
        or type(value["version"]) is not int
        or value["version"] != 1
        or not isinstance(value["skills"], dict)
    ):
        raise ValueError("Unsupported skills-lock.json; expected version 1")
    for name, entry in value["skills"].items():
        if (
            not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name)
            or not isinstance(entry, dict)
            or not all(
                isinstance(entry.get(key), str)
                for key in ("source", "sourceType", "computedHash")
            )
            or not re.fullmatch(r"[0-9a-f]{64}", entry["computedHash"])
        ):
            raise ValueError(f"Invalid external skill record: {name}")
    return value["skills"]
