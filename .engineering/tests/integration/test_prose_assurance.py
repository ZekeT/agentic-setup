"""Prose-only documentation routes to documentation checks; other content does not."""

import json
import subprocess
import sys

import pytest
from engineering.verification_requirements import DOCS

from .test_publication import STATE, publish, review
from .test_publication import hosting as hosting
from .test_review_tiers import CONFIG, settings_text
from .test_verification import TOOLING, change_plan, cli, git, prepare, report
from .test_verification import repo as repo
from .test_verification_requirements import CHECK, consumers, edit
from .test_verification_requirements import prepare as prepare_paths
from .test_verification_requirements import pristine as pristine
from .test_verification_requirements import project as project

pytestmark = pytest.mark.integration

GUIDE = (
    "# Guide\n\n"
    "Install the tool before use.\n\n"
    "```bash\nmake install\n```\n\n"
    "See [setup](#guide) and `make check`.\n\n"
    "- First step.\n\n> Note well.\n"
)


def launcher(root):
    """A committed launcher running the tooling under test from the checkout."""
    path = root / "engineering"
    path.write_text(
        f'#!/bin/sh\nexec "{sys.executable}" -c '
        '"from engineering.cli import main; raise SystemExit(main())" '
        '--root "$PWD" "$@"\n'
    )
    path.chmod(0o755)


@pytest.fixture
def documented(repo):
    """README is configured documentation and has a committed fenced example."""
    git(repo, "checkout", "--quiet", "main")
    launcher(repo)
    (repo / "README.md").write_text(GUIDE)
    (repo / CONFIG).write_text(settings_text(["README.md", "docs/**"]))
    git(repo, "add", ".")
    git(repo, "commit", "--quiet", "-m", "documented")
    git(repo, "checkout", "--quiet", "feature")
    git(repo, "merge", "--quiet", "--ff-only", "main")
    (repo / "app.txt").write_text("before\n")
    return repo


def requirements(root):
    record = root / STATE / "example.json"
    return json.loads(record.read_text())["requirements"]


def correct_prose(root):
    text = (root / "README.md").read_text()
    (root / "README.md").write_text(text.replace("before use", "before first use"))


def test_prose_beside_unchanged_example_needs_only_documentation_checks(documented):
    correct_prose(documented)
    change_plan(documented, paths=["README.md"], tier="documentation", checks=[CHECK])
    error = prepare(documented, status=1)["error"]
    assert "Required checks missing" in error and "docs-check" in error
    change_plan(documented, checks=[[*DOCS, "README.md"]])
    result = prepare(documented)
    assert result["floor"] == "documentation"
    assert result["required_roles"] == ["behavioral"]
    assert requirements(documented)["checks"] == [[*DOCS, "README.md"]]


def edit_readme(root, old, new):
    text = (root / "README.md").read_text()
    assert old in text
    (root / "README.md").write_text(text.replace(old, new, 1))


def plan_prose(root, name="README.md", tier="documentation"):
    change_plan(root, paths=[name], tier=tier, checks=[[*DOCS, name]])


def test_markdown_file_type_decides_prose_not_content(documented):
    # User decision 2026-10-14: configured Markdown files are prose by type.
    # Requirement facts hold no content, so one edited example shows it.
    edit_readme(documented, "make install\n", "make install --all\n")
    plan_prose(documented)
    result = prepare(documented)
    assert result["floor"] == "documentation"
    assert requirements(documented)["checks"] == [[*DOCS, "README.md"]]


@pytest.mark.parametrize(
    "change,reason",
    [
        ("delete", "deleted document"),
        ("mode", "executable file"),
        ("base-executable", "executable file"),
    ],
)
def test_non_prose_files_take_the_stricter_route(documented, change, reason):
    name = "README.md"
    if change == "delete":
        (documented / name).unlink()
    elif change == "mode":
        (documented / name).chmod(0o755)
    elif change == "base-executable":
        git(documented, "checkout", "--quiet", "main")
        (documented / name).chmod(0o755)
        git(documented, "commit", "--quiet", "-am", "executable readme")
        git(documented, "checkout", "--quiet", "feature")
        git(documented, "merge", "--quiet", "--ff-only", "main")
        correct_prose(documented)
    change_plan(documented, paths=[name], tier="documentation", checks=[CHECK])
    error = prepare(documented, status=1)["error"]
    assert f"{name} ({reason})" in error
    # The stricter route requires the application suite, not documentation checks.
    change_plan(documented, tier="ordinary", checks=[[*DOCS, name]])
    assert "Required checks missing" in prepare(documented, status=1)["error"]
    change_plan(documented, checks=[CHECK])
    prepare(documented)
    assert requirements(documented)["paths"]["ordinary"] == {name: reason}


def test_non_utf8_markdown_cannot_pass_the_documentation_check(documented):
    (documented / "README.md").write_bytes(b"# Guide\n\xff\n")
    plan_prose(documented)
    token = prepare(documented)["snapshot"]
    result = cli(
        documented, "check", "--change", "example", "--snapshot", token, status=1
    )
    assert result["status"] == "FAIL"
    assert "UTF-8" in result["checks"][0]["stderr"]


@consumers
def test_consumer_prose_check_runs_through_the_installed_launcher(project):
    edit(project, "README.md")
    checks = [[*DOCS, "README.md"]]
    token = prepare_paths(project, ["README.md"], checks, tier="documentation")[
        "snapshot"
    ]
    result = cli(project, "check", "--change", "example", "--snapshot", token)
    assert [item["exit_code"] for item in result["checks"]] == [0]
    report(project, token, "behavioral")
    assert cli(project, "status", "--change", "example")["status"] == "PASS"


def test_prose_correction_publishes_and_requires_documentation_proof(
    documented, hosting
):
    calls = documented / STATE / "calls"
    git(documented, "checkout", "--quiet", "main")
    (documented / "Makefile").write_text(f"check:\n\techo check >> {calls}\n")
    git(documented, "commit", "--quiet", "-am", "count application suite runs")
    git(documented, "push", "--quiet", "origin", "main")
    git(documented, "checkout", "--quiet", "feature")
    git(documented, "merge", "--quiet", "--ff-only", "main")
    correct_prose(documented)
    change_plan(
        documented,
        paths=["README.md"],
        tier="documentation",
        checks=[[*DOCS, "README.md"]],
    )
    token = prepare(documented)["snapshot"]
    # Without the documentation check and review there is no proof to publish.
    plan = {
        "snapshot": token,
        "summary": "Correct README prose.",
        "blockers": [],
        "branch": "feature",
        "remote": "origin",
        "remote_url": str(hosting[0]),
        "base": "main",
        "provider": hosting[1],
        "title": "docs: correct README prose",
        "pr_body": "## Summary\n\nProse correction.\n",
    }
    (documented / STATE / "acceptance.json").write_text(json.dumps(plan))
    status = cli(documented, "status", "--change", "example", status=1)
    assert status["missing"] == ["behavioral", "authoritative checks"]
    result = publish(
        documented, "review", "--plan", f"{STATE}/acceptance.json", status=1
    )
    assert result["status"] == "STOPPED"
    assert "Missing or failed independent proof" in result["error"]
    # The documentation check alone is not enough: the review is still missing.
    cli(documented, "check", "--change", "example", "--snapshot", token)
    status = cli(documented, "status", "--change", "example", status=1)
    assert status["missing"] == ["behavioral"]
    result = publish(
        documented, "review", "--plan", f"{STATE}/acceptance.json", status=1
    )
    assert "Missing or failed independent proof" in result["error"]
    review(documented, hosting, title="docs: correct README prose")
    result = publish(documented, "run", "--authorize", "pr")
    assert result["status"] == "PUBLISHED"
    assert "first use" in git(hosting[0], "show", "feature:README.md")
    assert not calls.exists()


def run_docs_check(root, *names):
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from engineering.cli import main; raise SystemExit(main())",
            "--root",
            str(root),
            "docs-check",
            *names,
        ],
        env={"PYTHONPATH": str(TOOLING), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )


def test_docs_check_reports_broken_links_and_anchors(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/target.md").write_text(
        "# Target Heading\n\n## Repeat\n## Repeat\n\nSetext Title\n============\n\n"
        "> ## Quoted Heading\n\n## Heading With [link](x.md)\n\n- ## Listed Heading\n"
    )
    (tmp_path / "docs/target file.md").write_text("Spaced\n")
    (tmp_path / "docs/ok.md").write_text(
        "# Ok\n\n[t](target.md#target-heading) [r](target.md#repeat-1) [s](#ok)\n"
        "[root](/docs/target.md) [web](https://example.invalid/missing) "
        "[mail](mailto:a@example.invalid)\n"
        "[a](target.md#setext-title) [b](target.md#quoted-heading) "
        "[c](target.md#heading-with-link) [d](<target file.md>) "
        "[l](target.md#listed-heading) "
        "[e](target.md?plain=1#repeat)\n\n"
        "```\n[ignored](missing.md)\n```\n\n`[ignored](missing.md)`\n\n"
        "[ref]: target.md\n"
    )
    assert run_docs_check(tmp_path, "docs/ok.md").returncode == 0
    (tmp_path / "docs/bad.md").write_text(
        "[gone](missing.md) [anchor](target.md#absent) [escape](../../outside.md)\n"
        "[ref]: also-missing.md\n"
    )
    result = run_docs_check(tmp_path, "docs/ok.md", "docs/bad.md")
    assert result.returncode == 1
    for target in (
        "missing.md",
        "target.md#absent",
        "../../outside.md",
        "also-missing.md",
    ):
        assert f"docs/bad.md: broken link {target}" in result.stderr
    assert "docs/ok.md" not in result.stderr


@pytest.mark.parametrize("name", ["missing.md", "../outside.md"])
def test_docs_check_refuses_missing_or_unsafe_paths(tmp_path, name):
    result = run_docs_check(tmp_path, name)
    assert result.returncode == 1 and name in result.stderr


def test_docs_check_treats_dash_paths_as_files(tmp_path):
    # The required check separates paths with "--", so "-h.md" is a file.
    result = run_docs_check(tmp_path, "--", "-h.md")
    assert result.returncode == 1 and "-h.md" in result.stderr


def test_docs_check_requires_utf8(tmp_path):
    (tmp_path / "bad.md").write_bytes(b"\xff\n")
    result = run_docs_check(tmp_path, "bad.md")
    assert result.returncode == 1 and "UTF-8" in result.stderr
