# Agentic Setup

Configure target workspaces with your development conventions and selected agent
skills, then adopt changes through explicit, scoped updates.

Clone `ZekeT/agentic-setup` separately from your target workspaces. Run `./agentic`
from this checkout; optionally add the checkout to PATH to call `agentic` anywhere.

A small setup for Matt Pocock's development workflow. Applications use their own
checks and installed skills; Agentic Setup runs only when you explicitly install or
update guidance. This repository is the setup tool's source: its `.scratch/`, docs
and tests maintain the tool itself. Every target project owns its own docs, tracker
and application. Only selected guidance and skills are installed; the tool's code,
plans and history stay here. See [product direction](docs/product-direction.md)
for the agreed scope and [architecture](docs/architecture.md) for the boundary.

Python 3.11+ and Git are **installer prerequisites**, not application
requirements. The launcher uses an available versioned Python executable when the
system python3 is older. No Node, uv, Makefile or Python application stack is imposed.

## Inspect a target first

```bash
./agentic inspect /path/to/project
```

Inspection is read-only and also accepts a new destination or an existing directory
without Git commits. It reports installed metadata, recognized v2 files, missing
configuration, differences from recorded template baselines, project-owned guidance,
local additions/edits, and potential update conflicts. It inventories project-local
skills and recorded revisions, including missing files and duplicate exposed names.

The report recommends initialization, adoption or minimal v2 adoption and explains
Git prerequisites. Native command candidates are shown but never executed. Existing
`.starter/` metadata is supported. Differences are advisory: exit 0 means the report
completed, not that the project complies with every convention. Unsafe paths or
malformed configuration return an error without modifying the target.

Checks are limited to bundled guidance, known legacy paths, bounded setup documents
and skill directories. This does not certify application code quality, traverse all
instruction imports, verify installed skill contents against upstream, or check
online for newer versions. A recorded revision differing from the historical reference revision
is not necessarily outdated. Use `agentic skills check` for an explicit online revision check; installation and
update commands below also fetch only when requested.

## Move an existing starter project first

From this external Agentic Setup checkout, against a committed Git project:

```bash
./agentic adopt /path/to/project --minimal
./agentic adopt /path/to/project --minimal --apply --expect TOKEN
```

For a readable before/after report, add `--html` with a new filename outside the
target workspace:

```bash
./agentic adopt /path/to/project --minimal --html /tmp/adoption-preview.html
```

Open the saved HTML locally. It shows conflicts first, change counts, preservation
notes and expandable side-by-side file comparisons. Blocked previews still save a
report and return exit 1; the proposed changes remain unapplied. Binary and large
files show byte counts and hashes instead of a content diff. The report embeds no
scripts or external resources, but may contain project configuration; keep it local.

`--html` also works with `agentic update` and `agentic skills install/update` previews.
It cannot be combined with `--apply`; existing output files and paths inside the
target are refused. Choose a new filename for each preview. Resolve conflicts by
refining Agentic Setup here and previewing again. For live target workspaces, only
an explicitly approved Agentic Setup apply operation should make changes; do not
edit target files or run target-mutating commands as a preview workaround.

Use the `PREVIEW` token from the first command. Preview reads configuration only;
it does not install dependencies or modify the target. Apply rejects stale content
and affected uncommitted files, while preserving unrelated staged/unstaged work.
Add `--check 'npm test'` (or the project's agreed native command) to apply to run
that command before and after. A failing check is reported with both exit codes;
installation does not pretend unrelated debt is fixed. Without `--check`, native
verification is explicitly unverified. Commands execute project code; inspect them.

The tool recognizes exact historical starter files and marked sections from its
catalog. It disconnects old review, evidence, publication and installer gates,
keeps useful protection hooks and installed skills, and preserves application
source, tests, dependencies, specs, tickets and ADRs. Customized active policy,
CI or imports become conflicts before writes. Customized dormant files are reported
and retained. Unknown older layouts need a reviewed manual patch, not deletion.
Ignored local evidence/state is left alone. Remote required checks need separate
inspection; local adoption cannot change branch protections.

Review `git diff`, run the recorded native checks, and commit only the transition
paths as a dedicated infrastructure commit. Then resume the next existing ticket
with `/implement`. Roll back later with `git revert <transition-commit>`; never
reset later application work. Before committing, restore only changed tracked
paths from the reported baseline and remove only newly added installer files after
checking that they are unchanged. Ordinary write errors restore touched bytes and
modes; after a process kill/power loss inspect the scoped diff against the baseline.

## New and ordinary existing projects

```bash
./agentic init /path/to/new-project
# Optional application code, only if wanted:
./agentic init /path/to/new-python-project --python-seed

./agentic adopt /path/to/existing-project
./agentic adopt /path/to/existing-project --apply --expect TOKEN
```

Initialization refuses an existing destination. Adoption preserves existing native
commands, package managers, standards, settings and tracker configuration. Confirm
that discovered standards cover the project’s needs. `docs/agents/checks.md` records
discovered native command candidates as unverified until exercised. Resolve conflicting old requirements before considering adoption done.
Commit the configuration before installing additional skills. Existing OpenSpec
application artifacts are preserved; no OpenSpec conversion feature is included.

## Check upstream skill revisions

```bash
./agentic skills check /path/to/project
./agentic skills check /path/to/project --bundle show-me
```

This is an explicit online, read-only check of recorded supported skills. It resolves
upstream default-branch HEAD once per relevant source in a temporary checkout, then
compares Git ancestry: **current**, **behind**, **ahead**, or **diverged**. Recorded
commits unavailable upstream, unrelated history and unknown sources report **unknown**.
Repository advancement does not necessarily change a selected skill, and a matching
revision does not verify installed bytes or certify compatibility.

Missing or duplicate recorded installations are reported. Unrecorded skills are left
unclassified; their source is never guessed. The command accepts older commit-only
records and `.starter/` metadata. It contacts only configured bundle repositories,
never URLs supplied by target metadata. No supported records means no network access.
A failed source produces a partial report; other sources are still checked.

Exit 0 means comparisons completed (including available updates or no recorded skills).
Exit 1 means an incomplete check, missing/duplicate recorded installations or invalid
input. Target files and Git state are unchanged; there is no cache or background check.
Use `skills update` to preview actual file changes and check for local conflicts.

## Install and update selected skills explicitly

Install defaults to the selected upstream repository's latest default-branch commit.
It prints the resolved commit and previews target changes. Replay that commit with
`--ref` when applying so a moving upstream does not invalidate your preview:

```bash
./agentic skills install /path/to/project --bundle matt
./agentic skills install /path/to/project --bundle matt --ref RESOLVED_COMMIT --apply --expect TOKEN

./agentic skills update /path/to/project --bundle matt
./agentic skills update /path/to/project --bundle matt --ref RESOLVED_COMMIT --apply --expect TOKEN
```

`RESOLVED_COMMIT` is the full hash printed in the `SOURCE` line. `TOKEN` is the
`PREVIEW` value. Fetching uses a temporary external checkout, removed after planning;
it does not modify the target during preview. No remote checks happen during normal
development or `agentic inspect`. Latest means upstream HEAD, not a compatibility
certification. Bundle selections remain explicit; missing upstream names require
review instead of silently choosing different skills.

For offline use, supply `--from /path/to/clean-upstream-checkout`. Its current committed
HEAD is the selected revision, with no fetch or checkout changes. An optional `--ref`
must match that HEAD. Local checkouts are explicitly trusted sources for the chosen
bundle; the tool does not independently authenticate their origin.

Initialize Git and commit first for new targets. Installation copies selected skill
files into `.claude/skills/`, recording source, commit and file hashes. Existing exposed
skills are preserved; installation never shadows a local skill. Updates change only
recorded bundle skills: unchanged managed files can be replaced or deleted when removed
upstream, and deletions must also match the recorded upstream Git tree. If that older
commit is unavailable (for example in a shallow offline checkout), deletion is blocked;
provide a checkout containing that revision. Locally modified/deleted files, incoming paths that overlap project additions,
relocated skills and duplicate names require reconciliation. Unrelated project-added
files remain untouched. Commit affected configuration before apply; repeat updates are
no-ops. Upstream licenses are retained by revision; old licenses are not overwritten.

Older records containing only source and commit need a verified file baseline first.
Preview `skills install` with `--ref RECORDED_COMMIT` (or its clean `--from` checkout),
then apply with that preview token. The tool adds hashes only if all installed skill
bytes match the recorded revision. Commit that metadata before updating. Unrecorded or
customized skills remain project-owned; no ownership is guessed from their names.

| Bundle | Upstream | Selection |
| --- | --- | --- |
| matt | mattpocock/skills | Selected planning, implementation, TDD, review and PR skills |
| show-me | humanlayer/skills | show-me |
| verification | backnotprop/pstack | create-verification-skill, maintain-verification-skill |

Claude discovers `.claude/skills`; other runtimes may read the same SKILL.md directly.
Check each selected skill's runtime/subagent requirements. Run `/setup-matt-pocock-skills`
to confirm tracker/domain setup, preserving the project's existing choices.

The verification bundle pairs create-verification-skill with its maintenance skill.
Use it once runnable behavior exists; exercise one real recipe before claiming it
works. Missing application environments remain a disclosed gap, not an adoption
gate. Optional model-heavy investigations and architecture work remain separate.

## What do you want to do?

| Need | Use |
| --- | --- |
| Configure tracker/domain docs | /setup-matt-pocock-skills |
| Clarify a change | /grill-me; /wayfinder for large uncertain work |
| Plan agreed scope | /to-spec → /to-tickets |
| Implement and test | /implement with Matt's /tdd |
| Review final changes | /code-review against intended PR target |
| Understand the result | show-me briefing; deeper how/why investigation when useful |
| Prepare a PR description | explanation first, then /pr |
| Improve architecture | Matt's selected codebase-design; advisory, user-invoked |
| Learn from recurring problems | /retro |

Checkpoint intended final changes before Matt's committed-diff review and review
later corrections too. This is the narrow compatibility decision for the pinned
/implement skill, which asks for review before its final commit. No synthetic
commits, duplicate reviewer or custom ledger is needed. Use native checks once at
appropriate completion boundaries and recheck affected behavior after fixes.
Security assessment is a separate user-invoked read-only review.

Read `docs/agents/git-workflow.md` for direct, personal-integration and fork routing.
Default to PR-description preparation and manual creation. Publication, promotion,
merge and force-push are separate authorizations.

## Explicit later updates

Use a separate checkout of a known Agentic Setup commit/release. No per-session fetch,
update check, mandatory upgrade or application-time digest validation runs.

```bash
./agentic update /path/to/project --only explanation --source-ref FULL_COMMIT
./agentic update /path/to/project --only explanation --source-ref FULL_COMMIT --apply --expect TOKEN
```

Scopes: explanation, git, workflow, standards. Only the selected template changes.
An intact old template surrounded by project additions can update safely; overlapping
edits require a reviewed manual merge. Reapplying is a no-op. Existing project-owned
guidance is never claimed. The compact `.agentic-setup` record stores installation
baselines and skill installation records only. Use `agentic skills update` for explicit
skill upgrades. Overlapping skill edits and feature removals still require reviewed
scoped patches; preserve custom extensions, run relevant checks and commit separately.
There is no automatic upstream skill merge or generalized feature-removal engine.

[Maintainer details](CONTRIBUTING.md) describe tests and the preserved baseline.

## Naming and release compatibility

Agentic Setup replaces the Agentic Starter name. This branch uses `agentic`, the
`agentic_setup/` implementation package and `.agentic-setup/` installation metadata.
The published v3.0.0 tag retains its original `engineering` command and names.
Existing `.starter/` installation records and licenses continue to be used in
place; do not rename or duplicate them to upgrade. Conflicting metadata records
in both locations require manual reconciliation. New workspaces use the new name.

The skill installation command is `agentic skills install`; `agentic inspect` reports
local setup and recorded revisions. `agentic skills update` previews explicit upgrades.
`agentic skills check` explicitly compares recorded revisions with upstream. Development conventions is the term for shared workflow, Git
preferences, standards and configuration; no profile abstraction is introduced.
