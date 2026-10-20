"""Frozen plan updates replace the retired custom skill ownership contract."""

import json

import pytest
from skill_support import saved_plan, source_repo, target_repo
from test_transition import cli


def stage(tmp_path, target, source, name="plan.json", operation="install"):
    return saved_plan(
        cli(
            "skills",
            operation,
            target,
            "--from",
            source,
            "--bundle",
            "show-me",
            "--plan",
            tmp_path / name,
        )
    )


@pytest.mark.parametrize("change", ["target", "new-file", "mode", "plan", "baseline"])
def test_stale_plan_is_refused_without_target_writes(tmp_path, installer, change):
    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    old = target / ".claude/skills/show-me"
    old.mkdir(parents=True)
    (old / "SKILL.md").write_text("---\nname: show-me\n---\nOriginal local")
    plan, token = stage(tmp_path, target, source)
    if change == "target":
        (old / "SKILL.md").write_text("Changed local")
    elif change == "new-file":
        (old / "new.txt").write_text("New work")
    elif change == "mode":
        (old / "SKILL.md").chmod(0o700)
    elif change == "baseline":
        from test_updates import commit

        commit(target, "new baseline")
    else:
        doc = json.loads(plan.read_text())
        doc["sources"]["show-me"] = "modified input"
        plan.write_text(json.dumps(doc))
    current = (old / "SKILL.md").read_bytes()
    result = cli(
        "skills", "install", target, "--plan", plan, "--apply", "--expect", token
    )
    assert result.returncode != 0
    assert (old / "SKILL.md").read_bytes() == current
    assert not (target / ".agents").exists()
    assert not (tmp_path / "backups").exists()


def test_customized_unrecorded_skill_is_backed_up_and_only_selected_records_retire(
    tmp_path, installer
):
    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    folder = target / ".claude/skills/show-me"
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(
        "---\nname: show-me\n---\nCustom local presentation"
    )
    (folder / "team.txt").write_text("Local extra")
    metadata = target / ".agentic-setup"
    metadata.mkdir()
    (metadata / "skills.json").write_text(
        json.dumps(
            {
                "show-me": {"source": "humanlayer/skills", "commit": "old"},
                "tdd": {"source": "mattpocock/skills", "commit": "keep"},
            }
        )
    )
    (metadata / "install.json").write_text("untouched convention baseline")
    plan, token = stage(tmp_path, target, source)
    assert "team.txt" in plan.read_text()
    assert (folder / "team.txt").exists()
    result = cli(
        "skills", "install", target, "--plan", plan, "--apply", "--expect", token
    )
    assert result.returncode == 0, result.stderr
    backup = tmp_path / "backups" / token / "before"
    assert (backup / ".claude/skills/show-me/team.txt").read_text() == "Local extra"
    assert "Custom local" in (backup / ".claude/skills/show-me/SKILL.md").read_text()
    assert not (folder / "team.txt").exists()
    assert (metadata / "install.json").read_text() == "untouched convention baseline"
    assert set(json.loads((metadata / "skills.json").read_text())) == {"tdd"}


def test_update_is_frozen_and_unrelated_project_edits_survive(tmp_path, installer):
    source, skill, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    plan, token = stage(tmp_path, target, source)
    assert (
        cli(
            "skills", "install", target, "--plan", plan, "--apply", "--expect", token
        ).returncode
        == 0
    )
    (skill / "support.md").write_text("Reviewed update")
    from test_updates import commit

    commit(source, "update")
    plan, token = stage(tmp_path, target, source, "update.json", "update")
    (target / "app.txt").write_text("Unrelated dirty work")
    installer.unlink()
    result = cli(
        "skills", "update", target, "--plan", plan, "--apply", "--expect", token
    )
    assert result.returncode == 0, result.stderr
    assert (
        target / ".agents/skills/show-me/support.md"
    ).read_text() == "Reviewed update"
    assert (target / "app.txt").read_text() == "Unrelated dirty work"
    assert (
        cli(
            "skills", "update", target, "--plan", plan, "--apply", "--expect", token
        ).returncode
        != 0
    )


def test_ordinary_apply_failure_restores_original_layout(
    tmp_path, installer, monkeypatch, capsys
):
    import sys
    from pathlib import Path

    from agentic_setup.cli import main

    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    old = target / ".claude/skills/show-me"
    old.mkdir(parents=True)
    (old / "SKILL.md").write_text("---\nname: show-me\n---\nOriginal")
    plan, token = stage(tmp_path, target, source)
    original = Path.rename

    def fail_lock(path, destination):
        if path.name == "skills-lock.json" and "proposed" in path.parts:
            raise OSError("injected failure")
        return original(path, destination)

    monkeypatch.setattr(Path, "rename", fail_lock)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "agentic",
            "skills",
            "install",
            str(target),
            "--plan",
            str(plan),
            "--apply",
            "--expect",
            token,
        ],
    )
    assert main() == 1
    assert "rolled back" in capsys.readouterr().err
    assert old.is_dir() and not old.is_symlink()
    assert (old / "SKILL.md").read_text().endswith("Original")
    assert not (target / ".agents").exists()
    assert not (target / "skills-lock.json").exists()
