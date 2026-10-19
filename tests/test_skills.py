"""Installed exposed names own their command even in a renamed directory."""

from test_transition import run
from test_updates import commit

from agentic_setup.skills import BUNDLES, plan_skills


def test_existing_exposed_name_prevents_second_tdd(tmp_path, monkeypatch):
    upstream = tmp_path / "upstream"
    (upstream / "skills/tdd").mkdir(parents=True)
    (upstream / "skills/tdd/SKILL.md").write_text("---\nname: tdd\n---\nUpstream TDD\n")
    run("git", "init", "-q", cwd=upstream)
    revision = commit(upstream, "skill source")
    monkeypatch.setitem(BUNDLES, "fixture", ("fixture/skills", revision, ["tdd"]))
    target = tmp_path / "target"
    existing = target / ".claude/skills/team-testing/SKILL.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("---\nname: tdd\n---\nTeam TDD\n")
    run("git", "init", "-q", cwd=target)
    commit(target, "existing renamed skill")
    plan = plan_skills(target, upstream, "fixture")
    assert not any(name.startswith(".claude/skills/tdd/") for name in plan.changes)
    assert any("PRESERVE skill tdd" in note for note in plan.notes)
    assert existing.read_text() == "---\nname: tdd\n---\nTeam TDD\n"
