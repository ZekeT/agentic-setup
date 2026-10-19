"""A later source revision updates guidance without erasing application work."""

import shutil
import sys

import pytest
from test_transition import ROOT, cli, legacy, run


def commit(root, message):
    run("git", "add", ".", cwd=root)
    result = run(
        "git",
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        message,
        cwd=root,
    )
    assert result.returncode == 0, result.stderr
    return run("git", "rev-parse", "HEAD", cwd=root).stdout.strip()


@pytest.mark.parametrize("metadata", [".agentic-setup", ".starter"])
def test_later_selective_update_preserves_application_and_customization(
    tmp_path, metadata
):
    target = legacy(tmp_path)
    preview = cli("adopt", target, "--minimal")
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = cli("adopt", target, "--minimal", "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr
    if metadata == ".starter":
        (target / ".agentic-setup").rename(target / ".starter")
    commit(target, "minimal transition")
    guidance = target / "docs/agents/explanation.md"
    guidance.write_text(guidance.read_text() + "\nTeam example: invoices.\n")
    (target / "app.js").write_text('console.log("application progress");\n')
    commit(target, "application work and custom guidance")
    upstream = tmp_path / "starter"
    upstream.mkdir()
    shutil.copytree(
        ROOT / "agentic_setup",
        upstream / "agentic_setup",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy(ROOT / "agentic", upstream / "agentic")
    run("git", "init", "-q", cwd=upstream)
    incoming = upstream / "agentic_setup/payload/docs/agents/explanation.md"
    incoming.write_text(
        incoming.read_text().replace(
            "a compact show-me briefing", "a concrete show-me briefing"
        )
    )
    revision = commit(upstream, "explicit later explanation update")
    command = [
        sys.executable,
        str(upstream / "agentic"),
        "update",
        str(target),
        "--only",
        "explanation",
        "--source-ref",
        revision,
    ]
    preview = run(*command, cwd=upstream)
    assert preview.returncode == 0, preview.stderr
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = run(*command, "--apply", "--expect", token, cwd=upstream)
    assert applied.returncode == 0, applied.stderr
    assert "a concrete show-me briefing" in guidance.read_text()
    assert "Team example: invoices." in guidance.read_text()
    assert (target / "app.js").read_text() == 'console.log("application progress");\n'
    assert "No changes" in run(*command, cwd=upstream).stdout
    repeated_adoption = run(
        sys.executable,
        str(upstream / "agentic"),
        "adopt",
        str(target),
        "--minimal",
        cwd=upstream,
    )
    assert repeated_adoption.returncode == 0, repeated_adoption.stderr
    assert "No changes" in repeated_adoption.stdout
    assert (target / metadata / "install.json").is_file()
    if metadata == ".starter":
        assert not (target / ".agentic-setup").exists()


@pytest.mark.parametrize(
    "case, expected_status, outcome",
    [
        ("current", "current", "unchanged"),
        ("already_updated", "current", "baseline_only"),
        ("local_additions", "local additions; template unchanged", "unchanged"),
        ("local_edits", "local edits; template unchanged", "unchanged"),
        ("update", "update available", "replace"),
        (
            "update_additions",
            "update available; local additions preserved",
            "preserve_additions",
        ),
        ("conflict", "conflict; template and project both changed", "conflict"),
        ("missing", "missing", "conflict"),
    ],
)
def test_inspection_and_update_agree_on_guidance_changes(
    tmp_path, case, expected_status, outcome
):
    import json

    upstream = tmp_path / "setup"
    shutil.copytree(
        ROOT / "agentic_setup",
        upstream / "agentic_setup",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy(ROOT / "agentic", upstream / "agentic")
    run("git", "init", "-q", cwd=upstream)
    revision = commit(upstream, "template source")
    command = [sys.executable, str(upstream / "agentic")]
    target = tmp_path / "app"
    assert run(*command, "init", str(target)).returncode == 0
    path = "docs/agents/explanation.md"
    guidance = target / path
    incoming = guidance.read_text()
    old = "Previously installed guidance\n"
    addition = "\nTeam rule: preserve invoice examples.\n"
    previous = (
        incoming if case in {"current", "local_additions", "local_edits"} else old
    )
    local = {
        "current": incoming,
        "already_updated": incoming,
        "local_additions": incoming + addition,
        "local_edits": "Project replacement\n",
        "update": old,
        "update_additions": old + addition,
        "conflict": "Project replacement\n",
        "missing": None,
    }[case]
    record_path = target / ".agentic-setup/install.json"
    record = json.loads(record_path.read_text())
    record["files"][path] = previous
    record_path.write_text(json.dumps(record))
    if local is None:
        guidance.unlink()
    else:
        guidance.write_text(local)
    run("git", "init", "-q", cwd=target)
    commit(target, "project baseline")
    report = run(*command, "inspect", str(target))
    assert report.returncode == 0, report.stderr
    assert f"{expected_status}: {path}" in report.stdout
    update = [
        *command,
        "update",
        str(target),
        "--only",
        "explanation",
        "--source-ref",
        revision,
    ]
    preview = run(*update)
    assert not run("git", "status", "--porcelain", cwd=target).stdout
    if outcome == "conflict":
        assert preview.returncode == 1
        assert f"CONFLICT {path}" in preview.stdout
        return
    assert preview.returncode == 0, preview.stderr
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = run(*update, "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr
    expected = (
        incoming + addition
        if outcome == "preserve_additions"
        else incoming
        if outcome == "replace"
        else local
    )
    assert guidance.read_text() == expected
    assert json.loads(record_path.read_text())["files"][path] == incoming
    assert "No changes" in run(*update).stdout
