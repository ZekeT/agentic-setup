# Read-only target inspection

Status: implemented and reviewed; awaiting merge

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

## Results

`make check` after review correction: Ruff lint/format, mypy and 30 tests passed
(58.27 seconds). New tests cover real archived v2, ordinary non-Git setup,
three-way convention comparison, both metadata layouts, recorded/missing/duplicate
skills, malformed records/configuration and symlink refusal. Snapshot assertions
verify target contents remain unchanged; a package script that would write a file
is never executed. CLI behavior tests were reproduced red before implementation.

Additional CLI smoke verified unborn Git, nested workspace recommendations,
regular-file target rejection, conflicting metadata, self-inspection and the local
HumanLayer revision record. Six local documentation links passed.

Matt Standards review found directory traversal before skill-entry symlink validation
and duplicated inventory parsing. The shared bounded skill inventory resolves both;
the new symlink-without-SKILL.md regression failed before correction and passes now.
Standards and Spec follow-up on a1e1485...1af2112 report zero remaining findings.

No remote publication, live target migration or online freshness check performed.
The pre-existing untracked .agentic-setup skill records were preserved unchanged.

## Shared comparison follow-up

The user accepted the review recommendation to share template comparison before PR
publication. A pure comparison now owns both report classifications and safe replacement
content; inspection renders its result and the updater builds its plan from that result.
Eight CLI agreement cases cover current, already-updated, local additions/edits,
replaceable templates, preserved additions, conflicts and missing files.

Final `make check`: Ruff lint/format, mypy and 38 tests passed (40.62 seconds).
Independent parallel Standards/Spec review of 92e673a...45d23aa reported zero findings
on both axes, resolving the prior optional duplication concern. The reviewer also
compared 504 input combinations against previous updater decisions without discrepancies.
The subsequent request authorizes publishing this feature PR; merge remains separate.
