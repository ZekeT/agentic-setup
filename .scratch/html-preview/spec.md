# Readable HTML transition previews

Status: in progress

Provide `--html PATH` on adopt, scoped update and skill install/update previews.
Keep existing terminal output, exit status and preview token. Save a standalone,
readable HTML report outside the target with target/baseline/token, action counts,
conflicts first, preserved guidance and expandable side-by-side before/after file
diffs. A blocked plan must never imply its proposed changes were applied or that
conflicted content has an approved replacement. Show available current contents for
conflicts without inventing a resolution. Explain safe next steps and regenerate
previews after refining the tool; only apply following explicit user approval.

No target modifications from report generation. Reject --html with --apply before
planning; reject target-contained output, symlinks and existing report files. Do not
read extra target files for rendering or alter the plan/token. Escape all embedded
paths, notes and content; no scripts, external resources or executable file content.
For binary or oversized content, show byte counts and hashes with an explicit omission
notice rather than silently truncating or performing unbounded diffs. Reports can
contain project configuration and should be handled as local review artifacts.

Verify through existing CLI/filesystem seams: HTML before/after content, conflicts,
HTML escaping, stable preview token, no target changes (including Git), unsafe
output and preview-only enforcement. Exercise no-change and bounded binary/large
file reports as relevant. Generate the user's actual adoption preview through the
CLI only, writing outside the target. No target edits, Git mutations, application
commands, apply, branch creation in target or remote publication are authorized.
