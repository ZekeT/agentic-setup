"""Standalone HTML views of an already-computed transition plan."""

from difflib import SequenceMatcher
from html import escape
from itertools import zip_longest
from pathlib import Path

from .files import Plan, checked_root, digest

STYLE = """
:root {color-scheme:light; font:16px/1.5 system-ui,sans-serif; color:#243247; background:#f3f5f8}
body {max-width:1440px; margin:0 auto; padding:32px}
h1 {font-size:2rem; margin:8px 0} h2 {margin-top:32px} p {max-width:100ch}
header,.panel,details {background:white; border:1px solid #d8dfe8; border-radius:10px; padding:18px; margin:12px 0}
.eyebrow {color:#526178; text-transform:uppercase; letter-spacing:.12em; font-size:.8rem}
.cards {display:flex; flex-wrap:wrap; gap:12px}.card {background:white; padding:12px 24px; border-radius:8px; border:1px solid #d8dfe8}
.card strong {font-size:1.7rem; display:block}.blocked {border-left:5px solid #b42318; background:#fff4f2}
.ready {border-left:5px solid #13795b}.muted {color:#526178}.badge {display:inline-block; font:700 .75rem system-ui; padding:5px 8px; border-radius:5px; margin-right:10px; background:#e7edf5}
.add {background:#dcf4e5}.delete {background:#ffe4e1}.update {background:#fff0c2}
summary {cursor:pointer; overflow-wrap:anywhere} summary:hover {color:#174ea6}
code,pre {font-family:ui-monospace,SFMono-Regular,Consolas,monospace} code {overflow-wrap:anywhere}
pre {white-space:pre-wrap; overflow-wrap:anywhere; font-size:.82rem; margin:0}
.table-scroll {overflow-x:auto; margin-top:16px} table {border-collapse:collapse; width:100%; table-layout:fixed; min-width:650px; font-size:.82rem}
th {background:#eaf0f6; text-align:left; padding:8px} td {vertical-align:top; border:1px solid #e3e7ed; padding:4px 8px}
td.num {width:42px; text-align:right; color:#6b7789; background:#f5f7fa}.removed {background:#fff0ee}.added {background:#eaf8ee}
.gap {text-align:center; color:#6b7789; background:#f5f7fa} li {margin:6px 0}
a {color:#174ea6}.token {font-size:.8rem}@media(max-width:650px){body{padding:12px}.card{padding:8px 16px}}
@media print {body{background:white;padding:0}details{break-inside:avoid}}
"""


def next_report(target: Path, resolutions: Path | None = None) -> Path:
    root = checked_root(target)
    folder = (
        checked_root(resolutions).parent
        if resolutions is not None
        else Path(__file__).resolve().parents[1] / "migrations" / root.name
    )
    folder = checked_root(folder)
    if folder == root or folder.is_relative_to(root):
        raise ValueError("HTML report must be outside the target workspace")
    folder.mkdir(parents=True, exist_ok=True)
    number = 1
    while (folder / f"preview-{number:03}.html").exists():
        number += 1
    return report_destination(folder / f"preview-{number:03}.html", root)


def report_destination(path: Path, target: Path) -> Path:
    destination, root = checked_root(path), checked_root(target)
    if destination == root or destination.is_relative_to(root):
        raise ValueError("HTML report must be outside the target workspace")
    if destination.exists():
        raise ValueError("HTML report already exists; choose a new output filename")
    if not destination.parent.is_dir():
        raise ValueError("HTML report parent directory must already exist")
    return destination


def text_content(raw: bytes | None) -> str | None:
    if raw is None:
        return ""
    if len(raw) > 64_000 or b"\0" in raw:
        return None
    try:
        value = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    lines = value.splitlines()
    if len(lines) > 800 or any(len(line) > 1000 for line in lines):
        return None
    return value


def content_summary(raw: bytes | None) -> str:
    if raw is None:
        return "File absent"
    return f"{len(raw):,} bytes; SHA-256 {digest(raw)}"


def comparison(before: bytes | None, after: bytes | None) -> str:
    old, new = text_content(before), text_content(after)
    metadata = (
        f'<p class="muted">Before: {content_summary(before)}<br>'
        f"After: {content_summary(after)}</p>"
    )
    if old is None or new is None:
        return (
            metadata
            + "<p>Comparison omitted: binary or large content. No content was truncated.</p>"
        )
    left, right = old.splitlines(), new.splitlines()
    rows = []
    for group_number, group in enumerate(
        SequenceMatcher(None, left, right).get_grouped_opcodes(3)
    ):
        if group_number:
            rows.append(
                '<tr><td colspan="4" class="gap">Unchanged lines omitted</td></tr>'
            )
        for tag, i, j, k, end in group:
            for a, b in zip_longest(range(i, j), range(k, end)):
                old_cell = escape(left[a]) if a is not None else ""
                new_cell = escape(right[b]) if b is not None else ""
                old_class = "removed" if tag != "equal" and a is not None else ""
                new_class = "added" if tag != "equal" and b is not None else ""
                rows.append(
                    f'<tr><td class="num">{a + 1 if a is not None else ""}</td>'
                    f'<td class="{old_class}"><pre>{old_cell}</pre></td>'
                    f'<td class="num">{b + 1 if b is not None else ""}</td>'
                    f'<td class="{new_class}"><pre>{new_cell}</pre></td></tr>'
                )
    if not rows:
        rows.append(
            '<tr><td colspan="4">No line-content differences (check byte hashes above).</td></tr>'
        )
    return metadata + (
        '<div class="table-scroll"><table><colgroup><col style="width:48px"><col>'
        '<col style="width:48px"><col></colgroup><thead><tr><th colspan="2">Before</th>'
        '<th colspan="2">After (proposed)</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table></div>"
    )


def render_preview(plan: Plan, token: str | None = None) -> str:
    groups: dict[str, list[str]] = {"UPDATE": [], "ADD": [], "DELETE": []}
    for name, after in plan.changes.items():
        action = (
            "DELETE"
            if after is None
            else "ADD"
            if plan.observed[name] is None
            else "UPDATE"
        )
        groups[action].append(name)
    status = (
        "Blocked — resolve conflicts and preview again"
        if plan.conflicts
        else "Preview ready for review"
    )
    parts = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'\">",
        f"<title>Agentic Setup preview — {escape(plan.root.name)}</title><style>{STYLE}</style></head><body>",
        '<header><div class="eyebrow">Agentic Setup · transition preview</div>',
        "<h1>Review before changing your workspace</h1>",
        "<p><strong>No changes have been applied.</strong> This is a snapshot of proposed changes, not an approval or an execution result.</p>",
        f"<p>Target: <code>{escape(str(plan.root))}</code><br>Git baseline: <code>{escape(plan.baseline)}</code></p></header>",
        f'<section class="panel {"blocked" if plan.conflicts else "ready"}"><strong>{status}</strong>',
        "<p>Refine unresolved proposals in Agentic Setup and regenerate the preview. Apply only after explicit approval of the preview, using its matching token. Changed inputs require a new preview.</p></section>",
        '<div class="cards">',
        *[
            f'<div class="card"><strong>{len(names)}</strong>{action.title()} files</div>'
            for action, names in groups.items()
        ],
        f'<div class="card"><strong>{len(plan.conflicts)}</strong>Conflicts</div></div>',
    ]
    resolutions = [note for note in plan.notes if note.startswith("RESOLVE ")]
    if resolutions:
        parts.append(
            "<h2>Project resolutions</h2><p>Explicit project decisions, included in this preview only. No target changes have been applied.</p><ul>"
        )
        parts.extend(f"<li>{escape(note)}</li>" for note in resolutions)
        parts.append("</ul>")
    if plan.conflicts:
        parts.append("<h2>Conflicts — resolve before applying</h2>")
        for conflict in plan.conflicts:
            parts.append(f'<div class="panel blocked"><p>{escape(conflict)}</p>')
            names = [name for name in plan.observed if conflict.startswith(name + ":")]
            if names:
                name = max(names, key=len)
                raw = plan.observed[name]
                text = text_content(raw)
                parts.append(
                    "<p>No conflict resolution is proposed here. Current content is preserved.</p>"
                )
                parts.append("<details><summary>Current content</summary>")
                parts.append(f'<p class="muted">{content_summary(raw)}</p>')
                parts.append(
                    f"<pre>{escape(text)}</pre>"
                    if text is not None
                    else "<p>Content omitted: binary or large file.</p>"
                )
                parts.append("</details>")
            parts.append("</div>")
    parts.append(
        '<h2>Proposed file changes</h2><p class="muted">Expand a file to compare. Red marks removed lines; green marks added lines. Diffs show three lines of surrounding context. These proposals are not applied, including when conflicts exist.</p>'
    )
    if not plan.changes:
        parts.append("<p>No file changes proposed.</p>")
    for action, names in groups.items():
        if not names:
            continue
        parts.append(f"<h3>{action.title()} · {len(names)}</h3>")
        for name in sorted(names):
            parts.append(
                f'<details><summary><span class="badge {action.lower()}">{action}</span><code>{escape(name)}</code></summary>'
            )
            reasons = [
                note for note in plan.notes if note.startswith(f"{action} {name}:")
            ]
            parts.extend(f"<p>{escape(reason)}</p>" for reason in reasons)
            parts.append(comparison(plan.observed[name], plan.changes[name]))
            parts.append("</details>")
    parts.append(
        '<h2>Preservation and planning notes</h2><p class="muted">Notes reflect the planner’s inspected scope, not an exhaustive inventory of the project.</p><ul>'
    )
    parts.extend(
        f"<li>{escape(note)}</li>"
        for note in plan.notes
        if not note.startswith(("ADD ", "UPDATE ", "DELETE "))
    )
    parts.append('</ul><section class="panel"><h2>Preview identity</h2>')
    parts.append(f'<p class="token"><code>{token or plan.token()}</code></p>')
    parts.append(
        "<p>Keep this report local: it may include project configuration. HTML export does not authorize applying changes.</p></section></body></html>"
    )
    return "".join(parts)


def write_preview(plan: Plan, destination: Path, token: str | None = None) -> None:
    destination = report_destination(destination, plan.root)
    rendered = render_preview(plan, token)
    with destination.open("x", encoding="utf-8") as output:
        output.write(rendered)
