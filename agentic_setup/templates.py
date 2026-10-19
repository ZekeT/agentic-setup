"""Pure comparison of project guidance, its installed baseline and an incoming template."""

from dataclasses import dataclass
from enum import Enum


class TemplateStatus(Enum):
    MISSING = "missing"
    PROJECT_OWNED = "project-owned; no installed baseline"
    CURRENT = "current"
    LOCAL_ADDITIONS = "local additions; template unchanged"
    LOCAL_EDITS = "local edits; template unchanged"
    UPDATE = "update available"
    UPDATE_WITH_ADDITIONS = "update available; local additions preserved"
    CONFLICT = "conflict; template and project both changed"


@dataclass(frozen=True)
class TemplateComparison:
    status: TemplateStatus
    replacement: bytes | None = None


def compare_template(
    local: bytes | None, previous: bytes | None, incoming: bytes
) -> TemplateComparison:
    if local is None:
        return TemplateComparison(TemplateStatus.MISSING)
    if previous is None:
        return TemplateComparison(TemplateStatus.PROJECT_OWNED)
    if local == incoming:
        return TemplateComparison(TemplateStatus.CURRENT)
    intact = bool(previous) and local.count(previous) == 1
    if previous == incoming:
        return TemplateComparison(
            TemplateStatus.LOCAL_ADDITIONS if intact else TemplateStatus.LOCAL_EDITS
        )
    if local == previous:
        return TemplateComparison(TemplateStatus.UPDATE, incoming)
    if intact:
        return TemplateComparison(
            TemplateStatus.UPDATE_WITH_ADDITIONS,
            local.replace(previous, incoming, 1),
        )
    return TemplateComparison(TemplateStatus.CONFLICT)
