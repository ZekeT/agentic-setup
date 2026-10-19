"""Copy selected unmodified skills from an explicitly fetched, pinned upstream checkout."""

import json
import re
from pathlib import Path

from .files import Plan, encoded, git, read

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


def plan_skills(target: Path, checkout: Path, bundle: str) -> Plan:
    source, revision, selected = BUNDLES[bundle]
    if git(checkout, "rev-parse", "HEAD") != revision or git(
        checkout, "status", "--porcelain"
    ):
        raise ValueError(f"Use a clean {source} checkout at {revision}")
    plan = Plan(target.resolve(), git(target, "rev-parse", "HEAD"))
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
        raise ValueError(f"Missing upstream skills: {set(selected) - set(candidates)}")
    record_path = ".starter/skills.json"
    record = json.loads(plan.inspect(record_path) or b"{}")
    for name, directory in candidates.items():
        destinations = [
            f".claude/skills/{name}/SKILL.md",
            f".agents/skills/{name}/SKILL.md",
            f".claude/commands/{name}.md",
        ]
        if any(plan.inspect(p) is not None for p in destinations):
            plan.notes.append(
                f"PRESERVE skill {name}: already exposed; upgrade separately, never shadow it"
            )
            continue
        for relative in files:
            p = Path(relative)
            if p.is_relative_to(directory):
                destination = (
                    f".claude/skills/{name}/{p.relative_to(directory).as_posix()}"
                )
                if plan.inspect(destination) is not None:
                    plan.conflicts.append(
                        f"{destination}: partial existing skill; inspect before installing"
                    )
                else:
                    plan.change(
                        destination,
                        read(checkout, relative),
                        f"unmodified {source}@{revision}",
                    )
        record[name] = {"source": source, "commit": revision}
    for license_name in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        if license_name in files:
            destination = f".starter/licenses/{bundle}/{license_name}"
            incoming = read(checkout, license_name)
            before = plan.inspect(destination)
            if before is not None and before != incoming:
                plan.conflicts.append(f"{destination}: customized license file")
            else:
                plan.change(destination, incoming, "retain upstream license")
    plan.change(
        record_path, encoded(record), "selected upstream pins; installation only"
    )
    return plan
