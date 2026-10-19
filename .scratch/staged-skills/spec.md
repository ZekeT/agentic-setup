# Stage external skill installations

Status: implementing

## Problem

Custom skill ownership/update logic is growing beyond Agentic Setup's purpose.
The skills@1.7.2 trial proved project installation works, but check is an update
alias and installs overwrite existing customized files. See docs/product-direction.md.

## Accepted design

Keep skills install/update/check commands. Delegate sourcing, selection and lock
creation to pinned npm skills@1.7.2, running only in an external staging directory.
Preview captures before and proposed bytes, modes, directories and supported relative
Claude aliases. Save the self-contained plan under migrations/<project>/ with an HTML
comparison and token. Apply requires --plan PATH --apply --expect TOKEN, uses no npm,
Node, Git fetch or upstream download, and verifies target baseline and captured scope.
A --from clean checkout is an explicit trusted local source for offline previews;
--ref selects an explicit GitHub commit only for previews. Multiple --bundle values
allow Matt and show-me in one approved transition. Update selects installed bundle
members; install also adds missing members. No source URL from target records is
executed. Node/npm are needed only to generate online previews/checks.

Canonical files live in .agents/skills; Claude links point exactly to the matching
canonical directory. Reject other symlinks, protected paths, renamed/duplicate skill
exposures, command collisions and unsupported output. Inspect must recognize aliases
as one skill. Lockfiles belong to the external installer; migrated selected entries
are removed from old .agentic-setup/skills.json (or .starter equivalent), preserving
unrelated records, licenses and convention installation baselines.

Display all changes, including deletion of extra skill files. Existing unrecorded
skills can be transitioned by explicit approval of the exact diff; never invent their
history. No automatic merge or local-edit provenance claim. Capture all original
bytes for recovery before touching target. Quiescent target required. Use bounded
same-filesystem moves with ordinary-failure rollback; preserve unrelated dirty work.
Reject changed snapshots, staged content, modes, baseline, scope, and stale tokens.
No generic arbitrary-file deletion engine. Apply cannot change unrelated configuration.

Check compares selected installed skills with freshly staged upstream output and
reports content/record differences; it does not certify compatibility or local-edit
provenance and never invokes the external check/update command against a target.

## Testing

Use the established public CLI/file-outcome seam in disposable Git repositories.
An external npm-process fixture supports deterministic offline unit journeys; this
is a boundary double, not a mock of Agentic Setup. Also run real pinned installer
integration on disposable projects, and generate a read-only UC3 preview.
Cover offline apply after upstream changes, tampering/staleness, symlink containment,
exact backup/rollback, lock validation, scoped migration, alias inspection and readonly
check. Replace tests enforcing retired custom skill-record/revision semantics with
these new behavioral contracts; retain unaffected adoption/update/inspection tests.

## Out of scope

No live-target apply, app execution, publication, arbitrary skill discovery, automatic
merges, restore command, or replacement of convention baselines. Source trial artifacts
remain local under migrations. User reviews the executable UC3 preview before apply.
