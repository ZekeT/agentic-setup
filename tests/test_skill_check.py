"""Online revision checks exercise real Git transport without changing targets."""

from test_inspection import snapshot
from test_skill_updates import apply, source_repo, target_repo
from test_transition import cli
from test_updates import commit


def redirect(monkeypatch, source):
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", f"url.{source.as_uri()}.insteadOf")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "https://github.com/humanlayer/skills.git")


def test_check_reports_current_then_behind_without_changing_target(
    tmp_path, monkeypatch
):
    source, skill, revision = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    redirect(monkeypatch, source)
    # Dirty local content must remain untouched and not be certified by the check.
    (target / ".claude/skills/show-me/old.md").write_text("Local customization\n")
    before = snapshot(target)
    current = cli("skills", "check", target)
    assert current.returncode == 0, current.stderr + current.stdout
    assert "show-me: current" in current.stdout
    assert revision in current.stdout
    assert "installed contents not verified" in current.stdout
    assert snapshot(target) == before
    (skill / "old.md").write_text("Upstream change\n")
    latest = commit(source, "upstream advanced")
    behind = cli("skills", "check", target, "--bundle", "show-me")
    assert behind.returncode == 0, behind.stderr + behind.stdout
    assert "show-me: behind" in behind.stdout
    assert latest in behind.stdout and revision in behind.stdout
    assert snapshot(target) == before


def test_check_reports_ahead_and_diverged_histories(tmp_path, monkeypatch):
    from test_transition import run

    source, skill, original = source_repo(tmp_path)
    target = target_repo(tmp_path)
    (skill / "old.md").write_text("Installed later revision\n")
    installed = commit(source, "installed later commit")
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    run("git", "branch", "retained", cwd=source)
    run("git", "reset", "--hard", original, cwd=source)
    redirect(monkeypatch, source)
    before = snapshot(target)
    ahead = cli("skills", "check", target)
    assert ahead.returncode == 0, ahead.stderr + ahead.stdout
    assert "show-me: ahead" in ahead.stdout and installed in ahead.stdout
    (skill / "old.md").write_text("Different upstream history\n")
    commit(source, "diverged default branch")
    diverged = cli("skills", "check", target)
    assert diverged.returncode == 0, diverged.stderr + diverged.stdout
    assert "show-me: diverged" in diverged.stdout
    assert snapshot(target) == before


def test_check_supports_legacy_records_and_reports_missing_skill(tmp_path, monkeypatch):
    import json

    source, _, revision = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    (target / ".agentic-setup").rename(target / ".starter")
    (target / ".starter/skills.json").write_text(
        json.dumps({"show-me": {"source": "humanlayer/skills", "commit": revision}})
    )
    redirect(monkeypatch, source)
    before = snapshot(target)
    result = cli("skills", "check", target)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "show-me: current" in result.stdout
    assert snapshot(target) == before
    (target / ".claude/skills/show-me/SKILL.md").unlink()
    before = snapshot(target)
    missing = cli("skills", "check", target)
    assert missing.returncode == 1
    assert "recorded but missing" in missing.stdout
    assert snapshot(target) == before


def test_check_reports_partial_failure_and_bundle_filter(tmp_path, monkeypatch):
    import json

    source, _, revision = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    path = target / ".agentic-setup/skills.json"
    records = json.loads(path.read_text())
    records["tdd"] = {"source": "mattpocock/skills", "commit": revision}
    path.write_text(json.dumps(records))
    tdd = target / ".claude/skills/tdd"
    tdd.mkdir()
    (tdd / "SKILL.md").write_text("---\nname: tdd\n---\n")
    redirect(monkeypatch, source)
    # Allow only local transport; an unredirected source fails without network.
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file")
    before = snapshot(target)
    partial = cli("skills", "check", target)
    assert partial.returncode == 1
    assert "show-me: current" in partial.stdout
    assert "tdd: unknown; upstream check failed" in partial.stdout
    filtered = cli("skills", "check", target, "--bundle", "show-me")
    assert filtered.returncode == 0, filtered.stderr + filtered.stdout
    assert "mattpocock" not in filtered.stdout
    assert snapshot(target) == before


def test_check_does_not_guess_provenance_or_fetch_target_urls(tmp_path, monkeypatch):
    import json

    target = target_repo(tmp_path)
    folder = target / ".claude/skills/show-me"
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text("---\nname: show-me\n---\nProject skill\n")
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file")
    before = snapshot(target)
    unrecorded = cli("skills", "check", target)
    assert unrecorded.returncode == 0
    assert "unrecorded revision" in unrecorded.stdout
    assert "no upstream contacted" in unrecorded.stdout
    assert snapshot(target) == before
    metadata = target / ".agentic-setup"
    metadata.mkdir()
    (metadata / "skills.json").write_text(
        json.dumps({"show-me": {"source": "file:///untrusted", "commit": "0" * 40}})
    )
    before = snapshot(target)
    unknown = cli("skills", "check", target)
    assert unknown.returncode == 1
    assert "unknown source" in unknown.stdout
    assert "no upstream contacted" in unknown.stdout
    assert snapshot(target) == before


def test_check_reports_unavailable_recorded_history(tmp_path, monkeypatch):
    import json

    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    path = target / ".agentic-setup/skills.json"
    records = json.loads(path.read_text())
    records["show-me"]["commit"] = "0" * 40
    path.write_text(json.dumps(records))
    redirect(monkeypatch, source)
    before = snapshot(target)
    result = cli("skills", "check", target)
    assert result.returncode == 1
    assert (
        "show-me: unknown (recorded history unavailable or unrelated)" in result.stdout
    )
    assert snapshot(target) == before


def test_check_rejects_invalid_metadata_and_symlink_paths(tmp_path, monkeypatch):
    import json

    target = target_repo(tmp_path)
    metadata = target / ".agentic-setup"
    metadata.mkdir()
    path = metadata / "skills.json"
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "file")
    path.write_text(
        '{"show-me": {"source": "humanlayer/skills", "commit": "--upload-pack=bad"}}'
    )
    before = snapshot(target)
    invalid = cli("skills", "check", target)
    assert invalid.returncode == 1
    assert "invalid recorded commit" in invalid.stdout
    assert "no upstream contacted" in invalid.stdout
    assert snapshot(target) == before
    path.write_text(json.dumps(["not a metadata object"]))
    before = snapshot(target)
    malformed = cli("skills", "check", target)
    assert malformed.returncode == 1
    assert "Skill metadata must be an object" in malformed.stderr
    assert snapshot(target) == before
    path.unlink()
    outside = tmp_path / "outside.json"
    outside.write_text("{}")
    path.symlink_to(outside)
    before = snapshot(target)
    symlink = cli("skills", "check", target)
    assert symlink.returncode == 1 and "Symlink refused" in symlink.stderr
    assert snapshot(target) == before


def test_check_reports_duplicate_recorded_skill(tmp_path, monkeypatch):
    source, _, _ = source_repo(tmp_path)
    target = target_repo(tmp_path)
    apply("skills", "install", target, "--from", source, "--bundle", "show-me")
    duplicate = target / ".agents/skills/show-me"
    duplicate.mkdir(parents=True)
    (duplicate / "SKILL.md").write_text("---\nname: show-me\n---\nTeam copy\n")
    redirect(monkeypatch, source)
    before = snapshot(target)
    result = cli("skills", "check", target)
    assert result.returncode == 1
    assert "duplicate installed locations" in result.stdout
    assert snapshot(target) == before
