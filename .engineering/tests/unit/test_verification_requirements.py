"""Requirement decisions from a written-down facts value: categories, floors, checks."""

import re

import pytest
from engineering.verification_requirements import (
    DOCS,
    GRAFT,
    HEALTH,
    PROJECT,
    SUITES,
    classify,
    requirements,
    tier_paths,
)

CONFIG = ".engineering/config.toml"
MANIFEST = ".engineering/manifest.json"
INSTALL = ".engineering/state/install.json"
TOOL = ".engineering/engineering/tool.py"


def categorized(categories):
    """Only the categories that hold paths."""
    return {category: names for category, names in categories.items() if names}


def rejection(facts, plan):
    with pytest.raises(ValueError) as error:
        requirements(facts, plan)
    return str(error.value)


# Path classification


def test_no_paths_fall_in_no_category(facts):
    assert categorized(classify(facts(), "consumer", [])) == {}


@pytest.mark.parametrize(
    "ownership,changed,category",
    [
        ({}, True, "project"),
        ({"Makefile": "section"}, True, "managed integration"),
        ({"Makefile": "integration"}, True, "managed integration"),
        ({"Makefile": "preserve"}, True, "project configuration"),
        ({"Makefile": "file"}, False, "managed integration"),
        ({"Makefile": "file"}, True, "managed implementation"),
    ],
)
def test_consumer_paths_are_classified_by_ownership(
    facts, path_facts, ownership, changed, category
):
    observed = facts(
        paths={"Makefile": path_facts(changed=changed)}, ownership=ownership
    )
    assert categorized(classify(observed, "consumer", ["Makefile"])) == {
        category: ["Makefile"]
    }


@pytest.mark.parametrize("name", [MANIFEST, INSTALL])
def test_unowned_installation_metadata_is_its_own_category(facts, name):
    assert categorized(classify(facts([name]), "consumer", [name])) == {
        "installation metadata": [name]
    }


def test_baseline_ownership_survives_a_dropped_entry(facts):
    # Dropping the entry and the file together still edits a managed file.
    observed = facts([TOOL], base_ownership={TOOL: "file"})
    assert categorized(classify(observed, "consumer", [TOOL])) == {
        "managed implementation": [TOOL]
    }


@pytest.mark.parametrize(
    "name,ownership",
    [
        (TOOL, {TOOL: "file"}),
        (".engineering/tests/test_tool.py", {}),
        (".engineering/template/README.md", {}),
        (".engineering/scripts/check.sh", {}),
        (".engineering/migrations/0001.py", {}),
        (".engineering/evals/case.toml", {}),
    ],
)
def test_maintainer_tooling_and_distributed_files_are_maintainer_source(
    facts, name, ownership
):
    observed = facts([name], ownership=ownership)
    assert categorized(classify(observed, "maintainer", [name])) == {
        "maintainer source": [name]
    }
    assert "maintainer source" not in categorized(
        classify(observed, "consumer", [name])
    )


def test_many_paths_are_sorted_into_each_category(facts, path_facts):
    names = ["z.txt", CONFIG, "a.txt", "Makefile", TOOL]
    observed = facts(
        names,
        paths={TOOL: path_facts(changed=False)},
        ownership={CONFIG: "preserve", "Makefile": "section", TOOL: "file"},
    )
    assert categorized(classify(observed, "consumer", names)) == {
        "project configuration": [CONFIG],
        "managed integration": [TOOL, "Makefile"],
        "project": ["a.txt", "z.txt"],
    }


def test_missing_manifest_blocks_classification(facts, plan):
    assert rejection(facts(["app.txt"], manifest=False), plan(["app.txt"])) == (
        f"{MANIFEST} is missing; ownership cannot be classified. "
        "Restore the installation manifest before verification."
    )


# Per-path tier floor


def floors(names, role="consumer", review=None):
    """Each path's (tier, rule) under the given review settings versions."""
    settings = review or (
        {"documentation": ("README.md", "docs/**/*.md"), "sensitive": ()},
    )
    result = tier_paths(role, names, settings)
    return {
        name: (tier, rule) for tier in result for name, rule in result[tier].items()
    }


def test_no_paths_have_no_floor():
    assert tier_paths("consumer", [], ({"documentation": (), "sensitive": ()},)) == {
        "sensitive": {},
        "ordinary": {},
        "documentation": {},
    }


@pytest.mark.parametrize(
    "name,rule",
    [
        ("pyproject.toml", "dependency manifest or lock"),
        ("uv.lock", "dependency manifest or lock"),
        ("web/package.json", "dependency manifest or lock"),
        ("web/package-lock.json", "dependency manifest or lock"),
        (".engineering/dependencies.toml", "dependency manifest or lock"),
        (".claude/settings.json", "agent settings"),
        (".claude/settings.local.json", "agent settings"),
        (".claude/hooks/project_hook.py", "hook"),
        (".pre-commit-config.yaml", "hook"),
        (".envrc", "environment loader"),
        (".github/workflows/ci.yml", "workflow"),
        ("Makefile", "build recipe"),
        ("GNUmakefile", "build recipe"),
        ("build/rules.mk", "build recipe"),
        (".engineering/scripts/check.sh", "check script"),
        (".claude/statusline.sh", "agent-executed script"),
        ("engineering", "Engineering launcher"),
        (".engineering/bin/graft", "Engineering launcher"),
        (".engineering/setup.sh", "Engineering launcher"),
    ],
)
def test_starter_sensitive_paths_floor_at_sensitive_for_every_role(name, rule):
    for role in ("consumer", "maintainer"):
        assert floors([name], role) == {name: ("sensitive", rule)}


def test_launcher_rule_is_anchored_to_the_root():
    assert floors(["tools/engineering"]) == {
        "tools/engineering": ("ordinary", "no documentation rule")
    }


@pytest.mark.parametrize(
    "name,rule",
    [
        (".engineering/engineering/verification.py", "verification module"),
        (".engineering/engineering/verification_facts.py", "verification module"),
        (".engineering/engineering/markdown.py", "verification module"),
        (".engineering/engineering/publication_git.py", "publication module"),
        (".engineering/engineering/deps.py", "dependency module"),
        (".engineering/engineering/graft.py", "dependency module"),
        (".engineering/engineering/skill_install.py", "skill installation module"),
        (".engineering/engineering/transaction.py", "apply or transaction module"),
        (".engineering/engineering/updates.py", "update module"),
        (".engineering/engineering/migrate/legacy.py", "migration module"),
        (".engineering/migrations/0001.py", "migration module"),
    ],
)
def test_destructive_maintainer_modules_floor_at_sensitive_only_for_maintainers(
    name, rule
):
    assert floors([name], "maintainer") == {name: ("sensitive", rule)}
    assert floors([name], "consumer")[name][0] == "ordinary"


def test_other_maintainer_source_floors_at_ordinary():
    assert floors([TOOL], "maintainer") == {TOOL: ("ordinary", "no documentation rule")}


@pytest.mark.parametrize(
    "name",
    [
        "CLAUDE.md",
        "AGENTS.md",
        "REVIEW.md",
        "ENGINEERING.md",
        ".claude/commands/review.md",
        ".engineering/docs/verification.md",
        "docs/agents/domain.md",
    ],
)
def test_agent_policy_is_never_documentation(name):
    # docs/agents/ lies inside the default docs/**/*.md documentation setting.
    broad = ({"documentation": ("**",), "sensitive": ()},)
    assert floors([name], review=broad) == {name: ("ordinary", "agent policy")}


def test_review_settings_floor_at_ordinary_even_when_documented():
    broad = ({"documentation": ("**",), "sensitive": ()},)
    assert floors([CONFIG], review=broad) == {CONFIG: ("ordinary", "review settings")}


@pytest.mark.parametrize(
    "name,tier",
    [
        ("README.md", "documentation"),
        ("docs/intro.md", "documentation"),
        ("docs/deep/intro.md", "documentation"),
        ("docs/conf.py", "ordinary"),
        ("notes.md", "ordinary"),
        ("sub/README.md", "documentation"),
    ],
)
def test_default_documentation_setting_covers_root_and_nested_markdown(name, tier):
    assert floors([name])[name][0] == tier


def test_project_sensitive_settings_add_floors():
    review = ({"documentation": ("docs/**",), "sensitive": ("src/auth/**",)},)
    assert floors(["src/auth/login.py", "src/app.py"], review=review) == {
        "src/auth/login.py": ("sensitive", "project sensitive setting"),
        "src/app.py": ("ordinary", "no documentation rule"),
    }


def test_project_settings_cannot_weaken_starter_rules():
    broad = ({"documentation": ("**",), "sensitive": ()},)
    names = ["Makefile", "CLAUDE.md", "guide.md", ".envrc", ".pre-commit-config.yaml"]
    assert floors(names, review=broad) == {
        "Makefile": ("sensitive", "build recipe"),
        ".envrc": ("sensitive", "environment loader"),
        ".pre-commit-config.yaml": ("sensitive", "hook"),
        "CLAUDE.md": ("ordinary", "agent policy"),
        "guide.md": ("documentation", "project documentation setting"),
    }


def test_the_stricter_of_base_and_proposed_settings_applies():
    base = {"documentation": ("docs/**",), "sensitive": ("billing/**",)}
    proposed = {"documentation": ("src/**",), "sensitive": ("api/**",)}
    names = ["docs/guide.md", "src/app.py", "billing/rates.py", "api/keys.py"]
    assert floors(names, review=(base, proposed)) == {
        "api/keys.py": ("sensitive", "project sensitive setting"),
        "billing/rates.py": ("sensitive", "project sensitive setting"),
        "docs/guide.md": ("ordinary", "no documentation rule"),
        "src/app.py": ("ordinary", "no documentation rule"),
    }


# Overall floor, prose route and reviewer roles


def test_one_project_path_needs_the_project_suite_and_ordinary_review(facts, plan):
    assert requirements(facts(["app.txt"]), plan(["app.txt"], tier="ordinary")) == {
        "floor": "ordinary",
        "paths": {
            "sensitive": {},
            "ordinary": {"app.txt": "no documentation rule"},
            "documentation": {},
        },
        "checks": [PROJECT],
        "roles": ["standards", "spec", "behavioral"],
    }


def test_mixed_change_takes_the_highest_path_floor(facts, plan):
    names = ["README.md", "Makefile", "app.txt"]
    result = requirements(facts(names), plan(names))
    assert result["floor"] == "sensitive"
    assert result["roles"] == ["standards", "spec", "behavioral", "security"]
    assert rejection(facts(names), plan(names, tier="ordinary")) == (
        "Declared tier ordinary is below the tier floor sensitive: "
        "Makefile (build recipe). Declare at least sensitive."
    )


def test_below_floor_names_every_path_at_the_floor(facts, plan):
    names = ["app.txt", "notes.md"]
    assert rejection(facts(names), plan(names, tier="documentation")) == (
        "Declared tier documentation is below the tier floor ordinary: "
        "app.txt (no documentation rule), notes.md (no documentation rule). "
        "Declare at least ordinary."
    )


def test_no_review_settings_means_no_documentation(facts, plan):
    empty = {"documentation": (), "sensitive": ()}
    observed = facts(["README.md"], review=empty)
    assert rejection(observed, plan(["README.md"], tier="documentation")) == (
        "Declared tier documentation is below the tier floor ordinary: "
        "README.md (no documentation rule). Declare at least ordinary."
    )


@pytest.mark.parametrize("names", [["README.md"], ["docs/b.md", "README.md"]])
def test_prose_only_documentation_needs_only_documentation_checks(facts, plan, names):
    checks = [[*DOCS, *sorted(names)]]
    result = requirements(facts(names), plan(names, checks, tier="documentation"))
    assert result["floor"] == "documentation"
    assert result["checks"] == checks
    assert result["roles"] == ["behavioral"]


def test_prose_only_plan_without_documentation_check_is_rejected(facts, plan):
    message = rejection(facts(["README.md"]), plan(["README.md"], tier="documentation"))
    assert message == (
        f"Required checks missing: [{[*DOCS, 'README.md']!r}] (role consumer; "
        "project: README.md; prose-only documentation needs documentation checks)"
    )


@pytest.mark.parametrize(
    "name,changes,reason",
    [
        ("README.md", {"present": False}, "deleted document"),
        ("README.md", {"executable": True}, "executable file"),
        ("README.md", {"base_executable": True}, "executable file"),
        ("docs/notes.txt", {}, "unsupported documentation format"),
    ],
)
def test_non_prose_documentation_takes_the_stricter_route(
    facts, path_facts, plan, name, changes, reason
):
    review = {"documentation": ("README.md", "docs/**"), "sensitive": ()}
    observed = facts(paths={name: path_facts(**changes)}, review=review)
    assert rejection(observed, plan([name], tier="documentation")) == (
        f"Declared tier documentation is below the tier floor ordinary: "
        f"{name} ({reason}). Declare at least ordinary."
    )
    assert "Required checks missing" in rejection(
        observed, plan([name], [[*DOCS, name]], tier="ordinary")
    )
    result = requirements(observed, plan([name], tier="ordinary"))
    assert result["paths"]["ordinary"] == {name: reason}
    assert result["checks"] == [PROJECT]


def test_mixed_prose_and_non_prose_requires_the_application_suite(facts, plan):
    names = ["README.md", "app.txt"]
    result = requirements(facts(names), plan(names, tier="ordinary"))
    assert result["checks"] == [PROJECT]
    assert result["paths"]["documentation"] == {
        "README.md": "project documentation setting"
    }


def test_agent_instructions_need_the_application_suite(facts, plan):
    observed = facts(["CLAUDE.md"])
    message = rejection(observed, plan(["CLAUDE.md"], [[*DOCS, "CLAUDE.md"]]))
    assert message.startswith(f"Required checks missing: [{PROJECT!r}]")


def test_owned_prose_is_not_prose_only(facts, plan):
    observed = facts(["README.md"], ownership={"README.md": "section"})
    result = requirements(observed, plan(["README.md"], [PROJECT, HEALTH]))
    assert result["checks"] == [PROJECT, HEALTH]


def test_configuring_documentation_cannot_lower_its_own_requirements(facts, plan):
    base = {"documentation": ("README.md",), "sensitive": ()}
    proposed = {"documentation": ("README.md", "*.txt"), "sensitive": ()}
    names = [CONFIG, "app.txt"]
    observed = facts(names, base_review=base, review=proposed)
    assert rejection(observed, plan(names, tier="documentation")) == (
        "Declared tier documentation is below the tier floor ordinary: "
        f"{CONFIG} (review settings), app.txt (no documentation rule). "
        "Declare at least ordinary."
    )


@pytest.mark.parametrize(
    "tier,roles",
    [
        ("ordinary", ["standards", "spec", "behavioral"]),
        ("sensitive", ["standards", "spec", "behavioral", "security"]),
    ],
)
def test_raised_tier_sets_roles_but_not_floor_or_checks(facts, plan, tier, roles):
    result = requirements(facts(["app.txt"]), plan(["app.txt"], tier=tier))
    assert (result["floor"], result["checks"], result["roles"]) == (
        "ordinary",
        [PROJECT],
        roles,
    )


# Required checks


@pytest.mark.parametrize(
    "name,ownership",
    [
        (CONFIG, {CONFIG: "preserve"}),
        ("CLAUDE.md", {"CLAUDE.md": "section"}),
        (".claude/settings.json", {".claude/settings.json": "integration"}),
        (TOOL, {TOOL: "file"}),
        (MANIFEST, {}),
        (INSTALL, {}),
    ],
)
def test_consumer_configuration_and_metadata_need_the_health_check(
    facts, path_facts, plan, name, ownership
):
    observed = facts(paths={name: path_facts(changed=False)}, ownership=ownership)
    message = rejection(observed, plan([name]))
    assert message.startswith(f"Required checks missing: [{HEALTH!r}] (role consumer;")
    assert "engineering-test" not in message
    assert requirements(observed, plan([name], [PROJECT, HEALTH]))["checks"] == [
        PROJECT,
        HEALTH,
    ]


def test_required_checks_are_unchanged_by_tier(facts, plan):
    observed = facts([CONFIG], ownership={CONFIG: "preserve"})
    messages = {
        tier: rejection(observed, plan([CONFIG], tier=tier))
        for tier in ("ordinary", "sensitive")
    }
    assert messages["ordinary"] == messages["sensitive"]
    assert messages["ordinary"] == (
        f"Required checks missing: [{HEALTH!r}] "
        f"(role consumer; project configuration: {CONFIG})"
    )


@pytest.mark.parametrize(
    "name,ownership",
    [
        (TOOL, {TOOL: "file"}),
        (".engineering/tests/test_tool.py", {}),
        (".engineering/template/README.md", {}),
    ],
)
def test_maintainer_source_requires_maintainer_suites(facts, plan, name, ownership):
    observed = facts([name], role="maintainer", ownership=ownership)
    message = rejection(observed, plan([name], [PROJECT, HEALTH]))
    assert message.startswith(f"Required checks missing: {SUITES!r} (role maintainer;")
    assert requirements(observed, plan([name], [PROJECT, *SUITES]))["checks"] == [
        PROJECT,
        *SUITES,
    ]


def test_maintainer_configuration_needs_only_project_and_health_checks(facts, plan):
    observed = facts([CONFIG], role="maintainer", ownership={CONFIG: "preserve"})
    assert requirements(observed, plan([CONFIG], [PROJECT, HEALTH]))["checks"] == [
        PROJECT,
        HEALTH,
    ]


@pytest.mark.parametrize("name", [MANIFEST, INSTALL])
def test_maintainer_metadata_needs_health_and_maintainer_suites(facts, plan, name):
    observed = facts([name], role="maintainer")
    assert rejection(observed, plan([name], [PROJECT, HEALTH])).startswith(
        f"Required checks missing: {SUITES!r}"
    )
    assert rejection(observed, plan([name], [PROJECT, *SUITES])).startswith(
        f"Required checks missing: [{HEALTH!r}]"
    )
    result = requirements(observed, plan([name], [PROJECT, HEALTH, *SUITES]))
    assert result["checks"] == [PROJECT, HEALTH, *SUITES]


def test_removing_a_maintainer_target_cannot_lower_requirements(facts, plan):
    names = ["Makefile", TOOL]
    ownership = {"Makefile": "section", TOOL: "file"}
    observed = facts(names, role="maintainer", ownership=ownership)
    assert requirements(observed, plan(names, [PROJECT, HEALTH, *SUITES]))[
        "checks"
    ] == [PROJECT, HEALTH, *SUITES]
    assert "engineering-test" in rejection(observed, plan(names, [PROJECT, HEALTH]))


@pytest.mark.parametrize(
    "role,base_role,expected",
    [
        ("consumer", "maintainer", "maintainer"),
        ("maintainer", "consumer", "maintainer"),
        ("maintainer", None, "maintainer"),
        ("consumer", None, "consumer"),
        ("consumer", "consumer", "consumer"),
    ],
)
def test_the_stricter_of_base_and_proposed_role_applies(
    facts, plan, role, base_role, expected
):
    name = ".engineering/tests/test_tool.py"
    observed = facts([name], role=role, base_role=base_role)
    message = rejection(observed, plan([name], [HEALTH]))
    assert f"(role {expected};" in message
    assert ("engineering-test" in message) == (expected == "maintainer")


def test_configured_application_roots_require_the_graft_check(facts, plan):
    observed = facts(["app.txt"], navigation="graft", graft=True)
    assert rejection(observed, plan(["app.txt"])) == (
        f"Required checks missing: [{GRAFT!r}] (role consumer; project: app.txt; "
        "configured application roots require Graft check)"
    )
    assert requirements(observed, plan(["app.txt"], [PROJECT, GRAFT]))["checks"] == [
        PROJECT,
        GRAFT,
    ]


@pytest.mark.parametrize(
    "navigation,accepted", [(None, True), ("graft", True), ("none", False)]
)
def test_graft_check_needs_graft_navigation_when_configured(
    facts, plan, navigation, accepted
):
    observed = facts(["app.txt"], navigation=navigation)
    checks = plan(["app.txt"], [PROJECT, GRAFT])
    if accepted:
        assert requirements(observed, checks)["checks"] == [PROJECT]
    else:
        assert rejection(observed, checks) == (
            "navigation disabled: remove the Graft check from the plan, or "
            'select [navigation] provider = "graft"'
        )


# Managed implementation and pinned starter updates


def test_consumer_managed_implementation_edit_is_rejected_with_route(facts, plan):
    observed = facts([TOOL], ownership={TOOL: "file"})
    message = rejection(observed, plan([TOOL], [PROJECT, HEALTH, *SUITES]))
    assert message.startswith(
        f"Managed implementation edited in a consumer project: [{TOOL!r}]. "
    )
    assert "./engineering update <project>" in message and "upstream" in message
    assert message.endswith("Proposed manifest digests cannot vouch for bytes.")


def test_pinned_starter_update_needs_health_and_sensitive_review(facts, plan):
    names = [TOOL, MANIFEST]
    observed = facts(names, ownership={TOOL: "file"}, starter_source=True)
    assert re.match(
        re.escape(f"Required checks missing: [{HEALTH!r}]"),
        rejection(observed, plan(names)),
    )
    assert rejection(observed, plan(names, [PROJECT, HEALTH], tier="ordinary")) == (
        "Declared tier ordinary is below the tier floor sensitive: "
        f"{TOOL} (pinned starter update source), "
        f"{MANIFEST} (pinned starter update source). Declare at least sensitive."
    )
    result = requirements(observed, plan(names, [PROJECT, HEALTH]))
    assert result["paths"] == {
        "sensitive": {
            MANIFEST: "pinned starter update source",
            TOOL: "pinned starter update source",
        },
        "ordinary": {},
        "documentation": {},
    }


def test_pinned_starter_update_of_prose_is_not_prose_only(facts, plan):
    observed = facts(["README.md"], starter_source=True)
    result = requirements(observed, plan(["README.md"], [PROJECT, HEALTH]))
    assert result["checks"] == [PROJECT, HEALTH]
