"""Public staged-skill journeys with exact frozen apply behavior."""

from skill_support import saved_plan, source_repo, target_repo
from test_transition import cli


def test_staged_install_applies_reviewed_bytes_without_installer(tmp_path, installer):
    source, skill, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    output = tmp_path / "plan.json"
    preview = cli(
        "skills",
        "install",
        target,
        "--bundle",
        "show-me",
        "--from",
        source,
        "--plan",
        output,
        "--html",
        tmp_path / "preview.html",
    )
    plan, token = saved_plan(preview)
    assert not (target / ".agents").exists()
    (skill / "SKILL.md").write_text("Different upstream after preview")
    installer.unlink()
    result = cli(
        "skills", "install", target, "--plan", plan, "--apply", "--expect", token
    )
    assert result.returncode == 0, result.stderr
    assert (target / ".claude/skills/show-me").is_symlink()
    assert (
        "Upstream presentation"
        in (target / ".agents/skills/show-me/SKILL.md").read_text()
    )
    assert (target / "app.txt").read_text() == "Keep application\n"
    assert (target / "skills-lock.json").exists()
    assert not (target / ".agentic-setup/skills.json").exists()


def test_inspection_recognizes_external_lock_and_one_alias_installation(
    tmp_path, installer
):
    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    plan, token = saved_plan(
        cli(
            "skills",
            "install",
            target,
            "--from",
            source,
            "--bundle",
            "show-me",
            "--plan",
            tmp_path / "plan.json",
        )
    )
    assert (
        cli(
            "skills", "install", target, "--plan", plan, "--apply", "--expect", token
        ).returncode
        == 0
    )
    result = cli("inspect", target)
    assert result.returncode == 0, result.stderr
    assert "show-me: external lock" in result.stdout
    assert "Duplicate exposed skill name" not in result.stdout


def test_migration_html_compares_old_copy_with_new_canonical_content(
    tmp_path, installer
):
    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    old = target / ".claude/skills/show-me"
    old.mkdir(parents=True)
    (old / "SKILL.md").write_text(
        "---\nname: show-me\n---\nExisting local presentation\n"
    )
    report = tmp_path / "preview.html"
    result = cli(
        "skills",
        "install",
        target,
        "--from",
        source,
        "--bundle",
        "show-me",
        "--plan",
        tmp_path / "plan.json",
        "--html",
        report,
    )
    assert result.returncode == 0, result.stderr
    html = report.read_text()
    assert "Before content from .claude/skills/show-me/SKILL.md" in html
    assert "Existing local presentation" in html and "Upstream presentation" in html
