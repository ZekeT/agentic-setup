"""Checks stage external installs and never run the mutating npm check command."""

from skill_support import saved_plan, source_repo, target_repo
from test_transition import cli


def test_check_is_readonly_and_uses_only_configured_upstreams(
    tmp_path, installer, monkeypatch
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
    # This external-process fixture maps a configured GitHub source to a local fixture.
    text = installer.read_text().replace(
        "source=Path(args[4]); names=", f"source=Path({str(source)!r}); names="
    )
    text = text.replace(
        "'source':os.path.relpath(source,root),'sourceType':'local'",
        "'source':'humanlayer/skills','sourceType':'github'",
    )
    installer.write_text(text)
    (target / ".agents/skills/show-me/support.md").write_text("Local customization")
    before = (target / "skills-lock.json").read_bytes()
    result = cli("skills", "check", target, "--bundle", "show-me")
    assert result.returncode == 0, result.stderr
    assert "differ" in result.stdout and "Target unchanged" in result.stdout
    assert (
        target / ".agents/skills/show-me/support.md"
    ).read_text() == "Local customization"
    assert (target / "skills-lock.json").read_bytes() == before


def test_empty_check_does_not_need_installer(tmp_path, monkeypatch):
    target = target_repo(tmp_path)
    result = cli("skills", "check", target)
    assert result.returncode == 0 and "No installed supported skills" in result.stdout
