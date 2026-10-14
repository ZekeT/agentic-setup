"""Plan shape and review settings are rejected from their content alone."""

import pytest
from engineering.settings import review_settings
from engineering.verification_snapshot import plan_shape


def rejection(plan):
    with pytest.raises(ValueError) as error:
        plan_shape(plan)
    return str(error.value)


def test_a_complete_plan_is_accepted(plan):
    plan_shape(plan(["app.txt"]))


@pytest.mark.parametrize(
    "changes,message",
    [
        (
            {"security_required": False, "security_reason": "Not sensitive"},
            "security_required and security_reason are replaced by tier and "
            "tier_reason: declare the review tier (documentation, ordinary or "
            "sensitive) and why",
        ),
        (
            {"extra": True},
            "Plan requires ['base', 'checks', 'inputs', 'paths', 'requirement', "
            "'tier', 'tier_reason', 'tools'] and optional starter_source",
        ),
        (
            {"tier": "trivial"},
            "tier must be one of: documentation, ordinary, sensitive",
        ),
        ({"tier_reason": " "}, "tier_reason: nonempty text required"),
        ({"requirement": 1}, "requirement: nonempty text required"),
        ({"base": "--upload-pack=x"}, "Invalid base reference"),
        ({"paths": []}, "paths: expected a list"),
        ({"paths": ["a.txt", "a.txt"]}, "paths: duplicate paths"),
        ({"paths": [""]}, "paths: expected nonempty strings"),
        ({"inputs": ["b.txt", "b.txt"]}, "inputs: duplicate paths"),
        (
            {"paths": [".engineering/state/verification/x.json"]},
            "Verification bookkeeping cannot be a source input",
        ),
        ({"checks": []}, "checks: nonempty argv list required"),
        ({"checks": [["make"], ["make"]]}, "checks: duplicate commands"),
        ({"tools": [[]]}, "tools: expected a list"),
        (
            {"starter_source": {"repository": "/local/path", "commit": "0" * 40}},
            "starter_source.repository requires an https/http/ssh/git URL without "
            "password, query or fragment; local checkout paths are not sources",
        ),
    ],
)
def test_malformed_plans_are_rejected(plan, changes, message):
    assert rejection({**plan(["app.txt"]), **changes}) == message


def test_a_plan_without_tier_is_rejected(plan):
    incomplete = plan(["app.txt"])
    del incomplete["tier"]
    assert rejection(incomplete).startswith("Plan requires ")


def test_empty_inputs_are_accepted_and_many_paths_too(plan):
    plan_shape({**plan(["a.txt", "b/c.txt", "README.md"]), "inputs": []})


@pytest.mark.parametrize(
    "text,message",
    [
        ('[review]\ndocumentation = "docs/**"\n', "review.documentation"),
        ("[review]\nsensitive = [1]\n", "review.sensitive"),
        ('[review]\nsensitive = [""]\n', "review.sensitive"),
        ("[review]\nskip = true\n", "config.unknown: review"),
    ],
)
def test_invalid_review_settings_name_the_setting(text, message):
    with pytest.raises(ValueError) as error:
        review_settings(text.encode())
    assert str(error.value).startswith(".engineering/config.toml review settings: ")
    assert message in str(error.value)


def test_absent_review_settings_list_nothing():
    assert review_settings(None) == {"documentation": (), "sensitive": ()}
    assert review_settings(b"schema_version = 2\n") == {
        "documentation": (),
        "sensitive": (),
    }
