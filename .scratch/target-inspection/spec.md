# Read-only target inspection

Status: in progress

## Scope

Implement `agentic inspect TARGET` from the agreed [product direction](../../docs/product-direction.md).
Report target setup, recognized legacy v2 remnants, installed tool metadata,
convention differences, local additions/edits, installed skills and recorded revisions.
Recommend init for a nonexistent destination, adoption for an existing workspace,
and minimal adoption for recognized legacy installations. State Git prerequisites
without preventing inspection of uncommitted or non-Git projects.

Compare current configuration against the recorded installed baseline and this
checkout's templates. Distinguish missing, project-owned, current, local additions,
local edits, available updates and overlapping edits. Do not certify qualitative
code adherence or claim a recorded skill commit proves installed contents unchanged.

Read only bounded configuration/skill files. Refuse symlinks, conflicting metadata,
malformed records and invalid target types with useful errors. Do not read secrets,
execute target commands, fetch network data or create target files. Existing
.starter metadata remains supported. Exit zero for a successful advisory report,
even with differences; exit nonzero when inspection cannot complete safely.

## Verification

Use the existing external CLI and filesystem seams in disposable projects.
Exercise greenfield, ordinary brownfield, real archived v2, installed/customized
guidance, skill inventory, duplicate exposed skill names and malformed/unsafe input.
Assert no target mutations. Run native checks and committed-diff Standards/Spec review.

## Exclusions

No apply mode, JSON API, online freshness checks, automatic skill updates, profiles,
or unified onboarding. No remote publication or merge implied by this feature.
