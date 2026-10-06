"""Publish the exact presented draft without replacing it or reusing old approval."""

import json

import pytest

from .test_publication import PR_BODY, STATE, publish, review
from .test_publication import hosting as hosting
from .test_verification import git
from .test_verification import repo as repo

pytestmark = pytest.mark.integration


def test_body_file_is_captured_and_published_verbatim(repo, hosting):
    review(repo, hosting)
    path = repo / STATE / "acceptance.json"
    plan = json.loads(path.read_text())
    del plan["pr_body"]
    path.write_text(json.dumps(plan))
    draft = repo / STATE / "pr.md"
    content = PR_BODY + "\nLiteral: `$(not-a-command)` • café\n"
    draft.write_bytes(content.encode("utf-8"))
    publish(
        repo,
        "review",
        "--plan",
        f"{STATE}/acceptance.json",
        "--body-file",
        f"{STATE}/pr.md",
    )
    # The presented bytes are stored; later draft edits cannot silently publish.
    draft.write_text("unpresented replacement")
    publish(repo, "run", "--authorize", "pr")
    receipt = json.loads((repo / STATE / "created.json").read_text())
    assert receipt["body"] == content


def test_missing_body_stops_before_git_mutation_but_allows_commit(repo, hosting):
    review(repo, hosting)
    path = repo / STATE / "acceptance.json"
    plan = json.loads(path.read_text())
    del plan["pr_body"]
    path.write_text(json.dumps(plan))
    publish(repo, "review", "--plan", f"{STATE}/acceptance.json")
    head = git(repo, "rev-parse", "HEAD")
    result = publish(repo, "run", "--authorize", "pr", status=1)
    assert "Missing PR body" in result["error"]
    assert git(repo, "rev-parse", "HEAD") == head
    assert git(hosting[0], "branch", "--list", "feature") == ""
    assert not (repo / STATE / "created.json").exists()
    assert publish(repo, "run", "--authorize", "commit")["status"] == "COMPLETE"


def test_changed_presented_body_requires_new_authorization(repo, hosting):
    review(repo, hosting)
    publish(repo, "run", "--authorize", "push")
    path = repo / STATE / "acceptance.json"
    plan = json.loads(path.read_text())
    plan["pr_body"] += "\nNew disclosure.\n"
    path.write_text(json.dumps(plan))
    publish(repo, "review", "--plan", f"{STATE}/acceptance.json")
    result = publish(repo, "run", status=1)
    assert "Missing human authorization" in result["error"]
    assert not (repo / STATE / "created.json").exists()


@pytest.mark.parametrize("value", ["", "  \n", None, 42, "text\x00text"])
def test_invalid_body_rejected(value):
    from engineering.publication import validate_review

    plan = dict.fromkeys(
        ("snapshot", "summary", "branch", "remote", "remote_url", "base", "title"),
        "fixture",
    )
    plan.update(blockers=[], provider="github", pr_body=value)
    with pytest.raises(ValueError, match="pr_body"):
        validate_review(plan)
