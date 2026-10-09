---
description: Publish the accepted unchanged scope using current independent evidence.
---

Read REVIEW.md, .engineering/docs/publication.md and
.engineering/docs/commits-and-prs.md. Inspect the intended diff and saved acceptance
summary, including committed, staged, unstaged and intended new paths. Completed
acceptance review is required; invoking /ship cannot supply missing review.

After completed review, /ship expresses human acceptance of the presented unchanged
scope and authorization to commit remaining accepted fixes, push and create the
actual PR/MR when blockers are resolved. Honor narrower requests and existing
explicit authorization. Never infer publication permission from /implement.
Never merge or force-push without separate specific authorization.

Consume the Markdown draft prepared with Matt's unchanged /pr skill. If no draft
exists, ask for /pr before PR publication; do not generate a competing body or
wrap the skill. Present the draft and record it with the acceptance plan using
engineering publish review --body-file <repository-relative-path>. The recorded
text is frozen; do not silently replace it with later file edits. Record revised
presented drafts before publication and honor authorization for that exact plan.
Commit-only and push-only requests do not require a PR body. The GitHub template
remains available for manual authoring.

Use engineering publish preflight to check intended content/paths, current proof,
comparison base, branch/remote and unresolved blockers. Preflight recomputes the
tier floor for the current scope and refuses evidence whose tier is below it.
Missing or stale evidence or classification returns to verification;
missing/stale acceptance summary or blockers return to /review and
human-directed corrections. Reuse current semantic review and checks;
do not rerun unchanged authoritative checks during shipping.

Use engineering publish run with only the human-authorized commit/push/pr scope.
Reuse implementation commits and stage only accepted paths. Preserve unrelated
working and staged files. Hooks remain enforced; failures stop publication and
hook content mutations require reassessment before transport. Use the configured
provider, not an assumed GitHub repository. A PR body draft is not publication:
report the actual PR/MR URL, scope and useful test evidence. On failure report
completed steps, the failed or uncertain operation and the concrete recovery action.
After restoring connectivity, use engineering publish run --change <change> to
reuse saved scoped authorization and current evidence. The command reconciles
actual Git/provider state, reuses the existing commit and PR/MR, and skips an
already completed push. A transport failure alone does not repeat verification.
Stop on uncertain lookup or changed inputs; never recover with automatic force-push.

The implementer may run the initial full applicable suite through `verify check`.
Fresh behavioral inspection consumes its recorded results without repeating it.
For carried snapshots only, existing review reports may accompany fresh checks. A clean rebase
can carry independent reports through `verify prepare` when the own patches,
plan, tools and checks are unchanged and upstream paths do not overlap scope or
explicit inputs. Reports record `carried_from`; fresh checks are required before
PASS. Failed checks drop the carried behavioral report and require independent
review. Other changes follow review corrections; never self-certify or manually
relabel reports. Publication accepts current carried PASS evidence and still
requires the remote base tip recorded at the latest prepare.
