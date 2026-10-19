"""The public command names describe workspace setup and skill installation."""

import json
import sys

from test_transition import ROOT, run


def test_agentic_initializes_named_metadata_and_groups_skill_installation(tmp_path):
    command = [sys.executable, str(ROOT / "agentic")]
    target = tmp_path / "project"
    result = run(*command, "init", str(target))
    assert result.returncode == 0, result.stderr
    record = json.loads((target / ".agentic-setup/install.json").read_text())
    assert record["source"] == "https://github.com/ZekeT/agentic-setup"
    assert not (target / ".starter").exists()
    assert not (target / "agentic_setup").exists()
    help_result = run(*command, "skills", "install", "--help")
    assert help_result.returncode == 0, help_result.stderr
    assert "--bundle" in help_result.stdout
    assert "--expect" in help_result.stdout


def test_ambiguous_installation_records_are_rejected_without_writes(tmp_path):
    command = [sys.executable, str(ROOT / "agentic")]
    target = tmp_path / "project"
    assert run(*command, "init", str(target)).returncode == 0
    (target / ".starter").mkdir()
    (target / ".starter/skills.json").write_text("{}\n")
    run("git", "init", "-q", cwd=target)
    from test_updates import commit

    commit(target, "conflicting metadata")
    result = run(*command, "adopt", str(target), "--apply", "--expect", "unused")
    assert result.returncode == 1
    assert "Conflicting installation metadata" in result.stderr
    assert not run("git", "status", "--porcelain", cwd=target).stdout
