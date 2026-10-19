"""Inspection advises through the CLI without modifying the target workspace."""

import hashlib
import json

import pytest
from test_transition import cli


def test_nonexistent_destination_recommends_init_without_creating_it(tmp_path):
    target = tmp_path / "new app"
    result = cli("inspect", target)
    assert result.returncode == 0, result.stderr
    assert "Setup: new destination" in result.stdout
    assert f"agentic init '{target}'" in result.stdout
    assert not target.exists()


def snapshot(root):
    return {
        str(p.relative_to(root)): (
            p.readlink().as_posix()
            if p.is_symlink()
            else hashlib.sha256(p.read_bytes()).hexdigest()
            if p.is_file()
            else None
        )
        for p in root.rglob("*")
    }


def test_brownfield_without_git_reports_existing_conventions_and_skills(tmp_path):
    target = tmp_path / "app"
    (target / ".claude/skills/team-review").mkdir(parents=True)
    (target / ".claude/skills/team-review/SKILL.md").write_text(
        "---\nname: code-review\n---\nTeam review\n"
    )
    (target / "CODING_STANDARDS.md").write_text(
        "# Coding standards\nKeep project rules.\n"
    )
    (target / "CLAUDE.md").write_text(
        "# Project instructions\nRead CODING_STANDARDS.md.\n"
    )
    (target / "package.json").write_text(
        '{"scripts":{"test":"touch SHOULD_NOT_EXIST"}}\n'
    )
    (target / ".env").symlink_to(tmp_path / "unreadable-secret")
    before = snapshot(target)
    result = cli("inspect", target)
    assert result.returncode == 0, result.stderr
    assert "Git: no repository" in result.stdout
    assert "project-owned" in result.stdout
    assert "missing: docs/agents/workflow.md" in result.stdout
    assert "code-review: unrecorded revision" in result.stdout
    assert "npm run test" in result.stdout
    assert "git init" in result.stdout
    assert "agentic adopt" in result.stdout
    assert snapshot(target) == before


def test_installed_conventions_distinguish_local_edits_from_available_updates(tmp_path):
    import json

    target = tmp_path / "app"
    assert cli("init", target).returncode == 0
    record_path = target / ".agentic-setup/install.json"
    record = json.loads(record_path.read_text())
    explanation = "docs/agents/explanation.md"
    record["files"][explanation] = "Old explanation template\n"
    (target / explanation).write_text("Old explanation template\n\nTeam addition\n")
    workflow = "docs/agents/workflow.md"
    (target / workflow).write_text("Team replacement workflow\n")
    record["files"]["CODING_STANDARDS.md"] = "Old standards\n"
    (target / "CODING_STANDARDS.md").write_text("# Coding standards\nTeam standards\n")
    record_path.write_text(json.dumps(record))
    before = snapshot(target)
    result = cli("inspect", target)
    assert result.returncode == 0, result.stderr
    assert "Installed version: 3.0.0" in result.stdout
    assert (
        "update available; local additions preserved: docs/agents/explanation.md"
        in result.stdout
    )
    assert "local edits; template unchanged: docs/agents/workflow.md" in result.stdout
    assert (
        "conflict; template and project both changed: CODING_STANDARDS.md"
        in result.stdout
    )
    assert "current: docs/agents/git-workflow.md" in result.stdout
    assert snapshot(target) == before


def test_archived_v2_recommends_minimal_adoption_without_mutation(tmp_path):
    from test_transition import legacy

    target = legacy(tmp_path)
    before = snapshot(target)
    result = cli("inspect", target)
    assert result.returncode == 0, result.stderr
    assert "Legacy: recognized Agentic Starter installation" in result.stdout
    assert f"agentic adopt {target} --minimal" in result.stdout
    assert snapshot(target) == before


@pytest.mark.parametrize("metadata", [".agentic-setup", ".starter"])
def test_skill_inventory_reports_recorded_missing_and_duplicate_skills(
    tmp_path, metadata
):
    target = tmp_path / "app"
    (target / metadata).mkdir(parents=True)
    (target / metadata / "skills.json").write_text(
        json.dumps(
            {
                "show-me": {
                    "source": "humanlayer/skills",
                    "commit": "newer-selected-revision",
                },
                "tdd": {"source": "mattpocock/skills", "commit": "recorded-revision"},
            }
        )
    )
    for folder in (".claude/skills/presentation", ".agents/skills/show-me"):
        (target / folder).mkdir(parents=True)
        (target / folder / "SKILL.md").write_text(
            "---\nname: show-me\n---\nPresentation\n"
        )
    before = snapshot(target)
    result = cli("inspect", target)
    assert result.returncode == 0, result.stderr
    assert (
        "show-me: recorded humanlayer/skills@newer-selected-revision" in result.stdout
    )
    assert "not necessarily outdated" in result.stdout
    assert "tdd: recorded but missing" in result.stdout
    assert "Duplicate exposed skill name: show-me" in result.stdout
    assert "Upstream freshness: not checked" in result.stdout
    assert snapshot(target) == before


@pytest.mark.parametrize(
    "name, content",
    [
        (".agentic-setup/install.json", "{}"),
        (".agentic-setup/install.json", '{"version":"3.0.0","files":[]}'),
        (".agentic-setup/skills.json", '{"show-me":null}'),
        ("package.json", "[]"),
        ("package.json", '{"scripts":[]}'),
    ],
)
def test_invalid_metadata_and_configuration_fail_cleanly(tmp_path, name, content):
    target = tmp_path / "app"
    path = target / name
    path.parent.mkdir(parents=True)
    path.write_text(content)
    before = snapshot(target)
    result = cli("inspect", target)
    assert result.returncode == 1
    assert "Error:" in result.stderr
    assert "Traceback" not in result.stderr
    assert snapshot(target) == before


def test_inspection_refuses_symlinked_skill_parent(tmp_path):
    target = tmp_path / "app"
    target.mkdir()
    outside = tmp_path / "outside"
    (outside / "skills/show-me").mkdir(parents=True)
    (outside / "skills/show-me/SKILL.md").write_text("---\nname: show-me\n---\n")
    (target / ".claude").symlink_to(outside, target_is_directory=True)
    result = cli("inspect", target)
    assert result.returncode == 1
    assert "Symlink refused" in result.stderr


def test_inspection_refuses_symlinked_skill_even_without_a_skill_file(tmp_path):
    target = tmp_path / "app"
    (target / ".claude/skills").mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (target / ".claude/skills/external").symlink_to(outside, target_is_directory=True)
    result = cli("inspect", target)
    assert result.returncode == 1
    assert "Symlink refused" in result.stderr
    assert not list(outside.iterdir())
