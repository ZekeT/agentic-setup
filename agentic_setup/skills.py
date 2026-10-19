"""Plan explicit skill installs and conservative updates from a resolved source."""

import json
import re
from pathlib import Path
from typing import Any

from .adopt import metadata_directory
from .files import Plan, baseline, checked_root, digest, encoded, git, path_at, read

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


def installed_names(plan: Plan) -> set[str]:
    locations = skill_locations(plan)
    for name, paths in locations.items():
        if len(paths) > 1:
            plan.conflicts.append(
                f"{', '.join(paths)}: duplicate existing exposed name {name}"
            )
    return set(locations)


def upstream_skills(checkout: Path, selected: list[str]) -> dict[str, dict[str, bytes]]:
    files = git(checkout, "ls-files").splitlines()
    candidates: dict[str, Path] = {}
    for name in files:
        if not name.endswith("/SKILL.md"):
            continue
        raw = read(checkout, name)
        match = re.search(rb'^name:\s*[\'"]?([a-z0-9-]+)', raw or b"", re.M)
        if match and match[1].decode() in selected:
            exposed = match[1].decode()
            if exposed in candidates:
                raise ValueError(f"Duplicate upstream skill name: {exposed}")
            candidates[exposed] = Path(name).parent
    if set(candidates) != set(selected):
        raise ValueError(
            f"Missing upstream skills: {sorted(set(selected) - set(candidates))}; review the bundle selection"
        )
    result: dict[str, dict[str, bytes]] = {}
    for name, directory in candidates.items():
        result[name] = {}
        for relative in files:
            path = Path(relative)
            if path.is_relative_to(directory):
                raw = read(checkout, relative)
                if raw is None:
                    raise ValueError(f"Missing tracked upstream file: {relative}")
                destination = (
                    f".claude/skills/{name}/{path.relative_to(directory).as_posix()}"
                )
                result[name][destination] = raw
    return result


def skill_records(plan: Plan, path: str) -> dict[str, Any]:
    records = json.loads(plan.inspect(path) or b"{}")
    if not isinstance(records, dict):
        raise ValueError("Skill metadata must be an object")
    for name, record in records.items():
        if not isinstance(record, dict) or not all(
            isinstance(record.get(key), str) for key in ("source", "commit")
        ):
            raise ValueError(f"Invalid skill record: {name}")
    return records


def owned_files(record: dict[str, Any], name: str) -> dict[str, str] | None:
    files = record.get("files")
    if files is None:
        return None
    if (
        not isinstance(files, dict)
        or not files
        or not all(
            isinstance(path, str)
            and path.startswith(f".claude/skills/{name}/")
            and isinstance(value, str)
            and re.fullmatch(r"[0-9a-f]{64}", value)
            for path, value in files.items()
        )
        or f".claude/skills/{name}/SKILL.md" not in files
    ):
        raise ValueError(f"Invalid owned file hashes for skill {name}")
    return files


def plan_skills(
    target: Path, checkout: Path, bundle: str, *, update: bool = False
) -> Plan:
    source, _, selected = BUNDLES[bundle]
    target, checkout = checked_root(target), checked_root(checkout)
    if (
        target == checkout
        or target.is_relative_to(checkout)
        or checkout.is_relative_to(target)
    ):
        raise ValueError("Skill source must be outside the target workspace")
    revision = git(checkout, "rev-parse", "HEAD")
    if git(checkout, "status", "--porcelain"):
        raise ValueError(f"Use a clean {source} checkout")
    plan = Plan(target, baseline(target))
    plan.notes.append(f"SOURCE {source}@{revision}; replay with --ref {revision}")
    candidates = upstream_skills(checkout, selected)
    metadata = metadata_directory(plan)
    record_path = f"{metadata}/skills.json"
    records = skill_records(plan, record_path)
    existing = installed_names(plan)
    managed = False
    license_directory = f"{metadata}/licenses/{bundle}/{revision}"
    for name, incoming in candidates.items():
        prior = records.get(name)
        canonical = f".claude/skills/{name}/SKILL.md"
        exposed = (
            name in existing or plan.inspect(f".claude/commands/{name}.md") is not None
        )
        if update:
            if plan.inspect(f".claude/commands/{name}.md") is not None:
                plan.conflicts.append(
                    f"{name}: command name collision; reconcile before updating"
                )
                continue
            if prior is None:
                plan.notes.append(
                    f"PRESERVE skill {name}: no installation record; install separately"
                )
                continue
            if prior["source"] != source:
                plan.conflicts.append(
                    f"{name}: recorded source differs from selected bundle"
                )
                continue
            previous = owned_files(prior, name)
            if previous is None:
                plan.conflicts.append(
                    f"{name}: no file baseline; first preview skills install --bundle {bundle} --ref {prior['commit']} to verify the recorded revision (or use that clean --from checkout)"
                )
                continue
            if name not in existing or plan.inspect(canonical) is None:
                plan.conflicts.append(
                    f"{name}: recorded skill is missing or relocated; reconcile manually"
                )
                continue
            before_conflicts = len(plan.conflicts)
            for path, expected in previous.items():
                if digest(plan.inspect(path)) != expected:
                    plan.conflicts.append(
                        f"{path}: locally modified or deleted; preserve and reconcile manually"
                    )
            for path in incoming.keys() - previous.keys():
                if plan.inspect(path) is not None:
                    plan.conflicts.append(
                        f"{path}: incoming file overlaps unowned project content"
                    )
            if len(plan.conflicts) != before_conflicts:
                continue
            for path in sorted(previous.keys() | incoming.keys()):
                plan.change(
                    path,
                    incoming.get(path),
                    f"explicit skill update from {source}@{revision}",
                )
        elif exposed:
            # Commit-only records can gain ownership only after exact byte verification.
            if (
                prior is None
                or prior["source"] != source
                or prior["commit"] != revision
                or prior.get("files") is not None
            ):
                plan.notes.append(
                    f"PRESERVE skill {name}: already exposed; use an explicit update, never shadow it"
                )
                continue
            if any(plan.inspect(path) != raw for path, raw in incoming.items()):
                plan.conflicts.append(
                    f"{name}: installed files differ from recorded revision; cannot establish a file baseline"
                )
                continue
            plan.notes.append(
                f"BASELINE {name}: verified installed bytes at recorded revision"
            )
        else:
            if prior is not None:
                plan.conflicts.append(
                    f"{name}: recorded installation is missing; reconcile before reinstalling"
                )
                continue
            for path, raw in incoming.items():
                if plan.inspect(path) is not None:
                    plan.conflicts.append(
                        f"{path}: partial existing skill; inspect before installing"
                    )
                else:
                    plan.change(path, raw, f"unmodified {source}@{revision}")
        records[name] = {
            **(prior or {}),
            "source": source,
            "commit": revision,
            "files": {path: digest(raw) for path, raw in incoming.items()},
            "license_directory": license_directory,
        }
        managed = True
    if managed:
        tracked = set(git(checkout, "ls-files").splitlines())
        for name in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
            license_bytes = read(checkout, name) if name in tracked else None
            if license_bytes is not None:
                destination = f"{license_directory}/{name}"
                before = plan.inspect(destination)
                if before is not None and before != license_bytes:
                    plan.conflicts.append(f"{destination}: customized license file")
                else:
                    plan.change(
                        destination,
                        license_bytes,
                        "retain license for this upstream revision",
                    )
        plan.change(
            record_path,
            encoded(records),
            "record installed revisions and owned file hashes",
        )
    if git(checkout, "rev-parse", "HEAD") != revision or git(
        checkout, "status", "--porcelain"
    ):
        raise ValueError(
            "Skill source changed while planning; preview again from a clean checkout"
        )
    return plan
