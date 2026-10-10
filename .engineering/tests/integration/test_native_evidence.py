"""Native semantic evidence binds the actual committed review to captured content."""

from __future__ import annotations

import json

import pytest

from .test_publication import hosting as hosting
from .test_verification import cli, git, prepare
from .test_verification import repo as repo

pytestmark = pytest.mark.integration


def native_report(repo, token, role, *, status=0, **identity):
    report = {
        "snapshot": token,
        "role": role,
        "reviewer": f"native-{role}",
        "independent": True,
        "verdict": "PASS",
        "summary": "Native review of fixture requirement",
        "findings": [],
        "coverage_gaps": [],
        "reviewed_commit": git(repo, "rev-parse", "HEAD"),
        "comparison_base": git(repo, "rev-parse", "main"),
        **identity,
    }
    path = repo / ".engineering/state/verification/native.json"
    path.write_text(json.dumps(report))
    return cli(
        repo,
        "record",
        "--change",
        "example",
        "--report",
        str(path.relative_to(repo)),
        status=status,
    )


def test_native_axes_require_checkpoint_and_remain_distinct(repo):
    token = prepare(repo)["snapshot"]
    refused = native_report(repo, token, "standards", status=1)
    assert "checkpoint" in refused["error"]
    git(repo, "add", "app.txt")
    git(repo, "commit", "-m", "scoped checkpoint")
    native_report(repo, token, "standards")
    result = cli(repo, "status", "--change", "example", status=1)
    assert result["missing_roles"] == ["spec", "behavioral"]
    native_report(repo, token, "spec")
    cli(repo, "check", "--change", "example", "--snapshot", token)
    from .test_verification import report

    report(repo, token, "behavioral")
    assert cli(repo, "status", "--change", "example")["status"] == "PASS"
    (repo / "app.txt").write_text("uncovered correction\n")
    assert cli(repo, "status", "--change", "example", status=1)["status"] == "STALE"


def test_checks_leave_capture_immutable_even_when_command_mutates(repo):
    from .test_verification import change_plan

    (repo / "Makefile").write_text("check:\n\t@echo mutation >> app.txt\n")
    change_plan(repo, paths=["app.txt", "Makefile"], tier="sensitive")
    prepared = prepare(repo)
    result = cli(
        repo,
        "check",
        "--change",
        "example",
        "--snapshot",
        prepared["snapshot"],
        status=1,
    )
    assert "mutated" in result["error"]
    assert (repo / prepared["checkout"] / "app.txt").read_text() == "after\n"
    assert (repo / "app.txt").read_text() == "after\n"
    assert (
        cli(repo, "status", "--change", "example", status=1)["status"] == "INCOMPLETE"
    )
    assert prepare(repo)["status"] == "INCOMPLETE"


@pytest.mark.parametrize("edit", ["addition", "deletion", "mode"])
def test_checkpoint_must_cover_every_content_change(repo, edit):
    from .test_verification import change_plan

    git(repo, "add", "app.txt")
    git(repo, "commit", "-m", "initial checkpoint")
    paths = ["app.txt"]
    if edit == "addition":
        (repo / "new.txt").write_text("intended addition\n")
        paths.append("new.txt")
    elif edit == "deletion":
        (repo / "app.txt").unlink()
    else:
        (repo / "app.txt").chmod(0o755)
    change_plan(repo, paths=paths)
    token = prepare(repo)["snapshot"]
    assert "checkpoint" in native_report(repo, token, "standards", status=1)["error"]
    git(repo, "add", "--", *paths)
    git(repo, "commit", "-m", "complete checkpoint")
    native_report(repo, token, "standards")
    native_report(repo, token, "spec")


def test_old_contract_is_history_and_future_contract_needs_recovery(repo):
    from .test_verification import complete

    complete(repo)
    path = repo / ".engineering/state/verification/example.json"
    old = json.loads(path.read_text())
    old["schema_version"] = 2
    old["reports"] = {"maintainability": {"verdict": "PASS"}}
    path.write_text(json.dumps(old))
    assert (
        "prepare again" in cli(repo, "status", "--change", "example", status=1)["error"]
    )
    current = prepare(repo)
    assert current["reports"] == {} and current["checks"] == []
    assert json.loads((repo / current["previous_evidence"]).read_text()) == old
    future = {**old, "schema_version": 999}
    path.write_text(json.dumps(future))
    assert "compatible tooling" in prepare(repo, status=1)["error"]
    assert json.loads(path.read_text()) == future


def test_concurrent_writer_is_refused_without_losing_evidence(repo):
    import fcntl

    prepare(repo)
    path = repo / ".engineering/state/verification/example.json"
    before = path.read_bytes()
    with path.with_suffix(".json.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert "serialize" in prepare(repo, status=1)["error"]
    assert path.read_bytes() == before


def test_native_comparison_and_commit_are_checked(repo):
    git(repo, "add", "app.txt")
    git(repo, "commit", "-m", "checkpoint")
    token = prepare(repo)["snapshot"]
    head = git(repo, "rev-parse", "HEAD")
    assert (
        "comparison"
        in native_report(repo, token, "spec", comparison_base=head, status=1)["error"]
    )
    assert (
        "checkpoint"
        in native_report(
            repo,
            token,
            "standards",
            reviewed_commit=git(repo, "rev-parse", "main"),
            status=1,
        )["error"]
    )


def test_publication_consumes_one_suite_and_both_native_axes(repo, hosting):
    from .test_publication import PR_BODY, STATE, publish
    from .test_verification import change_plan, report

    (repo / "Makefile").write_text(f"check:\n\t@echo executed >> {STATE}/calls\n")
    change_plan(repo, paths=["app.txt", "Makefile"], tier="sensitive")
    git(repo, "add", "app.txt", "Makefile")
    git(repo, "commit", "-m", "ordinary scoped checkpoint")
    prepared = prepare(repo)
    token = prepared["snapshot"]
    checked = cli(repo, "check", "--change", "example", "--snapshot", token)
    native_report(repo, token, "standards")
    native_report(repo, token, "spec")
    report(repo, token, "behavioral")
    assert cli(repo, "status", "--change", "example", status=1)["missing_roles"] == [
        "security"
    ]
    report(repo, token, "security")
    plan = {
        "snapshot": token,
        "summary": "Fixture native review journey",
        "blockers": [],
        "branch": "feature",
        "remote": "origin",
        "remote_url": str(hosting[0]),
        "base": "main",
        "provider": hosting[1],
        "title": "Native reviewed change",
        "pr_body": PR_BODY,
    }
    (repo / STATE / "acceptance.json").write_text(json.dumps(plan))
    publish(repo, "review", "--plan", f"{STATE}/acceptance.json")
    (repo / "app.txt").write_text("uncovered\n")
    assert publish(repo, "run", "--authorize", "pr", status=1)["status"] == "STOPPED"
    (repo / "app.txt").write_text("after\n")
    assert publish(repo, "run", "--authorize", "pr")["status"] == "PUBLISHED"
    assert publish(repo, "run")["status"] == "PUBLISHED"
    assert (
        repo / checked["check_checkout"] / STATE / "calls"
    ).read_text() == "executed\n"
    assert not (repo / prepared["checkout"] / STATE / "calls").exists()
    assert json.loads((repo / STATE / "created.json").read_text())["body"] == PR_BODY


def test_unavailable_reviewed_commit_is_history_not_proof(repo):
    from .test_verification import complete

    complete(repo)
    path = repo / ".engineering/state/verification/example.json"
    old = json.loads(path.read_text())
    git(repo, "commit", "--amend", "--allow-empty", "-m", "reworded checkpoint")
    git(repo, "reflog", "expire", "--expire=now", "--all")
    git(repo, "gc", "--prune=now", "--quiet")
    assert (
        "prepare again" in cli(repo, "status", "--change", "example", status=1)["error"]
    )
    current = prepare(repo)
    assert current["reports"] == {} and current["checks"] == []
    assert "commit is unavailable" in current["history_note"]
    assert current["checkout"] != old["checkout"]
    assert json.loads((repo / current["previous_evidence"]).read_text()) == old


def test_unrelated_comparison_history_is_not_reused(repo):
    from .test_verification import complete

    complete(repo)
    git(repo, "checkout", "--orphan", "unrelated")
    git(repo, "commit", "--allow-empty", "-m", "unrelated root")
    orphan = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-f", "feature")
    path = repo / ".engineering/state/verification/example.json"
    record = json.loads(path.read_text())
    record["reports"]["spec"]["comparison_base"] = orphan
    path.write_text(json.dumps(record))
    current = prepare(repo)
    assert current["reports"] == {} and current["checks"] == []
    assert "not reused" in current["history_note"]
