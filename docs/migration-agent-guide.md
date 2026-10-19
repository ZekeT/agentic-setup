# Agent guide: migrate an existing project

Use this from the Agentic Setup checkout for the three existing projects being
migrated. Work on one target at a time. This is a bounded migration procedure, not
a new platform or a recurring development requirement. The human supplies the
workspace path; do not discover and migrate other projects automatically.

## Boundary

Prepare files only here, under `migrations/<workspace-name>/`. The live target is
read-only until the human explicitly approves a concrete preview. Only Agentic
Setup commands may modify it. Do not directly edit/delete target files, switch its
branches, stage/commit/stash/reset/clean its Git state, install dependencies, or run
application commands as a workaround. Do not execute upstream skills during preview.
Never read .env or secret variants. Preserve security hooks and unrelated work.

Read relevant target instructions as project context. The requested migration retires
the old starter's mandatory verification/publication machinery; do not recreate its
review tiers or ledgers to satisfy the very rules being removed. Security review is
user-invoked only. Removing a customized reviewer needs an explicit project decision;
never assume the decision from another target applies to this one.

## 1. Inspect and produce the first preview

```bash
./agentic inspect /absolute/path/project-name
./agentic adopt /absolute/path/project-name --minimal --html
```

Record the actual target path, Git baseline and current branch in a short local
`migrations/<workspace-name>/README.md`. Read-only Git queries may be used with
`git --no-optional-locks -C /absolute/path/project-name ...`. Do not assume the
workspace is still on the branch or commit seen in an earlier conversation.
Note existing local work; do not resolve it by switching branches or committing it.
If tracked local edits block application, explain the specific paths to the human.

Review the HTML, including proposals without conflicts. Check that application
checks/Make targets, domain and tracker conventions, Git host/remotes, useful hooks,
installed skills and project-specific rules are preserved. Inspect surviving custom
instruction sections for references to retired machinery. Zero reported conflicts
means the planner found none; it does not certify every project-specific decision.

## 2. Prepare project decisions here

Use [the resolution format](../migrations/README.md). Create resolutions.json only
when needed, with the canonical target path, exact current file hashes and a reason
for each operation. Put full replacement files under replacements/. Select the
narrowest sufficient action: delete, replace_text, json_remove or replace_file.
Do not put shell commands, ignore-conflict flags or unsupported fields in the plan.

Hashes describe current target bytes; edits operate on the default proposed contents
when present. Use null for an absent file. Do not propose deleting an already absent
file. Inspect the original before supplying a full replacement; preserve relevant
project rules rather than substituting generic boilerplate. Keep existing upstream
skills initially; their installation or upgrade is a separate explicit decision.

Use known user decisions. Ask about materially ambiguous project policy, unknown
custom files or intended removals; do not invent consent. If the schema cannot express
a needed resolution safely, improve and test the tool here or report the limitation.
Never bypass its guards or patch the target directly.

```bash
./agentic adopt /absolute/path/project-name --minimal --resolutions migrations/project-name/resolutions.json --html
```

Repeat after editing the local plan or replacements. Each report is numbered; keep
older reports for comparison. If target contents changed, inspect the new contents
before revising the hashes—never blindly refresh them to force a plan through.
For targets with the same basename, use distinct external plan folders/report paths.

## 3. Present, then wait for approval

Provide the latest HTML link, a short explanation of the important changes and
remaining conflicts, the observed baseline/branch, and what has actually been tested.
State that the target has not been changed. Do not claim that source-tool tests
validate the real application's behavior. The human approves that concrete preview;
a request to prepare a migration or save resolutions is not apply approval.

After approval, apply the same inputs and token, without --html:

```bash
./agentic adopt /absolute/path/project-name --minimal --resolutions migrations/project-name/resolutions.json --apply --expect PREVIEW_TOKEN
```

Omit --resolutions if there was no resolution file. If inputs or the proposal change,
generate a fresh preview and obtain approval for the revised scope. Native application
checks require explicit authorization too; if agreed, inspect the command first and
use the CLI's --check option on apply. These commands execute project code and may
write caches. Without them, report application verification as not run.

Resolution applies save external recovery copies before target writes. Report the
actual recovery location and outcome. A failure is not permission to reset, clean,
manually restore files or overwrite an existing backup. Inspect read-only, report the
state, and propose recovery through the tool; no automated restore command currently
exists. Do not erase evidence of a partial attempt.

After successful apply, inspect the scoped diff read-only, report checks and gaps,
and hand back to the human. Target commits, publication and merge are not part of
this agent procedure. Keep the local artifacts; do not commit project-specific
reports or decisions into Agentic Setup. Once the three migrations are complete,
retain this guide as reference without adding an ongoing migration workflow.

## Optional post-adoption cleanup

For leftover legacy state, use `./agentic cleanup TARGET --adoption-notes --html`.
The notes flag selects only `.scratch/agentic-setup-adoption`; omit it to keep that
folder. Review the archive destination, inventory and ignore-rule diff. Stop target
writers before approved apply with the same options and `--apply --expect TOKEN`.
This command archives entire directories on the same filesystem without following
symlinks or scanning application/secret file contents. Git metadata is inspected
read-only to identify standalone snapshots. It does not reclaim disk space. Only standalone repositories at the recognized legacy verification checkout path
are included; other nested Git metadata and special files require separate review. Never replace refusal with
manual deletion. Existing uncommitted adoption edits remain untouched except the
explicitly previewed legacy paths and ignore rules. Recovery artifacts stay here.
