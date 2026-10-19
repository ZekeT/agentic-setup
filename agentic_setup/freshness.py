"""Read-only comparisons: external installation runs only in disposable staging."""

from pathlib import Path

from .files import Plan
from .skill_stage import build_stage, target_root
from .skills import BUNDLES, external_records, skill_locations


def check_skills(target: Path, bundle: str | None) -> tuple[str, int]:
    root = target_root(target)
    plan = Plan(root, "")
    installed = skill_locations(plan)
    records = external_records(plan)
    bundles = [bundle] if bundle else list(BUNDLES)
    supported = {n for b in bundles for n in BUNDLES[b][2]}
    lines = [
        f"Target: {root}",
        "Read-only staged comparison; external check/update is never run in the target.",
    ]
    for name in sorted(installed.keys() - supported):
        if bundle is None:
            lines.append(f"  {name}: outside selected bundles; not checked")
    if not (installed.keys() | records.keys()) & supported:
        lines.append("No installed supported skills to compare; use skills install.")
        return "\n".join(lines), 0
    stage = build_stage(root, bundles, True, None, None)
    for name in stage["names"]:
        prefixes = (f".agents/skills/{name}", f".claude/skills/{name}")
        before = {
            n: v
            for n, v in stage["before"].items()
            if any(n == p or n.startswith(p + "/") for p in prefixes)
        }
        after = {
            n: v
            for n, v in stage["after"].items()
            if any(n == p or n.startswith(p + "/") for p in prefixes)
        }
        status = (
            "installed files/layout differ from current upstream proposal"
            if before != after
            else "installed files/layout match current upstream proposal"
        )
        record = (
            "external record present"
            if name in records
            else "unrecorded; preview install to establish external records"
        )
        lines.append(f"  {name}: {status}; {record}")
    lines.append(
        "Differences may include local customizations; this does not certify compatibility. Preview skills update/install for an HTML comparison. Target unchanged."
    )
    return "\n".join(lines), 0
