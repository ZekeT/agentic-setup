"""Explicit skill operations preserve project work through the external CLI."""

import json

import pytest
from test_inspection import snapshot
from test_transition import cli, run
from test_updates import commit


def source_repo(tmp_path):
    source = tmp_path / "source"
    skill = source / "plugins/show-me/skills/show-me"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: show-me\n---\nOriginal presentation\n")
    (skill / "old.md").write_text("Old support\n")
    (source / "LICENSE").write_text("Fixture license\n")
    run("git", "init", "-q", cwd=source)
    revision = commit(source, "initial upstream")
    return source, skill, revision


def target_repo(tmp_path):
    target = tmp_path / "app"
    target.mkdir()
    (target / "app.txt").write_text("Project work\n")
    run("git", "init", "-q", cwd=target)
    commit(target, "project baseline")
    return target


def apply(*args):
    preview = cli(*args)
    assert preview.returncode == 0, preview.stderr + preview.stdout
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    result = cli(*args, "--apply", "--expect", token)
    assert result.returncode == 0, result.stderr + result.stdout
    return result


def test_install_accepts_explicit_checkout_head_and_records_files(tmp_path):
    source, skill, revision = source_repo(tmp_path)
    target = target_repo(tmp_path)
    command = ["skills", "install", target, "--from", source, "--bundle", "show-me"]
    before = snapshot(target)
    preview = cli(*command)
    assert preview.returncode == 0, preview.stderr
    assert revision in preview.stdout
    assert snapshot(target) == before
    apply(*command)
    record = json.loads((target / ".agentic-setup/skills.json").read_text())["show-me"]
    assert record["commit"] == revision
    assert ".claude/skills/show-me/SKILL.md" in record["files"]
    assert (target / ".claude/skills/show-me/SKILL.md").read_bytes() == (
        skill / "SKILL.md"
    ).read_bytes()
    assert "No changes" in cli(*command).stdout


def test_update_replaces_unchanged_files_and_preserves_project_additions(tmp_path):
    source, skill, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    extra = target / ".claude/skills/show-me/team.md"
    extra.write_text("Keep team addition\n")
    commit(target, "installed skill and team addition")
    (skill / "SKILL.md").write_text("---\nname: show-me\n---\nUpdated presentation\n")
    (skill / "old.md").unlink()
    (skill / "new.md").write_text("New support\n")
    revision = commit(source, "new upstream revision")
    before = snapshot(target)
    command = ["skills", "update", target, "--from", source, "--bundle", "show-me"]
    preview = cli(*command)
    assert preview.returncode == 0, preview.stderr
    assert snapshot(target) == before
    apply(*command)
    assert not (target / ".claude/skills/show-me/old.md").exists()
    assert (target / ".claude/skills/show-me/new.md").read_text() == "New support\n"
    assert extra.read_text() == "Keep team addition\n"
    assert (target / "app.txt").read_text() == "Project work\n"
    assert (
        json.loads((target / ".agentic-setup/skills.json").read_text())["show-me"][
            "commit"
        ]
        == revision
    )
    assert "No changes" in cli(*command).stdout


def test_default_fetch_resolves_latest_and_pinned_replay(tmp_path, monkeypatch):
    source, _, revision = source_repo(tmp_path)
    target = target_repo(tmp_path)
    # Redirect only the transport URL, using real Git fetch/checkout and no network.
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", f"url.{source.as_uri()}.insteadOf")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "https://github.com/humanlayer/skills.git")
    result = cli("skills", "install", target, "--bundle", "show-me")
    assert result.returncode == 0, result.stderr
    assert revision in result.stdout
    token = result.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = cli(
        "skills",
        "install",
        target,
        "--bundle",
        "show-me",
        "--ref",
        revision,
        "--apply",
        "--expect",
        token,
    )
    assert applied.returncode == 0, applied.stderr
    assert (
        json.loads((target / ".agentic-setup/skills.json").read_text())["show-me"][
            "commit"
        ]
        == revision
    )


@pytest.mark.parametrize("change", ["edit", "delete", "collision"])
def test_update_conflicts_preserve_local_work(tmp_path, change):
    source, skill, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    installed = target / ".claude/skills/show-me/old.md"
    if change == "edit":
        installed.write_text("Local customization\n")
    elif change == "delete":
        installed.unlink()
    else:
        (target / ".claude/skills/show-me/new.md").write_text("Project-owned content\n")
    commit(target, "intentional project customization")
    (skill / "SKILL.md").write_text("---\nname: show-me\n---\nNew upstream\n")
    (skill / "new.md").write_text("Upstream addition\n")
    commit(source, "upstream change")
    before = snapshot(target)
    result = cli(
        "skills",
        "update",
        target,
        "--from",
        source,
        "--bundle",
        "show-me",
        "--apply",
        "--expect",
        "unused",
    )
    assert result.returncode == 1
    assert "CONFLICT" in result.stdout
    assert snapshot(target) == before


@pytest.mark.parametrize("metadata", [".agentic-setup", ".starter"])
def test_legacy_record_can_be_verified_before_update(tmp_path, metadata):
    source, skill, revision = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    if metadata == ".starter":
        (target / ".agentic-setup").rename(target / metadata)
    record = target / metadata / "skills.json"
    record.write_text(
        json.dumps({"show-me": {"source": "humanlayer/skills", "commit": revision}})
    )
    commit(target, "commit-only older installation")
    blocked = cli("skills", "update", target, "--from", source, "--bundle", "show-me")
    assert blocked.returncode == 1 and "no file baseline" in blocked.stdout
    apply(
        "skills",
        "install",
        target,
        "--from",
        source,
        "--bundle",
        "show-me",
        "--ref",
        revision,
    )
    assert "files" in json.loads(record.read_text())["show-me"]
    commit(target, "verified baseline")
    (skill / "old.md").write_text("Updated support\n")
    commit(source, "later upstream")
    apply("skills", "update", target, "--from", source, "--bundle", "show-me")
    assert (target / ".claude/skills/show-me/old.md").read_text() == "Updated support\n"


def test_latest_moving_between_preview_and_apply_requires_new_token(
    tmp_path, monkeypatch
):
    source, skill, revision = source_repo(tmp_path)
    target = target_repo(tmp_path)
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", f"url.{source.as_uri()}.insteadOf")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "https://github.com/humanlayer/skills.git")
    command = ["skills", "install", target, "--bundle", "show-me"]
    preview = cli(*command)
    assert preview.returncode == 0, preview.stderr
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    (skill / "old.md").write_text("Upstream moved\n")
    commit(source, "new latest")
    before = snapshot(target)
    result = cli(*command, "--apply", "--expect", token)
    assert result.returncode == 1 and "Stale preview" in result.stderr
    assert snapshot(target) == before
    pinned = cli(*command, "--ref", revision, "--apply", "--expect", token)
    assert pinned.returncode == 0, pinned.stderr
    assert (target / ".claude/skills/show-me/old.md").read_text() == "Old support\n"


def test_update_refuses_unowned_paths_in_metadata(tmp_path):
    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    record_path = target / ".agentic-setup/skills.json"
    records = json.loads(record_path.read_text())
    records["show-me"]["files"]["app.txt"] = "0" * 64
    record_path.write_text(json.dumps(records))
    commit(target, "invalid metadata")
    before = snapshot(target)
    result = cli(
        "skills",
        "update",
        target,
        "--from",
        source,
        "--bundle",
        "show-me",
        "--apply",
        "--expect",
        "unused",
    )
    assert result.returncode == 1
    assert "Invalid owned file hashes" in result.stderr
    assert snapshot(target) == before


def test_legacy_baseline_verification_refuses_modified_skill(tmp_path):
    source, _, revision = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    (target / ".agentic-setup/skills.json").write_text(
        json.dumps({"show-me": {"source": "humanlayer/skills", "commit": revision}})
    )
    (target / ".claude/skills/show-me/old.md").write_text("Local change\n")
    commit(target, "older customized skill")
    before = snapshot(target)
    result = cli("skills", "install", target, "--from", source, "--bundle", "show-me")
    assert result.returncode == 1
    assert "cannot establish a file baseline" in result.stdout
    assert snapshot(target) == before


def test_update_refuses_legacy_command_name_collision(tmp_path):
    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    (target / ".claude/commands").mkdir()
    (target / ".claude/commands/show-me.md").write_text("Team command\n")
    commit(target, "conflicting local command")
    before = snapshot(target)
    result = cli("skills", "update", target, "--from", source, "--bundle", "show-me")
    assert result.returncode == 1
    assert "command name collision" in result.stdout
    assert snapshot(target) == before
