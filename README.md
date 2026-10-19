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
system python3 is older. Skill preview/check additionally needs Node/npm; frozen
apply does not. No application package manager or Python stack is imposed.

## Inspect a target first

```bash
./agentic inspect /path/to/project
```

Inspection is read-only and also accepts a new destination or an existing directory
without Git commits. It reports installed metadata, recognized v2 files, missing
configuration, differences from recorded template baselines, project-owned guidance,
local additions/edits, and potential update conflicts. It inventories project-local
skills and external lock records (or legacy revisions), including missing files and
duplicate exposed names. Canonical Claude aliases count as one installation.

The report recommends initialization, adoption or minimal v2 adoption and explains
Git prerequisites. Native command candidates are shown but never executed. Existing
`.starter/` metadata is supported. Differences are advisory: exit 0 means the report
completed, not that the project complies with every convention. Unsafe paths or
malformed configuration return an error without modifying the target.

Checks are limited to bundled guidance, known legacy paths, bounded setup documents
and skill directories. This does not certify application code quality, traverse all
instruction imports, verify installed skill contents against upstream, or check
online for newer versions. A recorded revision differing from the historical reference revision
is not necessarily outdated. Use `agentic skills check` for an explicit staged content comparison; installation and
update commands below also fetch only when requested.

## Move an existing starter project first

For agent-assisted migration, use the [migration agent guide](docs/migration-agent-guide.md).
It covers project-specific decisions and the preview/approval boundary for the three
existing projects; no self-service resolution interface is needed.

From this external Agentic Setup checkout, against a committed Git project:

```bash
./agentic adopt /path/to/project --minimal
./agentic adopt /path/to/project --minimal --apply --expect TOKEN
```

For a readable before/after report, add `--html`:

```bash
./agentic adopt /path/to/project --minimal --html
```

Reports are numbered under `migrations/<workspace-name>/` in this checkout.
Supply `--html PATH` to choose an explicit new filename outside the target. Generated
reports are ignored by Git; `/migrations/` would mean the filesystem root.

Open the saved HTML locally. It shows conflicts first, change counts, preservation
notes and expandable side-by-side file comparisons. Blocked previews still save a
report and return exit 1; the proposed changes remain unapplied. Binary and large
files show byte counts and hashes instead of a content diff. The report embeds no
scripts or external resources, but may contain project configuration; keep it local.

`--html` also works with `agentic update` and `agentic skills install/update` previews.
It cannot be combined with `--apply`; existing output files and paths inside the
target are refused. Automatic numbering keeps earlier previews. Resolve project-specific
conflicts with an external plan, then preview again:

```bash
./agentic adopt /path/to/project --minimal --resolutions migrations/project/resolutions.json --html
```

See [resolution plans](migrations/README.md) for the JSON format, supported actions and
recovery behavior. The file binds the target and current hashes; it is never loaded
automatically. Saving it does not authorize apply. For live target workspaces, only
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
and retained. Unknown older layouts need an explicit resolution plan or a tested tool extension,
not direct target edits or blanket deletion.
Ignored local evidence/state is left alone. Remote required checks need separate
inspection; local adoption cannot change branch protections.

After approved application, inspect the scoped diff read-only and report actual checks
and recovery information. The human manages target commits and any later Git revert;
agents must not modify target Git state or restore files directly as a workaround.
Resolution applies keep external originals under the migration folder. Ordinary write
errors restore touched bytes and modes; after interruption, inspect the state before
proposing recovery. No automatic restore command is currently available.

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

## Install, update and check skills

Agentic Setup delegates skill sourcing to **skills@1.7.2**, through Node/npm, only
inside a temporary workspace. Skills live in `.agents/skills/` with matching relative
Claude links in `.claude/skills/`. The external installer's `skills-lock.json` owns
source/path/content-hash records. `.agentic-setup/install.json` still owns convention
baselines; it does not run during development.

```bash
# Prepare and save a proposal; the target stays unchanged.
./agentic skills install /path/to/project --bundle matt --bundle show-me --html

# After reviewing: use the printed PLAN path and PREVIEW token.
./agentic skills install /path/to/project --plan migrations/project/skills-001.json --apply --expect TOKEN

# Later, preview updates to installed members of the selected bundle.
./agentic skills update /path/to/project --bundle matt --html
./agentic skills update /path/to/project --plan migrations/project/skills-002.json --apply --expect TOKEN

# Read-only comparison against freshly staged upstream content.
./agentic skills check /path/to/project
./agentic skills check /path/to/project --bundle show-me
```

Apply uses the saved bytes and modes, **without Node/npm or downloads**. It rejects
changed target contents, directory membership, modes, baseline, or proposal token.
Stop writers before apply. Recovery lives beside the plan under `backups/<token>/`;
ordinary move failures roll back. Recovery must share the target's filesystem.
Interrupted-process recovery is manual; do not overwrite later project work.

`--plan PATH` chooses the output file during preview and the input during apply.
Existing outputs are never overwritten. Default plans and HTML reports live under
this checkout's `migrations/<project>/`. Apply omits `--bundle`, `--from`, `--ref` and
`--html`; the saved proposal already contains those decisions. Keep plans private:
they contain original and proposed skill bytes.

Install includes missing bundle members and can explicitly migrate unrecorded skills.
Update selects already installed or recorded bundle members. Both show the full
proposal, **including replacement of customizations and deletion of extra files**.
Approval authorizes that exact diff; there is no automatic merge or guessed revision
history. Decline and refine the proposal when it would discard useful project rules.
Unrelated skills and application work stay untouched. Renamed/duplicate exposures,
command collisions and unsupported symlinks block staging. Supported canonical
Claude aliases count as one installation in `inspect`.

Selected entries retire from legacy `.agentic-setup/skills.json` or `.starter/skills.json`
only in the approved transition. Unrelated entries, old licenses and convention
baselines remain. The external lock records folder content hashes, not necessarily
full upstream commit revisions; compatibility is not certified by a matching hash.

Preview defaults to current upstream. `--ref FULL_COMMIT` selects a GitHub revision.
For a trusted clean local source, `--from /path/to/checkout` supports one bundle;
an optional `--ref` must match its HEAD. Node/npm and a cached installer are still
needed to prepare offline proposals. The resulting local source record is relative
to the target project, not the temporary workspace. No target record supplies an
executable source URL: checks and future default previews use configured bundles.

**Do not substitute `npx skills check` for `agentic skills check`:** version 1.7.2
routes it to updates. Our check runs installation only in disposable staging and
compares the result. It reports content/layout differences, which may include local
customizations, rather than Git ancestry. Exit 0 means the comparison completed;
exit 1 means invalid input or a failed comparison. No background checks run.

| Bundle | Upstream | Selection |
| --- | --- | --- |
| matt | mattpocock/skills | Selected planning, implementation, TDD, review and PR skills |
| show-me | humanlayer/skills | show-me |
| verification | backnotprop/pstack | create-verification-skill, maintain-verification-skill |

The verification bundle is optional. Use it once runnable behavior exists and
exercise a real recipe before claiming it works. Run `/setup-matt-pocock-skills`
to confirm tracker/domain choices, preserving the project's existing conventions.

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
baselines and any not-yet-migrated legacy records. New skill records live in skills-lock.json. Use `agentic skills update` for explicit
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
`agentic skills check` compares installed content/layout with staged upstream output. Development conventions is the term for shared workflow, Git
preferences, standards and configuration; no profile abstraction is introduced.

### Archive leftover legacy folders

After adoption, preview a bounded cleanup from this checkout:

```bash
./agentic cleanup /absolute/path/project --adoption-notes --html
```

This proposes moving `.engineering/` and, with `--adoption-notes`,
`.scratch/agentic-setup-adoption/` into
`migrations/<project>/cleanup-backups/<token>/`, and removes only the five known
obsolete Engineering ignore rules. It preserves unrelated local edits. Review the
HTML before applying the exact token:

```bash
./agentic cleanup /absolute/path/project --adoption-notes --apply --expect TOKEN
```

Use the same options in both commands. `--archive PATH` overrides the archive parent;
it must be outside the target on the same filesystem. These are directory moves,
not recursive deletion or disk-space reclamation. Symlinks move intact without
being followed. Standalone Git repositories at the recognized legacy verification checkout path
are archived intact. Other nested Git metadata, linked worktrees, alternates, mount
boundaries and special files are refused.
Stop background writers before applying: the tree token fingerprints metadata
(including inode, size, mode, modification/change times and symlink text), not file
contents. Secret file contents are never scanned. Ordinary failures roll back
completed moves; interrupted processes may require recovery using the archive's
manifest. No automated restore command is provided. Keep the archive until recovery
is no longer needed; do not manually restore over subsequent project changes.
