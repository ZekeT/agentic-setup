"""A later source revision updates guidance without erasing application work."""

import shutil
import sys

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


def test_later_selective_update_preserves_application_and_customization(tmp_path):
    target = legacy(tmp_path)
    preview = cli("adopt", target, "--minimal")
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = cli("adopt", target, "--minimal", "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr
    commit(target, "minimal transition")
    guidance = target / "docs/agents/explanation.md"
    guidance.write_text(guidance.read_text() + "\nTeam example: invoices.\n")
    (target / "app.js").write_text('console.log("application progress");\n')
    commit(target, "application work and custom guidance")
    upstream = tmp_path / "starter"
    upstream.mkdir()
    shutil.copytree(
        ROOT / "starter",
        upstream / "starter",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy(ROOT / "engineering", upstream / "engineering")
    run("git", "init", "-q", cwd=upstream)
    incoming = upstream / "starter/payload/docs/agents/explanation.md"
    incoming.write_text(
        incoming.read_text().replace(
            "a compact show-me briefing", "a concrete show-me briefing"
        )
    )
    revision = commit(upstream, "explicit later explanation update")
    command = [
        sys.executable,
        str(upstream / "engineering"),
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
