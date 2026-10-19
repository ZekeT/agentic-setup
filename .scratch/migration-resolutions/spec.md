# Project-specific migration resolutions

Status: in progress

Keep reusable adoption logic separate from project decisions. Store each target's
local artifacts in migrations/<workspace-name>/, ignored by Git. Add optional
`--html` (without a path) to create the next preview-NNN.html there. Existing explicit
HTML paths still work. Add `adopt --resolutions FILE` to load an explicit external
resolution plan; do not silently discover or apply one.

Version-1 JSON identifies the canonical target path and a list of distinct path
operations. Each operation has a reason and expected_sha256 of current target bytes
(null means absent). Supported actions: delete, replace_text (one exact occurrence),
json_remove (one exact value from a selected JSON array), replace_file (external
replacement file relative to the resolution plan). Edits act on the default proposed
content when one exists, otherwise current content. Replacement files specify the
whole final file. Reject unknown fields/actions, duplicate paths, malformed hashes,
ambiguous edits, wrong targets, symlinks, traversal and secret/Git paths. Limit edits
to configuration files already inspected by adoption; never source/data sweep rules.

Apply resolutions after default proposals, replacing only their path's proposal and
customized-legacy conflict. Recheck active wiring against the final plan; no blanket
ignore-conflict option, shell commands or bypass of global/remaining conflicts.
A resolution can preserve a file by supplying its current contents; stale default
notes/proposals must not survive that override. Keep installed template baselines as
the upstream templates so explicit project overrides remain distinguishable.

Tokens bind resolution JSON, replacement bytes and resulting plan; changed inputs
require a fresh preview. Existing tracked edits still block apply. Explicitly resolved
untracked/ignored files may be modified only after a recovery snapshot is successfully
saved under the external migration folder, recording before bytes/modes and after
hashes. All resolution applies create recovery snapshots before any target writes.
Existing in-memory rollback remains for ordinary write failures. Preview creates no
recovery files or target changes. Do not implement a broad backup/restore service.

HTML includes resolution action/reason and remaining conflicts. CLI and report name
recovery location. All resolution and report paths remain outside the target; report
folder auto-creation must not introduce a target-write loophole.

Test through existing CLI/filesystem seams with disposable repositories: valid actions,
blocked stale/ambiguous inputs, active-wiring revalidation, unchanged target during
preview, accurate overrides, token binding, guarded apply with recovery, preserving
unrelated work and unique automatic report names. Run native checks and Standards/Spec
review. Prepare the uc3-lane-watch plan and HTML only; never apply, mutate its Git state,
execute its application commands or directly edit its files. Publication is separate.
