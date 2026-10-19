"""Explicit online revision comparisons; never write into the target workspace."""

import re
from pathlib import Path

from .adopt import metadata_directory
from .files import Plan, checked_root, git
from .skills import BUNDLES, skill_locations, skill_records
from .sources import skill_source


def revision_status(checkout: Path, recorded: str, latest: str) -> str:
    if recorded == latest:
        return "current"
    try:
        git(checkout, "cat-file", "-e", f"{recorded}^{{commit}}")
    except ValueError:
        # Only a validated hash is fetched, from the configured bundle remote.
        git(checkout, "fetch", "--quiet", "origin", recorded)
    ancestor = git(checkout, "merge-base", recorded, latest)
    if ancestor == recorded:
        return "behind (upstream advanced; preview an update)"
    if ancestor == latest:
        return "ahead (recorded revision is newer than upstream HEAD)"
    return "diverged (review history before updating)"


def check_skills(target: Path, bundle: str | None) -> tuple[str, int]:
    target = checked_root(target)
    if not target.is_dir():
        raise ValueError("Target must be an existing workspace directory")
    plan = Plan(target, "")
    metadata = metadata_directory(plan)
    records = skill_records(plan, f"{metadata}/skills.json")
    locations = skill_locations(plan)
    selected = {
        name: source
        for key, (source, _, names) in BUNDLES.items()
        if bundle is None or key == bundle
        for name in names
    }
    names = records.keys() | locations.keys()
    if bundle is not None:
        names &= selected.keys()
    lines = [
        f"Target: {target}",
        "Online upstream revision check; installed contents not verified.",
        "Repository revisions do not certify skill changes or compatibility.",
    ]
    pending: dict[str, list[str]] = {}
    incomplete = False
    for name in sorted(names):
        record = records.get(name)
        paths = locations.get(name, [])
        if record is None:
            lines.append(f"  {name}: unrecorded revision; not checked")
            continue
        if not paths:
            lines.append(f"  {name}: recorded but missing")
            incomplete = True
        elif len(paths) > 1:
            lines.append(f"  {name}: duplicate installed locations; reconcile")
            incomplete = True
        source = selected.get(name)
        if source is None or record["source"] != source:
            lines.append(f"  {name}: unknown source; not checked")
            incomplete = True
        elif not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", record["commit"]):
            lines.append(f"  {name}: invalid recorded commit; not checked")
            incomplete = True
        else:
            pending.setdefault(source, []).append(name)
    for source, skills in pending.items():
        try:
            with skill_source(source, None, None) as checkout:
                latest = git(checkout, "rev-parse", "HEAD")
                lines.append(f"Upstream: {source}@{latest}")
                statuses = {}
                for name in skills:
                    recorded = records[name]["commit"]
                    if recorded not in statuses:
                        try:
                            statuses[recorded] = revision_status(
                                checkout, recorded, latest
                            )
                        except ValueError:
                            statuses[recorded] = (
                                "unknown (recorded history unavailable or unrelated)"
                            )
                            incomplete = True
                    lines.append(f"  {name}: {statuses[recorded]}; recorded {recorded}")
        except (ValueError, OSError) as exc:
            lines.append(f"Upstream: {source}: unavailable ({exc})")
            lines.extend(f"  {name}: unknown; upstream check failed" for name in skills)
            incomplete = True
    if not pending:
        lines.append("No supported recorded revisions to check; no upstream contacted.")
    lines.append(
        "Read-only: no target files changed. Use skills update to preview changes."
    )
    return "\n".join(lines), int(incomplete)
