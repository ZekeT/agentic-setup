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

## Move an existing starter project first

From this external Agentic Setup checkout, against a committed Git project:

```bash
./agentic adopt /path/to/project --minimal
./agentic adopt /path/to/project --minimal --apply --expect TOKEN
```

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

## Install selected skills once

Fetch the chosen upstream into a separate directory, then check out its recorded
commit. The installer copies selected skill directories unchanged, retains licenses,
and refuses duplicate upstream names. Existing exposed skills are preserved;
upgrading them is a separate explicit decision. It does not install a second TDD.

```bash
git clone https://github.com/mattpocock/skills.git /tmp/matt-skills
git -C /tmp/matt-skills checkout 4588b32ecab9ecc9fc8cc6b6c5e7d675b6004b0d
./agentic skills install /path/to/project --from /tmp/matt-skills --bundle matt
./agentic skills install /path/to/project --from /tmp/matt-skills --bundle matt --apply --expect TOKEN
```

Initialize Git and commit first for new projects. Skills go into `.claude/skills`;
Claude discovers them, and other runtimes may read the same SKILL.md directly.
Check your runtime supports each selected skill's subagent needs. Do not install
another copy with the same exposed name. Run `/setup-matt-pocock-skills` to confirm
missing tracker/domain configuration, reusing existing answers. Local Markdown is
the suggested tracker for new projects; existing trackers keep their semantics.
Triage configuration is only needed when its skill is installed.

Optional bundles use the same preview/apply command:

| Bundle | Upstream | Required checkout |
| --- | --- | --- |
| show-me | humanlayer/skills | 3c2629142c5d437428269b1b722b08c0b87f574d |
| verification | backnotprop/pstack | 6f131f137de64fdaf928278c0fd9ecec520ccbee |

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
| Improve architecture | Matt's codebase-design at this pin; advisory, user-invoked |
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
baselines and skill pins only. Skill upgrades and feature removals use reviewed
scoped patches: compare the pinned versions, update/remove their own references,
preserve custom extensions, run native checks, and commit separately. There is no
automatic upstream skill merge or generalized feature-removal engine.

[Maintainer details](CONTRIBUTING.md) describe tests and the preserved baseline.

## Naming and release compatibility

Agentic Setup replaces the Agentic Starter name. This branch uses `agentic`, the
`agentic_setup/` implementation package and `.agentic-setup/` installation metadata.
The published v3.0.0 tag retains its original `engineering` command and names.
Existing `.starter/` installation records and licenses continue to be used in
place; do not rename or duplicate them to upgrade. Conflicting metadata records
in both locations require manual reconciliation. New workspaces use the new name.

The skill installation command is `agentic skills install`. Unified `agentic inspect`,
`agentic skills check` and `agentic skills update` are planned capabilities, not
available commands. Development conventions is the term for shared workflow, Git
preferences, standards and configuration; no profile abstraction is introduced.
