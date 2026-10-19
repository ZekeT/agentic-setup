"""HTML reports are public CLI artifacts, never target changes."""

from test_inspection import snapshot
from test_transition import cli, legacy


def test_html_preview_shows_before_after_without_changing_target_or_token(tmp_path):
    target = legacy(tmp_path)
    report = tmp_path / "preview.html"
    before = snapshot(target)
    plain = cli("adopt", target, "--minimal")
    result = cli("adopt", target, "--minimal", "--html", report)
    assert result.returncode == 0, result.stderr + result.stdout
    assert snapshot(target) == before
    assert plain.stdout.split("PREVIEW ")[1].splitlines()[0] in result.stdout
    html = report.read_text()
    assert "Before" in html and "After" in html
    assert "Makefile" in html and "engineering" in html
    assert "No changes have been applied" in html
    assert "Team rule: retain audit logs." in html.replace("&nbsp;", " ")
    assert "ADD" in html and "UPDATE" in html and "DELETE" in html


def test_conflicts_are_reported_with_escaped_current_content(tmp_path):
    target = legacy(tmp_path)
    policy = target / "CLAUDE.md"
    policy.write_text(
        policy.read_text().replace(
            "## Read first", "## Team <script>alert('x')</script>"
        )
    )
    before = snapshot(target)
    report = tmp_path / "blocked.html"
    result = cli("adopt", target, "--minimal", "--html", report)
    assert result.returncode == 1
    html = report.read_text()
    assert "Blocked" in html and "customized integration" in html
    assert "No conflict resolution is proposed" in html
    assert "&lt;script&gt;" in html and "<script>" not in html
    assert "default-src 'none'" in html
    assert snapshot(target) == before


def test_html_rejects_apply_and_unsafe_output_without_writes(tmp_path):
    target = legacy(tmp_path)
    before = snapshot(target)
    report = tmp_path / "preview.html"
    applied = cli(
        "adopt", target, "--minimal", "--html", report, "--apply", "--expect", "unused"
    )
    assert applied.returncode == 1 and "preview-only" in applied.stderr
    assert not report.exists()
    contained = cli("adopt", target, "--minimal", "--html", target / "preview.html")
    assert contained.returncode == 1 and "outside the target" in contained.stderr
    report.write_text("Keep existing report")
    existing = cli("adopt", target, "--minimal", "--html", report)
    assert existing.returncode == 1 and "already exists" in existing.stderr
    assert report.read_text() == "Keep existing report"
    link = tmp_path / "linked"
    link.symlink_to(target, target_is_directory=True)
    symlink = cli("adopt", target, "--minimal", "--html", link / "preview.html")
    assert symlink.returncode == 1 and "Symlink refused" in symlink.stderr
    assert snapshot(target) == before


def test_skill_report_bounds_binary_and_large_content(tmp_path, installer):
    from skill_support import source_repo, target_repo
    from test_updates import commit

    source, skill, _ = source_repo(tmp_path)
    (skill / "binary.bin").write_bytes(b"\0\xff\x01")
    (skill / "large.txt").write_text("x" * 65_000)
    commit(source, "support assets")
    target = target_repo(tmp_path)
    before = snapshot(target)
    report = tmp_path / "skills.html"
    result = cli(
        "skills",
        "install",
        target,
        "--from",
        source,
        "--bundle",
        "show-me",
        "--html",
        report,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    html = report.read_text()
    assert "binary.bin" in html and "large.txt" in html
    assert "Comparison omitted: binary or large content" in html
    assert "65,000 bytes" in html and "SHA-256" in html
    assert "x" * 1000 not in html
    assert snapshot(target) == before


def test_report_handles_no_change_and_guidance_update_preview(tmp_path):
    import shutil
    import sys

    from test_transition import ROOT, run
    from test_updates import commit

    target = legacy(tmp_path)
    plain = cli("adopt", target, "--minimal")
    token = plain.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = cli("adopt", target, "--minimal", "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr
    commit(target, "adopted fixture")
    before = snapshot(target)
    report = tmp_path / "unchanged.html"
    repeat = cli("adopt", target, "--minimal", "--html", report)
    assert repeat.returncode == 0 and "No changes" in repeat.stdout
    assert "No file changes proposed" in report.read_text()
    upstream = tmp_path / "setup"
    upstream.mkdir()
    shutil.copytree(
        ROOT / "agentic_setup",
        upstream / "agentic_setup",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy(ROOT / "agentic", upstream / "agentic")
    run("git", "init", "-q", cwd=upstream)
    revision = commit(upstream, "clean setup source")
    update = run(
        sys.executable,
        str(upstream / "agentic"),
        "update",
        target,
        "--only",
        "explanation",
        "--source-ref",
        revision,
        "--html",
        tmp_path / "update.html",
    )
    assert update.returncode == 0, update.stderr + update.stdout
    assert "No file changes proposed" in (tmp_path / "update.html").read_text()
    assert snapshot(target) == before
