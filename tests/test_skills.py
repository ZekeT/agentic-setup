"""Skill staging refuses ambiguous ownership and unsafe filesystem structures."""

import json

import pytest
from skill_support import saved_plan, source_repo, target_repo
from test_transition import cli


@pytest.mark.parametrize(
    "case", ["renamed", "command", "duplicate", "symlink", "secret", "bad-lock"]
)
def test_unsafe_or_ambiguous_installation_is_refused(tmp_path, installer, case):
    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    folder = target / ".claude/skills/show-me"
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text("---\nname: show-me\n---\nTeam version")
    if case == "renamed":
        folder.rename(folder.parent / "renamed")
    elif case == "command":
        commands = target / ".claude/commands"
        commands.mkdir()
        (commands / "show-me.md").write_text("Team command")
    elif case == "duplicate":
        other = target / ".agents/skills/show-me"
        other.mkdir(parents=True)
        (other / "SKILL.md").write_text("---\nname: show-me\n---\nSecond copy")
    elif case == "symlink":
        (folder / "support").symlink_to(tmp_path)
    elif case == "secret":
        (folder / ".env").write_text("fixture secret")
    else:
        (target / "skills-lock.json").write_text('{"version":99,"skills":{}}')
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
    )
    assert result.returncode != 0
    assert not (tmp_path / "plan.json").exists()
    assert not (target / "skills-lock.json").exists() or case == "bad-lock"


def test_tampered_scope_is_refused_even_with_recomputed_token(tmp_path, installer):
    import hashlib

    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    plan, _ = saved_plan(
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
    doc = json.loads(plan.read_text())
    doc["after"]["app.txt"] = {"kind": "absent"}
    raw = (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode()
    plan.write_bytes(raw)
    result = cli(
        "skills",
        "install",
        target,
        "--plan",
        plan,
        "--apply",
        "--expect",
        hashlib.sha256(raw).hexdigest(),
    )
    assert result.returncode != 0 and "scope" in result.stderr
    assert (target / "app.txt").read_text() == "Keep application\n"


def test_apply_requires_saved_plan_and_preview_cannot_write_inside_target(
    tmp_path, installer
):
    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    result = cli("skills", "install", target, "--apply", "--expect", "anything")
    assert result.returncode != 0 and "--plan" in result.stderr
    result = cli(
        "skills",
        "install",
        target,
        "--from",
        source,
        "--bundle",
        "show-me",
        "--plan",
        target / "plan.json",
    )
    assert result.returncode != 0
    assert not (target / "plan.json").exists()


@pytest.mark.parametrize("name", ["support.md", "SKILL.md", "linked-directory"])
def test_local_source_symlinks_are_rejected_before_installer(tmp_path, installer, name):
    from test_updates import commit

    source, skill, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    outside = tmp_path / "private-fixture"
    outside.mkdir()
    secret = outside / "secret.txt"
    secret.write_text("Disposable secret fixture")
    link = skill / name
    if link.exists():
        link.unlink()
    link.symlink_to(outside if name == "linked-directory" else secret)
    commit(source, "linked source")
    marker = tmp_path / "installer-called"
    installer.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 1\n")
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
    )
    assert result.returncode != 0 and "symlink" in result.stderr.lower()
    assert not marker.exists()
    assert not (tmp_path / "plan.json").exists()
    assert not (target / "skills-lock.json").exists()
