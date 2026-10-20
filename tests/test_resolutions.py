"""Explicit resolution plans are validated and applied through the public CLI."""

import hashlib
import json

from test_inspection import snapshot
from test_transition import cli, legacy
from test_updates import commit


def write_plan(folder, target, operations):
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "resolutions.json"
    path.write_text(
        json.dumps(
            {"version": 1, "target": str(target.resolve()), "operations": operations}
        )
    )
    return path


def operation(target, name, action, **fields):
    p = target / name
    return {
        "path": name,
        "action": action,
        "reason": "Explicit project decision",
        "expected_sha256": hashlib.sha256(p.read_bytes()).hexdigest()
        if p.exists()
        else None,
        **fields,
    }


def test_resolved_delete_and_ignored_json_edit_preview_then_apply(tmp_path):
    target = legacy(tmp_path)
    reviewer = ".claude/agents/security-reviewer.md"
    (target / reviewer).write_text(
        (target / reviewer).read_text() + "\nTeam security guidance\n"
    )
    commit(target, "custom reviewer")
    settings = ".claude/settings.local.json"
    (target / settings).write_text(
        json.dumps(
            {
                "permissions": {
                    "allow": ["Bash(./engineering publish *)", "Bash(make test)"]
                },
                "hooks": {"keep": True},
            }
        )
    )
    folder = tmp_path / "migration"
    plan = write_plan(
        folder,
        target,
        [
            operation(target, reviewer, "delete"),
            operation(
                target,
                settings,
                "json_remove",
                pointer=["permissions", "allow"],
                value="Bash(./engineering publish *)",
            ),
        ],
    )
    before = snapshot(target)
    args = ["adopt", target, "--minimal", "--resolutions", plan]
    preview = cli(*args, "--html", folder / "preview.html")
    assert preview.returncode == 0, preview.stderr + preview.stdout
    assert "RESOLVE" in preview.stdout and "RECOVERY" in preview.stdout
    assert snapshot(target) == before
    assert not (folder / "backups").exists()
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = cli(*args, "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr + applied.stdout
    assert not (target / reviewer).exists()
    assert json.loads((target / settings).read_text()) == {
        "permissions": {"allow": ["Bash(make test)"]},
        "hooks": {"keep": True},
    }
    saved = folder / "backups" / token
    assert (saved / "before" / reviewer).is_file()
    assert b"engineering publish" in (saved / "before" / settings).read_bytes()
    assert (saved / "manifest.json").is_file()


def test_automatic_html_names_live_beside_resolution_file(tmp_path):
    target = legacy(tmp_path)
    folder = tmp_path / "migrations" / target.name
    name = ".claude/agents/security-reviewer.md"
    path = write_plan(folder, target, [operation(target, name, "delete")])
    before = snapshot(target)
    for number in (1, 2):
        preview = cli("adopt", target, "--minimal", "--resolutions", path, "--html")
        assert preview.returncode == 0, preview.stderr + preview.stdout
        report = folder / f"preview-{number:03}.html"
        assert report.exists() and "Project resolutions" in report.read_text()
    assert snapshot(target) == before


def test_text_and_replacement_overrides_preserve_exact_project_choices(tmp_path):
    target = legacy(tmp_path)
    folder = tmp_path / "migration"
    folder.mkdir()
    name = "docs/agents/issue-tracker.md"
    (folder / "tracker.md").write_bytes((target / name).read_bytes())
    path = write_plan(
        folder,
        target,
        [
            operation(
                target,
                "CLAUDE.md",
                "replace_text",
                old="Team rule: retain audit logs.",
                new="Team rule: keep audit logs for seven years.",
            ),
            operation(target, name, "replace_file", replacement="tracker.md"),
        ],
    )
    before = snapshot(target)
    preview = cli("adopt", target, "--minimal", "--resolutions", path, "--html")
    assert preview.returncode == 0, preview.stderr + preview.stdout
    assert "UPDATE docs/agents/issue-tracker.md:" not in preview.stdout
    html = (folder / "preview-001.html").read_text()
    assert "keep audit logs for seven years" in html
    assert snapshot(target) == before


def test_changed_resolution_and_replacement_reject_old_apply_token(tmp_path):
    target = legacy(tmp_path)
    folder = tmp_path / "migration"
    folder.mkdir()
    replacement = folder / "makefile"
    replacement.write_text("check:\n\tpython -m pytest\n")
    path = write_plan(
        folder,
        target,
        [operation(target, "Makefile", "replace_file", replacement="makefile")],
    )
    args = ["adopt", target, "--minimal", "--resolutions", path]
    preview = cli(*args)
    assert preview.returncode == 0, preview.stderr + preview.stdout
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    before = snapshot(target)
    replacement.write_text("check:\n\tpython -m pytest -q\n")
    stale = cli(*args, "--apply", "--expect", token)
    assert stale.returncode == 1 and "Stale preview" in stale.stderr
    replacement.write_text("check:\n\tpython -m pytest\n")
    document = json.loads(path.read_text())
    document["operations"][0]["reason"] = "A different approval rationale"
    path.write_text(json.dumps(document))
    stale = cli(*args, "--apply", "--expect", token)
    assert stale.returncode == 1 and "Stale preview" in stale.stderr
    assert not (folder / "backups").exists()
    assert snapshot(target) == before


def test_resolution_cannot_hide_remaining_active_wiring(tmp_path):
    target = legacy(tmp_path)
    folder = tmp_path / "migration"
    folder.mkdir()
    (folder / "bad.md").write_text(
        "Read .engineering/docs/verification.md and run engineering verify check.\n"
    )
    path = write_plan(
        folder,
        target,
        [operation(target, "CLAUDE.md", "replace_file", replacement="bad.md")],
    )
    before = snapshot(target)
    result = cli("adopt", target, "--minimal", "--resolutions", path, "--html")
    assert result.returncode == 1
    assert "active retired wiring remains" in result.stdout
    assert "Blocked" in (folder / "preview-001.html").read_text()
    assert snapshot(target) == before


def test_stale_hash_ambiguous_text_and_dirty_tracked_edits_block(tmp_path):
    target = legacy(tmp_path)
    folder = tmp_path / "migration"
    name = "CLAUDE.md"
    op = operation(
        target,
        name,
        "replace_text",
        old="Team rule: retain audit logs.",
        new="Updated team rule.",
    )
    op["expected_sha256"] = "0" * 64
    path = write_plan(folder, target, [op])
    before = snapshot(target)
    stale = cli("adopt", target, "--minimal", "--resolutions", path)
    assert stale.returncode == 1 and "Stale resolution" in stale.stderr
    op = operation(target, name, "replace_text", old="absent text", new="new text")
    write_plan(folder, target, [op])
    ambiguous = cli("adopt", target, "--minimal", "--resolutions", path)
    assert ambiguous.returncode == 1 and "exactly once" in ambiguous.stderr
    assert snapshot(target) == before
    policy = target / name
    policy.write_text(policy.read_text() + "\nUncommitted team choice.\n")
    write_plan(
        folder,
        target,
        [
            operation(
                target,
                name,
                "replace_text",
                old="Uncommitted team choice.",
                new="Revised team choice.",
            )
        ],
    )
    before = snapshot(target)
    preview = cli("adopt", target, "--minimal", "--resolutions", path)
    assert preview.returncode == 0, preview.stderr + preview.stdout
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    apply = cli(
        "adopt",
        target,
        "--minimal",
        "--resolutions",
        path,
        "--apply",
        "--expect",
        token,
    )
    assert apply.returncode == 1 and "Commit affected local edits" in apply.stderr
    assert snapshot(target) == before


def test_recovery_failure_prevents_all_target_writes(tmp_path):
    target = legacy(tmp_path)
    folder = tmp_path / "migration"
    path = write_plan(
        folder,
        target,
        [operation(target, ".claude/agents/security-reviewer.md", "delete")],
    )
    args = ["adopt", target, "--minimal", "--resolutions", path]
    preview = cli(*args)
    assert preview.returncode == 0, preview.stderr + preview.stdout
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    (folder / "backups").write_text("Prevent creating a recovery directory")
    before = snapshot(target)
    result = cli(*args, "--apply", "--expect", token)
    assert result.returncode == 1
    assert snapshot(target) == before


def test_invalid_resolution_inputs_do_not_change_target(tmp_path):
    target = legacy(tmp_path)
    folder = tmp_path / "migration"
    good = operation(target, ".claude/agents/security-reviewer.md", "delete")
    path = write_plan(folder, target, [good])
    before = snapshot(target)
    invalid_operations = [
        [{**good, "action": "shell", "command": "touch app.js"}],
        [good, good],
        [{**good, "path": "../outside"}],
        [{**good, "path": ".git/config"}],
        [{**good, "path": ".env"}],
        [{**good, "path": "src/app.js"}],
        [{**good, "reason": ""}],
        [{**good, "ignore_conflicts": True}],
        [operation(target, "CLAUDE.md", "replace_file", replacement="../outside")],
    ]
    for ops in invalid_operations:
        write_plan(folder, target, ops)
        result = cli("adopt", target, "--minimal", "--resolutions", path)
        assert result.returncode == 1, ops
        assert snapshot(target) == before
    document = {"version": 1, "target": "/another/workspace", "operations": [good]}
    path.write_text(json.dumps(document))
    wrong = cli("adopt", target, "--minimal", "--resolutions", path)
    assert wrong.returncode == 1 and "target does not match" in wrong.stderr
    link = folder / "linked.json"
    link.symlink_to(path)
    result = cli("adopt", target, "--minimal", "--resolutions", link)
    assert result.returncode == 1 and "Symlink refused" in result.stderr
    assert snapshot(target) == before


def test_json_removal_distinguishes_boolean_and_number(tmp_path):
    target = legacy(tmp_path)
    name = ".claude/settings.local.json"
    (target / name).write_text('{"values": [1, true], "preserve": "team"}')
    folder = tmp_path / "migration"
    path = write_plan(
        folder,
        target,
        [operation(target, name, "json_remove", pointer=["values"], value=True)],
    )
    args = ["adopt", target, "--minimal", "--resolutions", path]
    preview = cli(*args)
    assert preview.returncode == 0, preview.stderr + preview.stdout
    token = preview.stdout.split("PREVIEW ")[1].splitlines()[0]
    applied = cli(*args, "--apply", "--expect", token)
    assert applied.returncode == 0, applied.stderr + applied.stdout
    assert (json.loads((target / name).read_text())) == {
        "values": [1],
        "preserve": "team",
    }


def test_in_target_plan_and_linked_replacement_are_refused(tmp_path):
    target = legacy(tmp_path)
    op = operation(target, ".claude/agents/security-reviewer.md", "delete")
    local_plan = write_plan(target / "migration", target, [op])
    before = snapshot(target)
    result = cli("adopt", target, "--minimal", "--resolutions", local_plan, "--html")
    assert result.returncode == 1 and "outside the target" in result.stderr
    assert snapshot(target) == before
    folder = tmp_path / "migration"
    folder.mkdir()
    (folder / "linked.md").symlink_to(target / "CLAUDE.md")
    path = write_plan(
        folder,
        target,
        [operation(target, "CLAUDE.md", "replace_file", replacement="linked.md")],
    )
    result = cli("adopt", target, "--minimal", "--resolutions", path)
    assert result.returncode == 1 and "Symlink refused" in result.stderr
    assert snapshot(target) == before


def test_auto_report_without_plan_uses_setup_workspace_folder(tmp_path):
    import shutil
    import sys

    from test_transition import ROOT, run

    target = legacy(tmp_path)
    setup = tmp_path / "setup"
    setup.mkdir()
    shutil.copytree(
        ROOT / "agentic_setup",
        setup / "agentic_setup",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy(ROOT / "agentic", setup / "agentic")
    before = snapshot(target)
    report = run(
        sys.executable,
        str(setup / "agentic"),
        "adopt",
        str(target),
        "--minimal",
        "--html",
        cwd=tmp_path,
    )
    assert report.returncode == 0, report.stderr + report.stdout
    assert (setup / "migrations" / target.name / "preview-001.html").is_file()
    assert not (tmp_path / "migrations").exists()
    assert snapshot(target) == before
