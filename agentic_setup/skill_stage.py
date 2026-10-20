"""Run the external installer in staging; replay approved snapshots offline."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .files import Plan, baseline, checked_root, digest, encoded, git, path_at
from .preview import next_report, report_destination, write_preview
from .resolutions import unique_object
from .skill_files import capture, contents, entry_path, materialize, validate
from .skills import BUNDLES, external_records, skill_locations

SOURCE = Path(__file__).resolve().parents[1]
INSTALLER = "skills@1.7.2"
LEGACY_RECORDS = [".agentic-setup/skills.json", ".starter/skills.json"]


def scope(names: list[str]) -> list[str]:
    return sorted(
        [
            "skills-lock.json",
            *LEGACY_RECORDS,
            *[
                f"{folder}/{name}"
                for name in names
                for folder in (".agents/skills", ".claude/skills")
            ],
        ]
    )


def guards(names: list[str]) -> list[str]:
    return [f".claude/commands/{name}.md" for name in names]


def target_root(target: Path) -> Path:
    root = checked_root(target)
    if root == SOURCE or root.is_relative_to(SOURCE) or SOURCE.is_relative_to(root):
        raise ValueError("Target must be outside Agentic Setup")
    baseline(root)
    return root


def selection(root: Path, bundles: list[str], update: bool) -> dict[str, list[str]]:
    plan = Plan(root, "")
    locations = skill_locations(plan)
    records = external_records(plan)
    chosen = {}
    for bundle in bundles:
        names = BUNDLES[bundle][2]
        selected = [
            name for name in names if not update or name in locations or name in records
        ]
        for name in selected:
            paths = locations.get(name, [])
            canonical = {
                f".agents/skills/{name}/SKILL.md",
                f".claude/skills/{name}/SKILL.md",
            }
            if len(paths) > 1 or any(path not in canonical for path in paths):
                raise ValueError(
                    f"{name}: duplicate or renamed exposure; reconcile before staging"
                )
            if update and not paths:
                raise ValueError(
                    f"{name}: recorded but missing; preview install to restore it"
                )
            if plan.inspect(f".claude/commands/{name}.md") is not None:
                raise ValueError(
                    f"{name}: command name collision; reconcile before staging"
                )
        if selected:
            chosen[bundle] = selected
    return chosen


def installer(workspace: Path, state: Path, source: str, names: list[str]) -> None:
    environment = dict(os.environ, DISABLE_TELEMETRY="1", XDG_STATE_HOME=str(state))
    command = [
        "npx",
        "--yes",
        f"--package={INSTALLER}",
        "skills",
        "add",
        source,
        "--skill",
        *names,
        "--agent",
        "claude-code",
        "codex",
        "--yes",
        "--json",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=workspace,
            env=environment,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError(
            "Skill installer timed out in staging; target unchanged"
        ) from exc
    if result.returncode:
        raise ValueError(
            f"Skill installer failed in staging (exit {result.returncode}): {result.stderr[-4000:]} {result.stdout[-2000:]}"
        )
    try:
        output = json.loads(result.stdout)
    except ValueError as exc:
        raise ValueError(
            "Installer did not return valid JSON; target unchanged"
        ) from exc
    if not isinstance(output, list) or {
        item.get("name")
        for item in output
        if isinstance(item, dict) and item.get("status") == "installed"
    } != set(names):
        raise ValueError("Installer did not install exactly the selected skills")


def build_stage(
    target: Path,
    bundles: list[str],
    update: bool,
    checkout: Path | None,
    revision: str | None,
) -> dict[str, Any]:
    root = target_root(target)
    chosen = selection(root, bundles, update)
    names = sorted(name for selected in chosen.values() for name in selected)
    if not names:
        raise ValueError(
            "No installed supported skills selected; use skills install first"
        )
    if checkout is not None and len(chosen) != 1:
        raise ValueError("--from requires exactly one selected bundle")
    if revision is not None and not re.fullmatch(
        r"[0-9a-f]{40}|[0-9a-f]{64}", revision
    ):
        raise ValueError("--ref must be a full commit hash")
    local = checked_root(checkout) if checkout is not None else None
    if local is not None:
        if local == root or local.is_relative_to(root) or root.is_relative_to(local):
            raise ValueError("Skill source must be outside the target")
        for source_directory, subdirectories, files in os.walk(
            local, followlinks=False
        ):
            for name in subdirectories + files:
                if (Path(source_directory) / name).is_symlink():
                    raise ValueError(
                        "Symlink in local skill source; refuse installer scan"
                    )
            subdirectories[:] = [name for name in subdirectories if name != ".git"]
            for name in subdirectories + files:
                if name == ".env" or name.startswith(".env."):
                    raise ValueError(
                        "Protected file in local skill source; refuse installer scan"
                    )
        if git(local, "status", "--porcelain"):
            raise ValueError("Use a clean local skill source")
        if revision is not None and git(local, "rev-parse", "HEAD") != revision:
            raise ValueError("--from HEAD does not match --ref")
    roots = scope(names)
    before = capture(root, roots)
    observed = capture(root, guards(names))
    commit = baseline(root)
    previous_lock = external_records(Plan(root, ""))
    sources = {}
    with tempfile.TemporaryDirectory(prefix="agentic-skill-stage-") as temporary:
        directory = checked_root(Path(temporary))
        workspace = directory / "workspace"
        workspace.mkdir()
        materialize(workspace, before)
        for bundle, selected in chosen.items():
            source = str(local) if local else BUNDLES[bundle][0]
            if local is None and revision is not None:
                source = f"https://github.com/{source}/tree/{revision}"
            sources[bundle] = source
            installer(workspace, directory / "state", source, selected)
        incoming = external_records(Plan(workspace, ""))
        exposed = skill_locations(Plan(workspace, ""))
        for name in names:
            if exposed.get(name) != [f".agents/skills/{name}/SKILL.md"]:
                raise ValueError(f"Unexpected staged skill exposure: {name}")
        if set(incoming) != set(previous_lock) | set(names):
            raise ValueError("Installer changed unrelated skill records")
        for name, entry in previous_lock.items():
            if name not in names and incoming.get(name) != entry:
                raise ValueError(f"Installer changed unrelated record: {name}")
        for bundle, selected in chosen.items():
            for name in selected:
                entry = incoming[name]
                if local is None and (
                    entry["source"] != BUNDLES[bundle][0]
                    or entry["sourceType"] != "github"
                ):
                    raise ValueError(f"Unexpected installed source for {name}")
                if local is not None:
                    # npm writes local paths relative to its working directory.
                    # Relocate that record to its eventual project location.
                    entry["source"] = os.path.relpath(local, root).replace(os.sep, "/")
                if not (workspace / f".agents/skills/{name}/SKILL.md").is_file():
                    raise ValueError(f"Missing staged skill: {name}")
        (workspace / "skills-lock.json").write_bytes(
            encoded({"version": 1, "skills": incoming})
        )
        for name in LEGACY_RECORDS:
            raw = contents(before[name])
            if raw is None:
                continue
            records = json.loads(raw, object_pairs_hook=unique_object)
            if not isinstance(records, dict):
                raise ValueError(f"Invalid legacy records: {name}")
            remaining = {
                key: value for key, value in records.items() if key not in names
            }
            if remaining == records:
                continue
            path = path_at(workspace, name)
            if remaining:
                path.write_bytes(encoded(remaining))
            else:
                path.unlink()
        after = capture(workspace, roots)
        # Reject additional installer writes inside the staging workspace.
        actual = capture(workspace, [p.name for p in workspace.iterdir()])
        for name in actual:
            if not any(
                name == item
                or name.startswith(item + "/")
                or item.startswith(name + "/")
                for item in roots
            ):
                raise ValueError(f"Unexpected installer output: {name}")
    if (
        capture(root, roots) != before
        or capture(root, guards(names)) != observed
        or baseline(root) != commit
    ):
        raise ValueError("Target changed during staging; preview again")
    return {
        "version": 1,
        "installer": INSTALLER,
        "target": str(root),
        "baseline": commit,
        "operation": "update" if update else "install",
        "bundles": list(chosen),
        "names": names,
        "sources": sources,
        "before": before,
        "after": after,
        "guards": observed,
    }


def display(document: dict[str, Any]) -> Plan:
    plan = Plan(Path(document["target"]), document["baseline"])
    before, after = dict(document["before"]), document["after"]
    origins = {}
    for skill in document["names"]:
        old_root, new_root = f".claude/skills/{skill}", f".agents/skills/{skill}"
        if (
            before[old_root]["kind"] == "directory"
            and before[new_root]["kind"] == "absent"
        ):
            plan.notes.append(
                f"LAYOUT {old_root}/ moves to {new_root}/; Claude receives a relative alias. File comparisons below pair old and new locations."
            )
            for old in list(before):
                if old.startswith(old_root + "/"):
                    new = new_root + old[len(old_root) :]
                    before[new] = before.pop(old)
                    origins[new] = old
    for name in sorted(before.keys() | after.keys()):
        left, right = contents(before.get(name)), contents(after.get(name))
        plan.observed[name] = left
        if left != right:
            reason = (
                f"Before content from {origins[name]}; after content at {name}"
                if name in origins
                else "reviewed external installer output"
            )
            plan.change(name, right, reason)
        elif before.get(name) != after.get(name):
            plan.notes.append(
                f"MODE/TYPE {name}: {before.get(name, {}).get('kind')} -> {after.get(name, {}).get('kind')}; modes {before.get(name, {}).get('mode')} -> {after.get(name, {}).get('mode')}"
            )
    plan.notes.extend(
        [
            f"INSTALLER {document['installer']}; upstream sources: {document['sources']}",
            "Existing skill customizations and extra files may be replaced/deleted as shown. Approve the entire diff; no history or automatic merge is inferred.",
            "Canonical .agents/skills copies and matching relative Claude aliases form one installation. skills-lock.json is the skill record.",
            "Apply uses only this saved plan, offline, after checking the target. Originals are archived beside the plan. Stop target writers before applying.",
            "No target commands, application checks or skill bodies were executed.",
        ]
    )
    return plan


def read_stage(path: Path, target: Path) -> dict[str, Any]:
    path = checked_root(path)
    root = target_root(target)
    if path == root or path.is_relative_to(root):
        raise ValueError("Skill plan must be outside the target")
    path_at(Path(path.anchor), path.relative_to(path.anchor).as_posix())
    if path.stat().st_size > 100 * 1024 * 1024:
        raise ValueError("Skill plan is too large")
    doc = json.loads(path.read_bytes(), object_pairs_hook=unique_object)
    fields = {
        "version",
        "installer",
        "target",
        "baseline",
        "operation",
        "bundles",
        "names",
        "sources",
        "before",
        "after",
        "guards",
    }
    if (
        not isinstance(doc, dict)
        or set(doc) != fields
        or type(doc["version"]) is not int
        or doc["version"] != 1
        or doc["installer"] != INSTALLER
        or doc["target"] != str(root)
    ):
        raise ValueError("Invalid or mismatched skill plan")
    bundles, names = doc["bundles"], doc["names"]
    if (
        not isinstance(bundles, list)
        or not bundles
        or any(not isinstance(b, str) or b not in BUNDLES for b in bundles)
    ):
        raise ValueError("Invalid staged bundles")
    allowed = {n for b in bundles for n in BUNDLES[b][2]}
    if (
        not isinstance(names, list)
        or not names
        or any(not isinstance(n, str) or n not in allowed for n in names)
        or names != sorted(set(names))
    ):
        raise ValueError("Invalid staged skill names")
    if (
        doc["operation"] not in ("install", "update")
        or not isinstance(doc["baseline"], str)
        or not isinstance(doc["sources"], dict)
    ):
        raise ValueError("Invalid staged operation")
    roots = scope(names)
    validate(doc["before"], roots)
    validate(doc["after"], roots)
    validate(doc["guards"], guards(names))
    for name, node in doc["guards"].items():
        if node != {"kind": "absent"}:
            raise ValueError(f"Staged command collision: {name}")
    return doc


def apply_stage(document: dict[str, Any], path: Path, expected: str) -> Path:
    token = digest(encoded(document))
    if expected != token:
        raise ValueError("Stale or modified skill plan; preview again")
    root = Path(document["target"])
    names = document["names"]
    roots = scope(names)
    if (
        baseline(root) != document["baseline"]
        or capture(root, roots) != document["before"]
        or capture(root, guards(names)) != document["guards"]
    ):
        raise ValueError("Target changed since skill preview; preview again")
    selection(root, document["bundles"], document["operation"] == "update")
    folder = checked_root(path.parent / "backups" / token)
    if folder.is_relative_to(root) or root.is_relative_to(folder):
        raise ValueError("Recovery must be outside the target")
    if path.parent.stat().st_dev != root.stat().st_dev:
        raise ValueError("Skill recovery must be on the same filesystem as the target")
    folder.mkdir(parents=True, mode=0o700)
    prepared = folder / "proposed"
    prepared.mkdir()
    materialize(prepared, document["after"])
    (folder / "manifest.json").write_bytes(encoded(document))
    if (
        capture(root, roots) != document["before"]
        or baseline(root) != document["baseline"]
    ):
        raise ValueError(f"Target changed during preparation; inspect {folder}")
    changed = [
        name
        for name in roots
        if {
            n: v
            for n, v in document["before"].items()
            if n == name or n.startswith(name + "/")
        }
        != {
            n: v
            for n, v in document["after"].items()
            if n == name or n.startswith(name + "/")
        }
    ]
    moved = []
    installed = []
    created = []
    try:
        for name in changed:
            destination = entry_path(root, name)
            if document["before"][name]["kind"] != "absent":
                backup = folder / "before" / name
                backup.parent.mkdir(parents=True, exist_ok=True)
                destination.rename(backup)
                moved.append(name)
            if document["after"][name]["kind"] != "absent":
                missing = []
                parent = destination.parent
                while not parent.exists():
                    missing.append(parent)
                    parent = parent.parent
                for parent in reversed(missing):
                    parent.mkdir()
                    created.append(parent)
                entry_path(prepared, name).rename(destination)
                installed.append(name)
    except (OSError, ValueError) as exc:
        failures = []
        for name in reversed(installed):
            try:
                entry_path(root, name).rename(entry_path(prepared, name))
            except (OSError, ValueError) as error:
                failures.append(str(error))
        for name in reversed(moved):
            try:
                destination = entry_path(root, name)
                if destination.exists() or destination.is_symlink():
                    raise ValueError(f"Rollback destination occupied: {name}")
                (folder / "before" / name).rename(destination)
            except (OSError, ValueError) as error:
                failures.append(str(error))
        for parent in reversed(created):
            try:
                parent.rmdir()
            except OSError as error:
                failures.append(str(error))
        outcome = (
            f"rollback incomplete: {failures}"
            if failures
            else "target changes rolled back"
        )
        raise ValueError(
            f"Skill apply failed: {exc}; {outcome}; inspect {folder}"
        ) from exc
    return folder


def run_skills(
    target: Path,
    operation: str,
    bundles: list[str] | None,
    checkout: Path | None,
    revision: str | None,
    plan_path: Path | None,
    html: str | Path | None,
    apply: bool,
    expected: str | None,
) -> int:
    root = target_root(target)
    if apply:
        if plan_path is None or not expected:
            raise ValueError(
                "Skill apply requires --plan PATH --expect TOKEN from a preview"
            )
        if checkout is not None or revision is not None or bundles is not None:
            raise ValueError(
                "Apply uses the saved plan; omit --from, --ref and --bundle"
            )
        plan_path = checked_root(plan_path)
        document = read_stage(plan_path, root)
        if operation != document["operation"]:
            raise ValueError("Skill operation does not match saved plan")
        saved = apply_stage(document, plan_path, expected)
        print(
            f"Applied saved skill plan offline. Recovery: {saved}. Application checks not run."
        )
        return 0
    document = build_stage(
        root, bundles or ["matt"], operation == "update", checkout, revision
    )
    if plan_path is None:
        folder = checked_root(SOURCE / "migrations" / root.name)
        folder.mkdir(parents=True, exist_ok=True)
        number = 1
        while (folder / f"skills-{number:03}.json").exists():
            number += 1
        plan_path = folder / f"skills-{number:03}.json"
    plan_path = report_destination(plan_path, root)
    path_at(Path(plan_path.anchor), plan_path.relative_to(plan_path.anchor).as_posix())
    with plan_path.open("xb") as stream:
        stream.write(encoded(document))
    token = digest(encoded(document))
    view = display(document)
    for note in view.notes:
        print(note)
    print(f"PLAN {plan_path}")
    print(f"PREVIEW {token}")
    if html is not None:
        destination = next_report(root, plan_path) if html == "auto" else Path(html)
        write_preview(view, destination, token=token)
        print(f"HTML preview: {destination}")
    if document["before"] == document["after"]:
        print("No changes")
    return 0
