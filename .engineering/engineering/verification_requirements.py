"""Decide required checks, tier floor and reviewer roles for a verification plan.

Decisions are pure functions of a gathered facts value (verification_facts) and
the plan: they read no files, start no processes and touch no clock or environment.
"""

from collections.abc import Mapping
from fnmatch import fnmatchcase
from pathlib import PurePosixPath
from typing import Any

from .installation import MANIFEST_PATH
from .markdown import SUFFIXES
from .ownership import METADATA
from .settings import CONFIGURATION
from .verification_facts import PathFacts, RequirementFacts, Review

# Starter tooling directories; some files are distributed, but everything here
# is maintainer source in the maintainer checkout (never consumer policy).
MAINTAINER_TOOLING = tuple(
    f".engineering/{name}/"
    for name in ("template", "tests", "evals", "scripts", "migrations")
)
PROJECT = ["make", "check"]
HEALTH = ["make", "engineering-check"]
SUITES = [["make", "engineering-test"], ["make", "engineering-evals"]]
GRAFT = [".engineering/bin/graft", "check"]
# Prose-only plans run this on their paths instead of the application suite;
# "--" keeps a path such as "-h.md" from being parsed as an option.
DOCS = ["./engineering", "docs-check", "--"]

# Review tiers in increasing order, with the reviewer roles each requires.
TIERS = ("documentation", "ordinary", "sensitive")
REVIEWERS = {
    "documentation": ["behavioral"],
    "ordinary": ["standards", "spec", "behavioral"],
    "sensitive": ["standards", "spec", "behavioral", "security"],
}
# Starter-owned floor rules (ADR 0002); projects may add to them, never remove.
# A pattern without "/" matches a file name at any depth; others match the
# repository path, where "*" also crosses directories. A leading "/" anchors a
# pattern without another "/" to the repository root. Project review settings
# use the same pattern rules.
STARTER_SENSITIVE = {
    "dependency manifest or lock": (
        "pyproject.toml",
        "uv.lock",
        "package*.json",
        "*package-lock.json",
        ".engineering/dependencies.toml",
    ),
    "agent settings": (".claude/settings*.json",),
    "hook": (".claude/hooks/**", ".pre-commit-config.yaml"),
    "environment loader": (".envrc",),
    "workflow": (".github/workflows/**",),
    "build recipe": ("Makefile", "GNUmakefile", "makefile", "*.mk"),
    "check script": (".engineering/scripts/**",),
    "agent-executed script": (".claude/statusline.sh",),
    "Engineering launcher": (
        "/engineering",
        ".engineering/bin/**",
        ".engineering/setup.sh",
    ),
}
MODULES = ".engineering/engineering/"
# Maintainer modules that execute dependencies, or destroy or publish data.
MAINTAINER_SENSITIVE = {
    "dependency module": (
        f"{MODULES}deps.py",
        f"{MODULES}registry.py",
        f"{MODULES}graft.py",
    ),
    "skill installation module": (f"{MODULES}skill_install.py",),
    "apply or transaction module": (f"{MODULES}apply.py", f"{MODULES}transaction.py"),
    "update module": (
        f"{MODULES}adoption.py",
        f"{MODULES}installation.py",
        f"{MODULES}updates.py",
    ),
    "migration module": (f"{MODULES}migrate/**", ".engineering/migrations/**"),
    "publication module": (f"{MODULES}publication*.py",),
    # docs-check implements the required documentation check.
    "verification module": (f"{MODULES}verification*.py", f"{MODULES}markdown.py"),
}
# Agent-policy files are never documentation: they change how agents behave.
AGENT_POLICY = (
    "CLAUDE.md",
    "AGENTS.md",
    "REVIEW.md",
    "ENGINEERING.md",
    ".claude/**",
    ".engineering/docs/**",
    "docs/agents/**",
)


def requirements(facts: RequirementFacts, plan: dict[str, Any]) -> dict[str, Any]:
    """Required checks, tier floor, per-path floor rules and reviewer roles.

    Rejects a plan that omits a required check or declares a tier below the
    floor. Checks come from recorded role and ownership, never from existing
    targets; the tier changes reviewers, never checks.
    """
    # The stricter of base and proposed role applies, so a role change counts
    # once merged (ADR 0001).
    role = "maintainer" if facts.base_role == "maintainer" else facts.role
    if GRAFT in plan["checks"] and facts.navigation not in (None, "graft"):
        raise ValueError(
            "navigation disabled: remove the Graft check from the plan, or "
            'select [navigation] provider = "graft"'
        )
    categories = classify(facts, role, plan["paths"])
    if (edited := categories["managed implementation"]) and not facts.starter_source:
        raise ValueError(
            f"Managed implementation edited in a consumer project: {edited}. "
            "Engineering owns these files, so verification cannot pass. Restore "
            "them; get changes through `./engineering update <project>` from a "
            "starter checkout (review the preview, then rerun with --apply), or "
            "propose the change upstream in the starter repository. For update output, "
            "declare starter_source with the repository and pinned commit in the "
            "verification plan. Proposed manifest digests cannot vouch for bytes."
        )
    paths = tier_paths(role, plan["paths"], facts.review)
    floor_non_prose_documentation(facts.paths, paths)
    prose = (
        len(paths["documentation"]) == len(plan["paths"])
        and categories["project"] == sorted(plan["paths"])
        and not facts.starter_source
    )
    required = required_checks(facts, role, categories, prose, plan["paths"])
    reject_missing_checks(facts, role, categories, prose, required, plan["checks"])
    if facts.starter_source:
        # The source is an explicit trust decision, including which repository
        # may vouch for executable code. Always obtain independent security review.
        for name in plan["paths"]:
            for tier in TIERS:
                paths[tier].pop(name, None)
            paths["sensitive"][name] = "pinned starter update source"
    floor = max((tier for tier in TIERS if paths[tier]), key=TIERS.index)
    reject_below_floor(plan["tier"], floor, paths)
    return {
        "floor": floor,
        "paths": paths,
        "checks": required,
        "roles": REVIEWERS[plan["tier"]],
    }


def required_checks(
    facts: RequirementFacts,
    role: str,
    categories: dict[str, list[str]],
    prose: bool,
    names: list[str],
) -> list[list[str]]:
    """Checks a plan must declare, from role, ownership and classified paths."""
    required = [[*DOCS, *sorted(names)]] if prose else [PROJECT]
    if (
        categories["project configuration"]
        or categories["managed integration"]
        or categories["installation metadata"]
        or facts.starter_source
    ):
        required.append(HEALTH)
    # In the maintainer checkout the metadata is the ownership contract every
    # consumer receives, so it is maintainer source as well as metadata.
    if categories["maintainer source"] or (
        role == "maintainer" and categories["installation metadata"]
    ):
        required += SUITES
    if facts.graft:
        required.append(GRAFT)
    return required


def reject_missing_checks(
    facts: RequirementFacts,
    role: str,
    categories: dict[str, list[str]],
    prose: bool,
    required: list[list[str]],
    declared: list[list[str]],
) -> None:
    """Name each missing check with the categories that required it."""
    if missing := [command for command in required if command not in declared]:
        reasons = [
            f"{category}: {', '.join(names)}"
            for category, names in categories.items()
            if names
        ]
        if prose:
            reasons.append("prose-only documentation needs documentation checks")
        if facts.graft:
            reasons.append("configured application roots require Graft check")
        raise ValueError(
            f"Required checks missing: {missing} (role {role}; {'; '.join(reasons)})"
        )


def reject_below_floor(
    declared: str, floor: str, paths: dict[str, dict[str, str]]
) -> None:
    """Name the paths and rules that set the floor a declared tier is below."""
    if TIERS.index(declared) < TIERS.index(floor):
        reasons = [f"{name} ({rule})" for name, rule in paths[floor].items()]
        raise ValueError(
            f"Declared tier {declared} is below the tier floor {floor}: "
            f"{', '.join(reasons)}. Declare at least {floor}."
        )


def floor_non_prose_documentation(
    facts: Mapping[str, PathFacts], paths: dict[str, dict[str, str]]
) -> None:
    """Floor documentation paths at ordinary unless they are prose files.

    Prose is decided by file type, not content (user decision 2026-10-14): a
    configured, present, non-executable Markdown file qualifies.
    """
    for name in list(paths["documentation"]):
        if reason := prose_reason(name, facts[name]):
            del paths["documentation"][name]
            paths["ordinary"][name] = reason


def prose_reason(name: str, facts: PathFacts) -> str | None:
    """Why a documentation path is not a prose file; None when it is."""
    if not name.endswith(SUFFIXES):
        return "unsupported documentation format"
    if not facts.present:
        return "deleted document"
    if facts.executable or facts.base_executable:
        return "executable file"
    return None


def tier_paths(
    role: str, paths: list[str], settings: tuple[Review, ...]
) -> dict[str, dict[str, str]]:
    """Floor each path under every review settings version; the highest tier wins."""
    result: dict[str, dict[str, str]] = {tier: {} for tier in reversed(TIERS)}
    for name in sorted(paths):
        tier, rule = max(
            (path_floor(role, name, review) for review in settings),
            key=lambda floor: TIERS.index(floor[0]),
        )
        result[tier][name] = rule
    return result


def path_floor(role: str, name: str, review: Review) -> tuple[str, str]:
    """The first matching rule; starter rules precede project settings."""
    sensitive = dict(STARTER_SENSITIVE)
    if role == "maintainer":
        sensitive.update(MAINTAINER_SENSITIVE)
    sensitive["project sensitive setting"] = review["sensitive"]
    for rule, patterns in sensitive.items():
        if matches(name, patterns):
            return "sensitive", rule
    if matches(name, AGENT_POLICY):
        return "ordinary", "agent policy"
    if name == CONFIGURATION:
        # Changing review settings is itself reviewed, whatever they list.
        return "ordinary", "review settings"
    if matches(name, review["documentation"]):
        return "documentation", "project documentation setting"
    return "ordinary", "no documentation rule"


def matches(name: str, patterns: tuple[str, ...]) -> bool:
    """Match file-name patterns at any depth and path patterns from the root."""
    return any(
        path_matches(name, pattern.removeprefix("/"))
        if "/" in pattern
        else fnmatchcase(PurePosixPath(name).name, pattern)
        for pattern in patterns
    )


def path_matches(name: str, pattern: str) -> bool:
    """A globstar directory may match zero directories as well as many."""
    if fnmatchcase(name, pattern):
        return True
    start = pattern.find("**/")
    if start < 0:
        return False
    return path_matches(name, pattern[:start] + pattern[start + 3 :]) or path_matches(
        name, pattern[:start] + "*/" + pattern[start + 3 :]
    )


def classify(
    facts: RequirementFacts, role: str, paths: list[str]
) -> dict[str, list[str]]:
    """Categorize each changed path by manifest ownership and installation role."""
    proposed = facts.proposed_ownership
    if proposed is None:
        raise ValueError(
            f"{MANIFEST_PATH} is missing; ownership cannot be classified. "
            "Restore the installation manifest before verification."
        )
    # Baseline ownership keeps a dropped entry from lowering requirements.
    owned = facts.base_ownership
    categories: dict[str, list[str]] = {
        "project configuration": [],
        "managed integration": [],
        "maintainer source": [],
        "managed implementation": [],
        "installation metadata": [],
        "project": [],
    }
    for name in sorted(paths):
        modes = {
            mode for mode in (proposed.get(name), owned.get(name)) if mode is not None
        }
        if role == "maintainer" and (
            "file" in modes or name.startswith(MAINTAINER_TOOLING)
        ):
            category = "maintainer source"
        elif "file" in modes and facts.paths[name].changed:
            # Manifest digests are proposed content too, so they never vouch
            # for an edit or removal; a fetched starter source must vouch for it.
            category = "managed implementation"
        elif modes == {"preserve"}:
            category = "project configuration"
        elif modes:
            # Integration sections, hooks and unchanged distributed files.
            category = "managed integration"
        elif name in METADATA:
            category = "installation metadata"
        else:
            category = "project"
        categories[category].append(name)
    return categories
