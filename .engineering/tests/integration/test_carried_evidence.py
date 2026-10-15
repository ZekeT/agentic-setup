"""Carry reviewer evidence through the public verification commands."""

import json

import pytest

from .test_publication import hosting as hosting
from .test_verification import cli, complete, git, prepare
from .test_verification import repo as repo

pytestmark = pytest.mark.integration


def advance_and_rebase(root, changes=None):
    """Commit the proposal, advance main, and replay it onto the new base."""
    git(root, "add", "app.txt")
    git(root, "commit", "--allow-empty", "-m", "proposal")
    git(root, "checkout", "main")
    for name, content in (changes or {"upstream.txt": "unrelated\n"}).items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        git(root, "add", name)
    git(root, "commit", "--allow-empty", "-m", "advance base")
    git(root, "checkout", "feature")
    git(root, "rebase", "main")


def test_clean_rebase_carries_reports_but_requires_fresh_checks(repo):
    old = complete(repo)
    advance_and_rebase(repo)
    current = prepare(repo)
    assert current["snapshot"] != old
    assert current["status"] == "INCOMPLETE"
    assert current["checks"] == []
    assert set(current["reports"]) == {"standards", "spec", "behavioral"}
    for report in current["reports"].values():
        assert report["carried_from"] == old
        assert report["snapshot"] == current["snapshot"]
    history = json.loads((repo / current["previous_evidence"]).read_text())
    assert history["snapshot"] == old
    checked = cli(
        repo, "check", "--change", "example", "--snapshot", current["snapshot"]
    )
    assert checked["status"] == "PASS"
    assert checked["reports"] == current["reports"]
    assert prepare(repo)["status"] == "PASS"


def test_failed_carried_rerun_drops_behavioral_and_stays_failed(repo):
    complete(repo)
    advance_and_rebase(repo, {"Makefile": "check:\n\t@exit 7\n"})
    current = prepare(repo)
    assert "behavioral" in current["reports"]
    failed = cli(
        repo,
        "check",
        "--change",
        "example",
        "--snapshot",
        current["snapshot"],
        status=1,
    )
    assert failed["status"] == "FAIL"
    assert set(failed["reports"]) == {"standards", "spec"}
    assert cli(repo, "status", "--change", "example", status=1)["status"] == "FAIL"


def test_upstream_overlap_with_scope_carries_nothing(repo):
    # Changed plans, probes and scoped content are unit tested at the carry seam;
    # this shows the upstream paths Git reports reach that decision.
    from .test_verification import change_plan

    change_plan(repo, paths=["app.txt", "context.txt"])
    complete(repo)
    advance_and_rebase(repo, {"context.txt": "upstream\n"})
    current = prepare(repo)
    assert current["reports"] == {}
    assert current["status"] == "INCOMPLETE"
    assert current["previous_evidence"]


def test_successive_rebases_preserve_provenance_and_reject_manual_carry(repo):
    old = complete(repo)
    advance_and_rebase(repo)
    first = prepare(repo)
    cli(repo, "check", "--change", "example", "--snapshot", first["snapshot"])
    advance_and_rebase(repo, {"second.txt": "more upstream\n"})
    second = prepare(repo)
    assert second["reports"]["behavioral"]["carried_from"] == first["snapshot"]
    assert first["reports"]["behavioral"]["carried_from"] == old
    path = repo / ".engineering/state/verification/manual.json"
    path.write_text(json.dumps(second["reports"]["behavioral"]))
    error = cli(
        repo,
        "record",
        "--change",
        "example",
        "--report",
        str(path.relative_to(repo)),
        status=1,
    )
    assert "Report fields" in error["error"]


def test_ordinary_check_still_clears_behavioral_report(repo):
    token = complete(repo)
    result = cli(repo, "check", "--change", "example", "--snapshot", token)
    assert result["status"] == "INCOMPLETE"
    assert set(result["reports"]) == {"standards", "spec"}


def test_publication_accepts_carried_pass_and_keeps_remote_base_guard(repo, hosting):
    from .test_publication import STATE, publish, review

    review(repo, hosting)
    advance_and_rebase(repo)
    git(repo, "push", "origin", "main")
    current = prepare(repo)
    cli(repo, "check", "--change", "example", "--snapshot", current["snapshot"])
    acceptance = repo / STATE / "acceptance.json"
    plan = json.loads(acceptance.read_text())
    plan["snapshot"] = current["snapshot"]
    acceptance.write_text(json.dumps(plan))
    publish(repo, "review", "--plan", f"{STATE}/acceptance.json")
    assert publish(repo, "preflight")["status"] == "READY"
    old = git(repo, "rev-parse", "main")
    tree = git(repo, "rev-parse", "main^{tree}")
    new = git(repo, "commit-tree", tree, "-p", old, "-m", "remote moved again")
    git(repo, "push", "origin", f"{new}:main")
    git(repo, "fetch", "origin")
    assert cli(repo, "status", "--change", "example")["status"] == "PASS"
    result = publish(repo, "preflight", status=1)
    assert "moved remotely" in result["error"]


def test_removed_history_folder_requires_fresh_proof(repo):
    import shutil

    complete(repo)
    advance_and_rebase(repo)
    first = prepare(repo)
    cli(repo, "check", "--change", "example", "--snapshot", first["snapshot"])
    advance_and_rebase(repo, {"second.txt": "more upstream\n"})
    second = prepare(repo)
    shutil.rmtree((repo / first["checkout"]).parent)
    assert cli(repo, "status", "--change", "example", status=1)["error"]
    current = prepare(repo)
    assert current["reports"] == {} and current["checks"] == []
    history = json.loads((repo / current["previous_evidence"]).read_text())
    assert history["snapshot"] == second["snapshot"]
