"""Gather the repository facts that verification requirements are decided from."""

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .config import object_value
from .installation import MANIFEST_PATH, ROLES, STATE_PATH, installation_role
from .ownership import json_object, read_bytes, validate_ownership
from .settings import (
    CONFIGURATION,
    graft_navigation,
    provider,
    review_settings,
    validate,
)
from .verification_git import Baseline
from .verification_source import verify_update

# Review settings as documentation and sensitive path patterns.
Review = Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class PathFacts:
    """What one planned path holds in the proposed checkout and at the base."""

    present: bool
    changed: bool
    executable: bool
    base_executable: bool


@dataclass(frozen=True)
class RequirementFacts:
    """Plain, immutable inputs to requirement decisions; no repository handles.

    Ownership maps a manifest path to its ownership mode; the proposed manifest
    is None when absent. Review holds the base, then the proposed, settings.
    Navigation is the selected provider, None without project configuration.
    """

    role: str
    base_role: str | None
    proposed_ownership: Mapping[str, str] | None
    base_ownership: Mapping[str, str]
    review: tuple[Review, ...]
    navigation: str | None
    graft: bool
    starter_source: bool
    paths: Mapping[str, PathFacts]


def gather(
    checkout: Path,
    base: Baseline,
    plan: dict[str, Any],
    starter_source: dict[str, Any] | None = None,
) -> RequirementFacts:
    """Read each fact once; reject unreadable or invalid inputs while reading.

    The checkout holds the proposed content; base holds the comparison base's blobs.
    """
    # The recorded role is trusted (ADR 0001); absence blocks planning.
    role = installation_role(checkout)
    configured = (checkout / CONFIGURATION).is_file()
    if configured:
        # Invalid project configuration fails planning visibly, not only doctor.
        try:
            validate(checkout, (checkout / CONFIGURATION).read_text())
        except tomllib.TOMLDecodeError as error:
            raise ValueError(f"{CONFIGURATION}: {error}") from error
    proposed = manifest_files(read_bytes(checkout, MANIFEST_PATH))
    owned = manifest_files(baseline(base, MANIFEST_PATH)) or {}
    if "starter_source" in plan:
        if starter_source is None:
            raise ValueError("Pinned starter source evidence is missing")
        verify_update(checkout, starter_source, owned)
    review = (
        review_settings(baseline(base, CONFIGURATION)),
        review_settings(read_bytes(checkout, CONFIGURATION)),
    )
    paths = {}
    for name in plan["paths"]:
        raw = read_bytes(checkout, name)
        paths[name] = PathFacts(
            present=raw is not None,
            changed=raw != baseline(base, name),
            executable=raw is not None
            and bool((checkout / name).stat().st_mode & 0o111),
            base_executable=base.get(name, ("",))[0] == "100755",
        )
    return RequirementFacts(
        role=role,
        base_role=baseline_role(base),
        proposed_ownership=None if proposed is None else ownership_modes(proposed),
        base_ownership=ownership_modes(owned),
        review=tuple(MappingProxyType(settings) for settings in review),
        navigation=provider(checkout, "navigation") if configured else None,
        graft=configured and graft_navigation(checkout),
        starter_source=starter_source is not None,
        paths=MappingProxyType(paths),
    )


def ownership_modes(files: dict[str, Any]) -> Mapping[str, str]:
    """Each validated manifest entry's ownership mode."""
    return MappingProxyType(
        {name: entry["ownership"]["mode"] for name, entry in files.items()}
    )


def baseline_role(base: Baseline) -> str | None:
    """The comparison base's recorded role, or None before it was recorded."""
    raw = baseline(base, STATE_PATH)
    role = None if raw is None else json_object(raw).get("role")
    return role if role in ROLES else None


def baseline(base: Baseline, name: str) -> bytes | None:
    """A path's bytes at the comparison base, None when absent."""
    entry = base.get(name)
    return None if entry is None else entry[1]


def manifest_files(raw: bytes | None) -> dict[str, Any] | None:
    """Validate the ownership of every manifest entry before trusting it."""
    if raw is None:
        return None
    files = object_value(json_object(raw).get("files"), f"{MANIFEST_PATH}: files")
    for name, entry in files.items():
        if not isinstance(entry, dict):
            raise ValueError(f"{MANIFEST_PATH}: invalid entry {name}")
        validate_ownership(name, entry.get("ownership"))
    return files
