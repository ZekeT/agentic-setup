"""Review tiers: declared tier, starter-rule floor and reviewer roles via the CLI."""

import json
import os
import subprocess
import sys
import tomllib

import pytest
from engineering.verification_requirements import DOCS

from .test_verification import (
    TOOLING,
    change_plan,
    cli,
    complete,
    git,
    prepare,
)
from .test_verification import repo as repo
from .test_verification_requirements import (
    CHECK,
    SUITES,
    edit,
    maintainer_checkout,
)
from .test_verification_requirements import prepare as prepare_paths
from .test_verification_requirements import pristine as pristine
from .test_verification_requirements import project as project

pytestmark = pytest.mark.integration


def test_plan_requires_a_review_tier_with_reason(repo):
    # Each plan-shape rejection is unit tested; this shows prepare applies them.
    path = repo / ".engineering/state/verification/plan.json"
    path.write_text(json.dumps({**json.loads(path.read_text()), "tier": "trivial"}))
    result = prepare(repo, status=1)
    assert result["status"] == "INCOMPLETE"
    assert "documentation, ordinary, sensitive" in result["error"]


def test_declared_tier_below_floor_names_paths_and_rules(repo):
    (repo / "Makefile").write_text("check:\n\t@test -s app.txt\n\n")
    change_plan(repo, paths=["app.txt", "Makefile"])
    error = prepare(repo, status=1)["error"]
    assert "below the tier floor sensitive" in error
    assert "Makefile" in error and "build recipe" in error
    assert "app.txt" not in error
    # A mixed change takes the highest path floor; declaring it is accepted.
    change_plan(repo, tier="sensitive")
    result = prepare(repo)
    assert result["floor"] == "sensitive" and result["required_roles"][-1] == "security"


CONFIG = ".engineering/config.toml"


def settings_text(documentation=(), sensitive=(), extra=""):
    return (
        'schema_version = 2\n[navigation]\nprovider = "none"\n[review]\n'
        f"documentation = {json.dumps(list(documentation))}\n"
        f"sensitive = {json.dumps(list(sensitive))}\n{extra}"
    )


def commit_base_settings(repo, text):
    """Commit review settings to the comparison base, keeping feature edits."""
    git(repo, "checkout", "--quiet", "main")
    (repo / CONFIG).write_text(text)
    git(repo, "add", CONFIG)
    git(repo, "commit", "--quiet", "-m", "review settings")
    git(repo, "checkout", "--quiet", "feature")
    git(repo, "merge", "--quiet", "--ff-only", "main")


def prepare_edits(repo, names, tier="sensitive"):
    """Replace the fixture change with edits to names; return prepare's result."""
    (repo / "app.txt").write_text("before\n")
    for name in names:
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text("changed\n")
    # Prose edits route to documentation checks; others to the project suite.
    checks = [["make", "check"], [*DOCS, *sorted(names)]]
    change_plan(repo, paths=names, tier=tier, checks=checks)
    return prepare(repo, status=0 if tier == "sensitive" else 1)


def recorded_paths(repo):
    record = repo / ".engineering/state/verification/example.json"
    return json.loads(record.read_text())["requirements"]["paths"]


def test_editing_review_settings_uses_the_stricter_of_base_and_proposed(repo):
    commit_base_settings(repo, settings_text(["docs/**"], ["billing/**"]))
    names = ["docs/guide.md", "src/app.py", "billing/rates.py", "api/keys.py"]
    prepare_edits(repo, names)
    # The proposed settings drop billing and document src; they add api.
    (repo / CONFIG).write_text(settings_text(["src/**"], ["api/**"]))
    change_plan(repo, paths=[CONFIG, *names])
    prepare(repo)
    assert recorded_paths(repo) == {
        "sensitive": {
            "api/keys.py": "project sensitive setting",
            "billing/rates.py": "project sensitive setting",
        },
        "ordinary": {
            CONFIG: "review settings",
            "docs/guide.md": "no documentation rule",
            "src/app.py": "no documentation rule",
        },
        "documentation": {},
    }


def test_invalid_review_settings_fail_planning(repo):
    commit_base_settings(repo, settings_text(["docs/**"]))
    (repo / CONFIG).write_text("schema_version = 2\n[review]\nsensitive = [1]\n")
    change_plan(repo, paths=["app.txt", CONFIG])
    result = prepare(repo, status=1)
    assert result["status"] == "INCOMPLETE" and "review.sensitive" in result["error"]


def test_record_stores_floor_categories_checks_and_roles(repo):
    (repo / "Makefile").write_text("check:\n\t@test -s app.txt\n\n")
    change_plan(repo, paths=["app.txt", "Makefile"], tier="sensitive")
    prepare(repo)
    data = json.loads(
        (repo / ".engineering/state/verification/example.json").read_text()
    )
    assert data["schema_version"] == 3
    assert data["requirements"] == {
        "floor": "sensitive",
        "paths": {
            "sensitive": {"Makefile": "build recipe"},
            "ordinary": {"app.txt": "no documentation rule"},
            "documentation": {},
        },
        "checks": [["make", "check"]],
        "roles": ["standards", "spec", "behavioral", "security"],
    }


def test_record_without_tier_data_requires_preparing_again(repo):
    complete(repo)
    path = repo / ".engineering/state/verification/example.json"
    legacy = json.loads(path.read_text())
    legacy["schema_version"] = 1
    del legacy["requirements"]
    plan = legacy["inputs"]["plan"]
    del plan["tier"], plan["tier_reason"]
    plan.update(security_required=False, security_reason="Legacy")
    path.write_text(json.dumps(legacy))
    result = cli(repo, "status", "--change", "example", status=1)
    assert result["status"] == "INCOMPLETE" and "prepare again" in result["error"]
    result = prepare(repo)
    assert result["status"] == "INCOMPLETE" and result["reports"] == {}
    history = json.loads((repo / result["previous_evidence"]).read_text())
    assert history["schema_version"] == 1


def floor_error(root, paths, checks, tier):
    return prepare_paths(root, paths, checks, status=1, tier=tier)["error"]


def test_generated_and_adopted_projects_share_review_defaults(pristine):
    settings = [
        tomllib.loads((pristine[kind] / CONFIG).read_text())["review"]
        for kind in ("generated", "adopted")
    ]
    assert settings[0] == settings[1]
    assert settings[0] == {
        "documentation": ["README.md", "docs/**/*.md"],
        "sensitive": [],
    }


@maintainer_checkout
def test_maintainer_destructive_modules_floor_at_sensitive(project):
    # Each maintainer floor rule is unit tested; this shows the role reaches them.
    name, rule = ".engineering/engineering/verification.py", "verification module"
    (project / name).parent.mkdir(parents=True, exist_ok=True)
    edit(project, name, "VALUE = 2\n")
    checks = [CHECK, *SUITES]
    error = floor_error(project, [name], checks, "ordinary")
    assert name in error and rule in error
    assert prepare_paths(project, [name], checks)["floor"] == "sensitive"


def test_status_reports_the_floor_current_rules_give(repo):
    change_plan(repo, tier="sensitive", tier_reason="Raised: parses credentials")
    complete(repo)
    stricter = (
        "import engineering.verification_requirements as rules\n"
        "rules.STARTER_SENSITIVE['fixture rule'] = ('app.txt',)\n"
    )
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            stricter + "from engineering.cli import main; raise SystemExit(main())",
            "--root",
            str(repo),
            "verify",
            "status",
            "--change",
            "example",
        ],
        env={**os.environ, "PYTHONPATH": str(TOOLING)},
        capture_output=True,
        text=True,
    )
    assert json.loads(proc.stdout)["floor"] == "sensitive"
    assert cli(repo, "status", "--change", "example")["floor"] == "ordinary"
