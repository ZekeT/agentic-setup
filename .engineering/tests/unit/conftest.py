"""Keep the unit tier in process: no subprocesses, no real repository reads."""

import os
import subprocess
from types import MappingProxyType

import pytest
from engineering.verification_facts import PathFacts, RequirementFacts
from engineering.verification_requirements import REVIEWERS

# Starter review defaults (settings.REVIEW_DEFAULTS), written down as data.
DEFAULT_REVIEW = MappingProxyType(
    {"documentation": ("README.md", "docs/**/*.md"), "sensitive": ()}
)


def frozen(settings):
    """Review settings as gathered: both pattern lists, as tuples."""
    return MappingProxyType(
        {key: tuple(settings.get(key, ())) for key in ("documentation", "sensitive")}
    )


@pytest.fixture(autouse=True)
def no_subprocesses(request, monkeypatch):
    """Fail a unit test that starts a subprocess, naming it and the command."""

    def refuse(command):
        pytest.fail(
            f"{request.node.nodeid} started a subprocess: {command!r}. Unit tests "
            "run in process; move it to an integration test or decide from facts.",
            pytrace=False,
        )

    original = subprocess.Popen.__init__

    def popen(self, args, *rest, **options):
        refuse(args)
        original(self, args, *rest, **options)  # pragma: no cover

    monkeypatch.setattr(subprocess.Popen, "__init__", popen)
    monkeypatch.setattr(os, "system", refuse)
    for name in ("posix_spawn", "posix_spawnp"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, lambda path, *_, **__: refuse(path))
    for name in ("fork", "forkpty"):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, lambda name=name: refuse(name))
    for name in ("execv", "execve"):
        monkeypatch.setattr(os, name, lambda path, *_: refuse(path))


@pytest.fixture
def path_facts():
    """A present, edited, non-executable file unless overridden."""

    def build(**changes) -> PathFacts:
        values = {
            "present": True,
            "changed": True,
            "executable": False,
            "base_executable": False,
        }
        return PathFacts(**{**values, **changes})

    return build


@pytest.fixture
def facts(path_facts):
    """A consumer project with default review settings and no ownership entries.

    Paths not given explicit facts are present, edited, non-executable files.
    """

    def build(
        names=(),
        *,
        paths=None,
        role="consumer",
        base_role=None,
        ownership=None,
        base_ownership=None,
        review=None,
        base_review=None,
        navigation=None,
        graft=False,
        starter_source=False,
        manifest=True,
    ) -> RequirementFacts:
        observed = {name: path_facts() for name in names} | (paths or {})
        proposed = frozen(review) if review is not None else DEFAULT_REVIEW
        return RequirementFacts(
            role=role,
            base_role=base_role,
            proposed_ownership=MappingProxyType(ownership or {}) if manifest else None,
            base_ownership=MappingProxyType(base_ownership or {}),
            review=(
                frozen(base_review) if base_review is not None else proposed,
                proposed,
            ),
            navigation=navigation,
            graft=graft,
            starter_source=starter_source,
            paths=MappingProxyType(observed),
        )

    return build


@pytest.fixture
def plan():
    """A verification plan; sensitive is never below the floor."""

    def build(paths, checks=(("make", "check"),), tier="sensitive"):
        return {
            "base": "main",
            "requirement": "Exercise requirement decisions",
            "paths": list(paths),
            "checks": [list(command) for command in checks],
            "tools": [["python", "--version"]],
            "inputs": [],
            "tier": tier,
            "tier_reason": "Fixture tier",
        }

    return build


# Evidence values as stored JSON: snapshot tokens and full commit IDs.
TOKEN = "1" * 64
BASE = "b" * 40
FILE = {"sha256": "f" * 64, "executable": False}


@pytest.fixture
def report():
    """An independent PASS report for the current snapshot."""

    def build(role="behavioral", **changes):
        native = (
            {"reviewed_commit": "c" * 40, "comparison_base": BASE}
            if role in ("standards", "spec")
            else {}
        )
        return {
            **native,
            "snapshot": TOKEN,
            "role": role,
            "reviewer": f"fresh-{role}-session",
            "independent": True,
            "verdict": "PASS",
            "summary": "Inspected fixture behavior against the requirement",
            "findings": [],
            "coverage_gaps": [],
            **changes,
        }

    return build


@pytest.fixture
def inputs(plan):
    """Snapshot inputs for a one-path ordinary plan."""

    def build(**changes):
        return {
            "base": BASE,
            "base_tip": BASE,
            "files": {"app.txt": FILE, "Makefile": FILE},
            "plan": plan(["app.txt"], tier="ordinary"),
            "tools": [
                {
                    "command": ["python", "--version"],
                    "exit_code": 0,
                    "stdout": "Python 3.12.0\n",
                    "stderr": "",
                }
            ],
            "root": "/work/project",
            "runtime": "3.12.0",
            **changes,
        }

    return build


@pytest.fixture
def record(inputs):
    """A stored schema 3 record of the given reports, with passing checks."""

    def build(*reports, tier="ordinary", checks=None, snapshot=TOKEN, **changes):
        current = inputs()
        current["plan"]["tier"] = tier
        return {
            "schema_version": 3,
            "snapshot": snapshot,
            "inputs": current,
            "requirements": {
                "floor": "ordinary",
                "paths": {
                    "sensitive": {},
                    "ordinary": {"app.txt": "no documentation rule"},
                    "documentation": {},
                },
                "checks": [["make", "check"]],
                "roles": list(REVIEWERS[tier]),
            },
            "checks": ([passed(["make", "check"])] if checks is None else list(checks)),
            "reports": {item["role"]: item for item in reports},
            "checkout": ".engineering/state/verification/example-1/checkout",
            **changes,
        }

    return build


def passed(command, exit_code=0):
    """One recorded check result."""
    return {"command": command, "exit_code": exit_code, "stdout": "", "stderr": ""}
