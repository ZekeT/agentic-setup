"""Carrying reports across an advanced base, decided from both records."""

import pytest
from engineering.verification_carry import carried, carry_candidate

from .conftest import TOKEN

OLD = "0" * 64
NEW_BASE = "e" * 40
DEPENDENCIES = ".engineering/state/dependencies.json"


@pytest.fixture
def rebased(record, report):
    """A complete record and its rebased successor on an advanced base."""

    def build(**changes):
        old = record(report("spec", snapshot=OLD), report(snapshot=OLD), snapshot=OLD)
        new = record()
        new["inputs"]["base"] = NEW_BASE
        for key, value in changes.items():
            new["inputs"][key] = value
        return old, new

    return build


def test_an_unrelated_base_advance_carries_every_report(rebased, report):
    old, new = rebased()
    assert carry_candidate(old, new)
    assert carried(old, new, {"upstream.txt"}) == {
        "spec": {**report("spec"), "snapshot": TOKEN, "carried_from": OLD},
        "behavioral": {**report(), "snapshot": TOKEN, "carried_from": OLD},
    }


def test_an_unchanged_base_carries_nothing(rebased):
    old, new = rebased(base="b" * 40)
    assert not carry_candidate(old, new)


def test_no_previous_reports_carry_nothing(rebased):
    old, new = rebased()
    old["reports"] = {}
    assert not carry_candidate(old, new)


@pytest.mark.parametrize(
    "key,value",
    [
        ("plan", {"requirement": "Changed requirement"}),
        ("plan", {"checks": [["make", "check"], ["git", "--version"]]}),
        ("plan", {"tools": [["git", "--version"]]}),
        ("tools", []),
        ("root", "/elsewhere"),
        ("runtime", "3.13.0"),
    ],
)
def test_changed_plan_tools_or_environment_carry_nothing(rebased, key, value):
    old, new = rebased()
    new["inputs"][key] = (
        {**new["inputs"][key], **value} if isinstance(value, dict) else value
    )
    assert not carry_candidate(old, new)


def test_a_changed_starter_source_carries_nothing(rebased):
    old, new = rebased(starter_source={"commit": "a" * 40})
    assert not carry_candidate(old, new)


def test_changed_requirements_carry_nothing(rebased):
    old, new = rebased()
    new["requirements"]["floor"] = "sensitive"
    assert not carry_candidate(old, new)


@pytest.mark.parametrize("changed", ["app.txt", "installed", DEPENDENCIES])
def test_upstream_changes_to_scoped_paths_carry_nothing(rebased, changed):
    old, new = rebased()
    for data in (old, new):
        data["inputs"]["plan"]["inputs"] = ["installed"]
    assert carried(old, new, {"upstream.txt", changed}) == {}


@pytest.mark.parametrize("changed", ["app.txt", "installed", DEPENDENCIES])
def test_changed_scoped_content_carries_nothing(rebased, changed):
    old, new = rebased()
    for data in (old, new):
        data["inputs"]["plan"]["inputs"] = ["installed"]
    new["inputs"]["files"][changed] = {"sha256": "a" * 64, "executable": False}
    assert carried(old, new, set()) == {}


def test_a_changed_mode_on_a_scoped_path_carries_nothing(rebased):
    old, new = rebased()
    new["inputs"]["files"]["app.txt"] = {
        **new["inputs"]["files"]["app.txt"],
        "executable": True,
    }
    assert carried(old, new, set()) == {}


def test_unestablished_ancestry_carries_nothing(rebased):
    old, new = rebased()
    assert carried(old, new, None) == {}
