"""Bounded, metadata-previewed archival of dormant legacy directories."""

import hashlib
import json
import os
import stat
from dataclasses import dataclass
from difflib import unified_diff
from html import escape
from pathlib import Path

from .adopt import inspect_wiring
from .files import Plan, baseline, checked_root, digest, encoded, git, path_at, read
from .preview import STYLE, next_report, report_destination

SOURCE = Path(__file__).resolve().parents[1]
IGNORE_RULES = {
    b"/.engineering/graft/node_modules/",
    b"/.engineering/state/dependencies.json",
    b"/.engineering/state/verification/",
    b"/.engineering/tmp/",
    b"/.engineering/migration-work/",
}


def inventory(root: Path) -> dict[str, int | str]:
    """Fingerprint metadata without opening files or following directory symlinks."""
    fingerprint = hashlib.sha256()
    device = root.lstat().st_dev
    counts = {"files": 0, "bytes": 0, "links": 0, "directories": 0, "repositories": 0}
    pending = [root]
    while pending:
        path = pending.pop()
        info = path.lstat()
        if info.st_dev != device:
            raise ValueError(f"Mount boundary refused: {path}")
        if path.name == ".git":
            relative = path.relative_to(root).parts
            snapshot = (
                root.name == ".engineering"
                and len(relative) == 5
                and relative[:2] == ("state", "verification")
                and relative[3:] == ("checkout", ".git")
            )
            if not snapshot or not stat.S_ISDIR(info.st_mode):
                raise ValueError(
                    f"Nested Git metadata requires separate review: {path}"
                )
            checkout = path.parent
            common = Path(git(checkout, "rev-parse", "--git-common-dir"))
            common = (checkout / common).resolve()
            top = Path(git(checkout, "rev-parse", "--show-toplevel")).resolve()
            if (
                common != path
                or top != checkout
                or (path / "worktrees").exists()
                or (path / "objects/info/alternates").exists()
            ):
                raise ValueError(
                    f"Linked snapshot repository requires separate review: {path}"
                )
            counts["repositories"] += 1
        link = None
        if stat.S_ISLNK(info.st_mode):
            counts["links"] += 1
            link = os.readlink(path)
        elif stat.S_ISDIR(info.st_mode):
            counts["directories"] += 1
            pending.extend(sorted(path.iterdir(), reverse=True))
        elif stat.S_ISREG(info.st_mode):
            counts["files"] += 1
            counts["bytes"] += info.st_size
        else:
            raise ValueError(f"Special file refused: {path}")
        fingerprint.update(
            encoded(
                [
                    path.relative_to(root).as_posix(),
                    info.st_dev,
                    info.st_ino,
                    info.st_mode,
                    info.st_size,
                    info.st_mtime_ns,
                    info.st_ctime_ns,
                    link,
                ]
            )
        )
    return {**counts, "metadata_sha256": fingerprint.hexdigest()}


@dataclass
class Cleanup:
    root: Path
    baseline: str
    archive: Path
    trees: dict[str, dict[str, int | str]]
    before: bytes | None
    after: bytes | None
    adoption_notes: bool

    def token(self) -> str:
        return digest(
            encoded(
                {
                    "target": str(self.root),
                    "baseline": self.baseline,
                    "archive": str(self.archive),
                    "trees": self.trees,
                    "before": digest(self.before),
                    "after": digest(self.after),
                    "adoption_notes": self.adoption_notes,
                }
            )
        )

    def changed(self) -> bool:
        return bool(self.trees) or self.before != self.after

    def apply(self, expected: str) -> None:
        if expected != self.token():
            raise ValueError("Stale cleanup preview; preview again")
        fresh = plan_cleanup(self.root, self.archive, self.adoption_notes)
        if fresh.token() != expected:
            raise ValueError("Target changed; preview again")
        saved = checked_root(self.archive / expected)
        if saved.exists():
            raise ValueError(f"Recovery archive already exists: {saved}")
        saved.mkdir(parents=True, mode=0o700)
        moved: list[str] = []
        ignore_written = False
        try:
            (saved / "manifest.json").write_bytes(
                encoded(
                    {
                        "target": str(self.root),
                        "baseline": self.baseline,
                        "preview": expected,
                        "trees": self.trees,
                        "gitignore_changed": self.before != self.after,
                        "status": "prepared",
                    }
                )
            )
            if self.before is not None and self.before != self.after:
                (saved / "gitignore.before").write_bytes(self.before)
                (saved / "gitignore.before").chmod(0o600)
            for name in self.trees:
                destination = saved / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                (self.root / name).rename(destination)
                moved.append(name)
            if self.before != self.after:
                ignore_written = True
                assert self.after is not None
                path_at(self.root, ".gitignore").write_bytes(self.after)
            manifest = saved / "manifest.json"
            data = json.loads(manifest.read_bytes())
            data["status"] = "applied"
            manifest.write_bytes(encoded(data))
        except (OSError, ValueError) as exc:
            failures = []
            if ignore_written:
                try:
                    assert self.before is not None
                    path_at(self.root, ".gitignore").write_bytes(self.before)
                except OSError as error:
                    failures.append(str(error))
            for name in reversed(moved):
                try:
                    if (self.root / name).exists() or (self.root / name).is_symlink():
                        raise ValueError(f"Rollback destination occupied: {name}")
                    (saved / name).rename(self.root / name)
                except (OSError, ValueError) as error:
                    failures.append(str(error))
            detail = (
                f"Rollback incomplete: {failures}"
                if failures
                else "Target changes rolled back"
            )
            raise ValueError(
                f"Cleanup failed: {exc}. {detail}. Inspect {saved}"
            ) from exc


def plan_cleanup(target: Path, archive: Path | None, notes: bool) -> Cleanup:
    root = checked_root(target)
    if root == SOURCE or root.is_relative_to(SOURCE) or SOURCE.is_relative_to(root):
        raise ValueError("Target must be outside Agentic Setup")
    revision = baseline(root)
    wiring = Plan(root, revision)
    inspect_wiring(wiring)
    if wiring.conflicts:
        raise ValueError("; ".join(wiring.conflicts))
    archived_names = [b".engineering"]
    if notes:
        archived_names.append(b".scratch/agentic-setup-adoption")
    for name, raw in wiring.observed.items():
        if raw is not None and any(reference in raw for reference in archived_names):
            raise ValueError(
                f"Active reference into cleanup scope: {name}; reconcile before cleanup"
            )
    archive = checked_root(
        archive or SOURCE / "migrations" / root.name / "cleanup-backups"
    )
    path_at(Path(archive.anchor), archive.relative_to(archive.anchor).as_posix())
    if archive == root or archive.is_relative_to(root) or root.is_relative_to(archive):
        raise ValueError("Archive must be outside and not contain the target")
    ancestor = archive
    while not ancestor.exists():
        ancestor = ancestor.parent
    if not ancestor.is_dir() or ancestor.stat().st_dev != root.stat().st_dev:
        raise ValueError("Archive must be on the same filesystem as the target")
    trees = {}
    names = [".engineering"]
    if notes:
        names.append(".scratch/agentic-setup-adoption")
    for name in names:
        path = path_at(root, name)
        if path.exists():
            if not path.is_dir() or path.stat().st_dev != root.stat().st_dev:
                raise ValueError(f"Expected same-filesystem directory: {name}")
            trees[name] = inventory(path)
    before = read(root, ".gitignore")
    after = (
        None
        if before is None
        else b"".join(
            line
            for line in before.splitlines(keepends=True)
            if line.rstrip(b"\r\n") not in IGNORE_RULES
        )
    )
    return Cleanup(root, revision, archive, trees, before, after, notes)


def run_cleanup(
    target: Path,
    archive: Path | None,
    notes: bool,
    html: str | Path | None,
    apply: bool,
    expected: str | None,
) -> int:
    plan = plan_cleanup(target, archive, notes)
    saved = plan.archive / plan.token()
    print(f"BASELINE {plan.baseline}")
    for name, summary in plan.trees.items():
        print(
            f"ARCHIVE {name}: {summary['files']} files, {summary['bytes']} logical bytes, {summary['links']} symlinks, {summary['repositories']} standalone snapshot repositories"
        )
    diff = "".join(
        unified_diff(
            (plan.before or b"").decode().splitlines(True),
            (plan.after or b"").decode().splitlines(True),
            fromfile="before/.gitignore",
            tofile="after/.gitignore",
        )
    )
    if diff:
        print(diff)
    print(f"RECOVERY {saved}")
    print(
        "Stop target writers before apply. Inventory binds metadata, not file contents."
    )
    print(f"PREVIEW {plan.token()}")
    if html is not None:
        path = (
            next_report(plan.root)
            if html == "auto"
            else report_destination(Path(html), plan.root)
        )
        rows = "".join(
            f"<tr><td>{escape(name)}</td><td>{summary['files']} files; {summary['bytes']} logical bytes; {summary['links']} links; {summary['repositories']} standalone snapshot repositories</td><td>Moved intact to recovery archive; absent from target</td></tr>"
            for name, summary in plan.trees.items()
        )
        body = f"""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>Legacy cleanup preview</title><style>{STYLE}</style><h1>Archive legacy leftovers</h1>
<p>Target: {escape(str(plan.root))}</p><p>Baseline: {plan.baseline}</p>
<table><tr><th>Path</th><th>Before</th><th>After</th></tr>{rows}</table>
<h2>Ignore rules</h2><pre>{escape(diff or "No change")}</pre>
<h2>Recovery archive</h2><code>{escape(str(saved))}</code>
<p>Same-filesystem moves preserve symlinks without following them. Tree inventories use filesystem metadata; Git metadata is inspected read-only to identify standalone snapshots. Application and secret file contents are not scanned. No disk space reclamation is promised.</p>
<p>Stop target writers before applying. The token binds directory metadata, not content hashes. Unrelated local changes are preserved. No application checks run.</p>
<h2>Preview token</h2><code>{plan.token()}</code></html>"""
        with path.open("x", encoding="utf-8") as stream:
            stream.write(body)
        print(f"HTML preview: {path}")
    if not plan.changed():
        print("No changes")
    elif apply:
        if not expected:
            raise ValueError("Apply requires --expect <PREVIEW token>; preview first")
        plan.apply(expected)
        print(
            f"Applied cleanup. Recovery archive: {saved}. Native verification not run."
        )
    return 0
