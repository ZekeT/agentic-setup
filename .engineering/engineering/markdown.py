"""Check local links and heading anchors in Markdown files (best effort)."""

import posixpath
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from .config import safe_path

SUFFIXES = (".md", ".markdown")
# Longer lines are skipped, keeping every scan linear and bounded.
MAX_LINE = 1000
FENCE = re.compile(r"^(`{3,}|~{3,})(.*)$")
CONTAINER = re.compile(r"^\s*(?:>|(?:[-*+]|\d{1,9}[.)])(?= |$)) ?")
CODE = re.compile(r"(`+)[^`]*?\1")
LINK = re.compile(r"!?\[[^\]]*+\]\(\s*+(?:<([^<>\n]*+)>|([^\s)<>]++))(?:\s++[^)]*+)?\)")
REFERENCE = re.compile(r"^\[[^\]]++\]:\s*+(?:<([^<>\n]*+)>|(\S++))")
HEADING = re.compile(r"^#{1,6}(?:\s++(.*?))?(?:\s+#+)?\s*$")
UNDERLINE = re.compile(r"^(?:=+|-+)\s*$")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:|^//")
ANCHOR = re.compile(r"""<a\s[^>]*\b(?:id|name)=["']([^"']+)["']""")


def contents(line: str) -> str:
    """Line text inside any blockquote and list markers."""
    line = line.expandtabs(4)
    while marker := CONTAINER.match(line):
        line = line[marker.end() :]
    return line.strip()


def lines_outside_fences(text: str) -> list[str]:
    """Lines outside code fences (container text only), skipping long lines."""
    found: list[str] = []
    fence = ""
    for line in text.splitlines():
        if len(line) > MAX_LINE:
            continue
        content = contents(line)
        marker = FENCE.match(content)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = ""
        elif marker:
            fence = marker[1]
        else:
            found.append(content)
    return found


def slug(heading: str) -> str:
    """A GitHub-style heading anchor from rendered heading text."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading.replace("`", ""))
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"[^\w\- ]", "", text.strip().lower())
    return text.replace(" ", "-")


def headings(lines: list[str]) -> list[str]:
    """ATX and setext heading texts, including inside containers."""
    found: list[str] = []
    previous = ""
    for content in lines:
        if atx := HEADING.match(content):
            found.append(atx[1] or "")
            previous = ""
        elif UNDERLINE.match(content) and previous:
            found.append(previous)
            previous = ""
        else:
            previous = content
    return found


def anchors(text: str) -> set[str]:
    """Heading slugs (with GitHub duplicate suffixes) and explicit HTML anchors."""
    lines = lines_outside_fences(text)
    found = {anchor for line in lines for anchor in ANCHOR.findall(line)}
    counts: dict[str, int] = {}
    for heading in headings(lines):
        base = slug(heading)
        count = counts.get(base, 0)
        counts[base] = count + 1
        found.add(base if count == 0 else f"{base}-{count}")
    return found


def links(text: str) -> list[str]:
    """Link and image targets and reference definitions outside code."""
    targets: list[str] = []
    for content in lines_outside_fences(text):
        if reference := REFERENCE.match(content):
            targets.append(reference[1] or reference[2])
            continue
        for angle, bare in LINK.findall(CODE.sub("", content)):
            targets.append(angle or bare)
    return targets


def read_markdown(root: Path, name: str) -> str:
    """Read a repository Markdown file as UTF-8, refusing unsafe paths."""
    path = safe_path(root, name)
    if not path.is_file():
        raise ValueError(f"{name}: not a regular file")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{name}: not UTF-8 text") from error


def broken_links(root: Path, name: str) -> list[str]:
    """Local link targets and anchors in name that do not resolve in root."""
    text = read_markdown(root, name)
    broken = []
    # Anchors per target file, computed once however many links point at it.
    known: dict[str, set[str]] = {}
    for target in links(text):
        if not target or SCHEME.match(target):
            continue
        location, _, fragment = target.partition("#")
        location = unquote(location.partition("?")[0])
        fragment = unquote(fragment)
        if location:
            base = "" if location.startswith("/") else posixpath.dirname(name)
            relative = posixpath.normpath(posixpath.join(base, location.lstrip("/")))
            path = root / relative
            if (
                relative.startswith("..")
                or not path.exists()
                or not path.resolve().is_relative_to(root.resolve())
            ):
                broken.append(target)
                continue
            if not fragment or not path.is_file() or not relative.endswith(SUFFIXES):
                continue
        else:
            relative = name
        if fragment:
            if relative not in known:
                content = text if relative == name else read_markdown(root, relative)
                known[relative] = anchors(content)
            if fragment not in known[relative]:
                broken.append(target)
    return broken


def link_problems(root: Path, names: list[str]) -> list[str]:
    """Problems in the named Markdown files; empty when every link resolves."""
    problems = []
    for name in names:
        try:
            problems += [
                f"{name}: broken link {target}" for target in broken_links(root, name)
            ]
        except (ValueError, OSError) as error:
            problems.append(str(error))
    return problems


def run(root: Path, names: list[str]) -> int:
    """Print link problems and a summary; nonzero when any problem exists."""
    problems = link_problems(root, names)
    for problem in problems:
        print(problem, file=sys.stderr)
    mark = "✗" if problems else "✓"
    print(f"{mark} docs-check: {len(names)} file(s), {len(problems)} problem(s)")
    return int(bool(problems))
