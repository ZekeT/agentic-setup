"""Read bounded setup documents and native command declarations without executing them."""

import json
import re

from .files import Plan, git


def standards(plan: Plan) -> list[str]:
    candidates = {
        "CODING_STANDARDS.md",
        "CONTRIBUTING.md",
        "docs/coding-standards.md",
        "docs/standards.md",
    }
    if plan.baseline:
        for name in git(
            plan.root, "ls-files", "--cached", "--others", "--exclude-standard"
        ).splitlines():
            if (
                name.endswith(".md")
                and (name.startswith("docs/") or "/" not in name)
                and re.search(r"standard|contribut|style|guideline", name, re.I)
            ):
                candidates.add(name)
    result = []
    for name in sorted(candidates):
        raw = plan.changes.get(name, plan.inspect(name))
        if raw and re.search(
            rb"(?im)^#{1,3}\s+(?:coding|code|development|engineering|project)?\s*(?:standards|guidelines|conventions|style)\b",
            raw,
        ):
            result.append(name)
    return result


def native_commands(plan: Plan) -> str:
    commands = []
    package = plan.inspect("package.json")
    if package:
        config = json.loads(package)
        if not isinstance(config, dict) or not isinstance(
            config.get("scripts", {}), dict
        ):
            raise ValueError(
                "Invalid package.json: expected an object with a scripts object"
            )
        scripts = config.get("scripts", {})
        manager = "npm"
        for lock, candidate in [
            ("pnpm-lock.yaml", "pnpm"),
            ("yarn.lock", "yarn"),
            ("bun.lock", "bun"),
        ]:
            if plan.inspect(lock) is not None:
                manager = candidate
                break
        for name in ("check", "lint", "typecheck", "test", "build"):
            if name in scripts:
                commands.append(f"- `{manager} run {name}` (package.json script)")
    make = plan.changes.get("Makefile", plan.inspect("Makefile"))
    if make:
        for name in ("check", "lint", "test", "typecheck"):
            if re.search(rb"(?m)^" + name.encode() + rb"\s*:", make):
                commands.append(f"- `make {name}` (Makefile target)")
    if plan.inspect("Cargo.toml"):
        commands.append(
            "- `cargo test` (Cargo project; inspect workspace/features first)"
        )
    if plan.inspect("go.mod"):
        commands.append("- `go test ./...` (Go module)")
    return (
        "# Native checks\n\nDiscovered candidates; not executed during preview. Inspect their definitions and\nchoose the relevant checks before running them. Record actual results and gaps.\n\n"
        + "\n".join(commands)
        + "\n\nUse an agreed command with adoption --check to compare baseline and after.\n"
        if commands
        else "# Native checks\n\nNo native command was identified in package scripts, Makefile, Cargo or Go config.\nInspect existing CI and tool configuration, agree commands, and record them here.\nNative verification remains unverified until exercised.\n"
    )
