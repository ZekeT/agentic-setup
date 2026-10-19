# Agentic Starter clean rebuild and minimal adoption handover

Updated 19 October 2026. This replaces the earlier incremental-refactor handover, including its OpenSpec migration requirements.

Rebuild `https://github.com/ZekeT/agentic-starter` in the same Git repository around Matt Pocock's development workflow. Add selected Pstack guidance and capabilities, HumanLayer show-me explanations, simple onboarding, and configurable Git conventions. Preserve the existing implementation with an annotated local tag before destructive changes.

The immediate priority is an ongoing large project already using an older Agentic Starter. Its development has become slow because of the starter's overhead. Deliver a minimal, reversible transition that removes that overhead without refactoring the application or waiting for the whole rebuild. Then continue improving the starter through explicit, selective upgrades that the application can adopt when ready.

## 1. Scope and authorization

Implement this handover locally in the starter repository on a dedicated rebuild branch. Creating the preservation tag and making scoped implementation commits are authorized. Preserve unrelated work. Remote pushes, release publication, PR creation, merges, and modifications to an external application require their own user instruction. Build and test the external migration capability using fixtures or an authorized disposable copy; do not guess which repository is the user's large project.

This handover explicitly replaces the old custom review, evidence, publication, and ownership-gate requirements. Update those policies and their dependent tests as part of the change. Retiring a documented old requirement is an intended product change; do not recreate it to satisfy an obsolete test. Preserve relevant application tests, security protections, team policies, and unrelated instructions. Resolve real conflicts explicitly rather than treating every old rule as a continuing requirement.

Build the smallest replacement for the agreed user journeys. Selectively reuse existing safe installer code when it is independently useful. Do not preserve the existing architecture simply because it is present, move old machinery into new folders, or compress a large platform into fewer files.

## 2. Agreed product decisions

| Area | Decision |
| --- | --- |
| Core workflow | Matt's setup, planning, implementation, TDD, review, and PR-description skills |
| New projects | Simple configuration-first initialization, with an optional explicit application seed |
| Existing projects | Inspect existing capabilities, reuse equivalent guidance, create missing configuration, propose larger repairs |
| Existing starter users | Minimal transition first; application work resumes without architectural remediation |
| OpenSpec | Remove starter migration tools, skills, fixtures, and operational instructions; no replacement migration feature |
| Quality | Project coding standards with selected Pstack principles and concrete test-integrity rules |
| Understanding | How/why investigation when needed, presented with show-me visuals and sufficient explanation |
| Verification | Native checks plus proportionate real-application verification; no evidence platform |
| Security | Separate user-invoked security review |
| Structure | User-invoked, advisory assessment; reuse Matt's architecture skill where it fits |
| Git | Shared conventions and allowed personal overrides, including personal integration branches |
| PRs | Show-me before Matt's pr skill; manual creation supported; agent creation only when authorized |
| Updates | Explicit versioned, scoped updates from the starter; no automatic tracking of main |

Do not install two skills with the same exposed name. In particular, Matt owns `/tdd`; Pstack's TDD guidance supplements standards and regression verification rather than replacing the called skill accidentally.

## 3. Preserve the old implementation before rebuilding

Inspect the current branch, HEAD, worktree, index, local tags, and repository instructions. Record the actual baseline commit; an earlier review used `0e6eea8200ce4ec520b0fe70662b3d39b882401a`, which is context only and must not replace the actual current baseline.

Create a descriptive annotated local tag such as `archive/pre-simplification-2026-10-19` at the complete pre-rebuild commit. Use the execution date if different. Never move or overwrite an existing tag. If an existing tag already identifies the correct baseline, reuse it; otherwise choose a distinct name. Verify the tag resolves to the intended commit before deleting tracked implementation files. Report the exact tag and commit.

A tag preserves committed content only. If the current worktree contains relevant uncommitted starter changes, establish a complete baseline without staging unrelated work or secrets. Use a scoped checkpoint where authorized and appropriate; otherwise preserve the dirty checkout and work from an isolated worktree, clearly reporting what the tag excludes. Do not claim a dirty working tree was backed up by tagging HEAD. Do not use destructive reset, clean, or blanket staging to obtain a clean baseline.

Create a dedicated rebuild branch from that baseline. Retain normal history; do not create an orphan branch or replace the repository. The tag is the archive: avoid copying the entire old system into an active `legacy/` tree. Local tagging does not make the archive available remotely; report that it remains local unless pushing it is separately authorized.

Before deleting a path, identify its purpose and consumers. Remove obsolete starter-owned files and dependency chains deliberately, including hooks, CI targets, scripts, instructions, tests, and generated templates that still invoke them. A failed useful test or a team safety rule is not an unnecessary blocker merely because it prevents progress.

## 4. Deliver the minimal transition first

Treat the ongoing application's transition as the first usable milestone. It must be independently usable before optional skill integrations or the complete greenfield experience are finished. Do not make it depend on a generalized migration framework.

Provide a small external command with preview and apply, for example:

```bash
./engineering adopt /path/to/project --minimal
./engineering adopt /path/to/project --minimal --apply
```

Command spelling may change for a materially simpler implementation. Preserve the two operations and document the real commands. Run the tool from the starter checkout; the target need not retain an installer runtime for daily development.

### Minimal transition procedure

1. Inspect existing instructions, installed skills, hooks, native commands, CI wiring, and known old starter metadata. Identify the installed version where possible and record the target's current Git baseline.
2. Preview a bounded change list: preserve, add, update, disconnect, delete, and unresolved conflict. Explain which recurring overhead each change removes.
3. Preserve application source, data, dependencies, tests, specs, glossary, ADRs, tracker format, open tickets, current task status, Git remotes, and team conventions. Retain usable installed Matt skills initially; upgrading their versions is a separate explicit decision.
4. Remove the active policy and command wiring that requires the retired verification ledger, review tiers, extra reviewer sessions, manifest repair, publication records, or starter self-tests for ordinary application work. Replace those requirements with the chosen native development flow and checks.
5. Remove obsolete files with established starter provenance when unmodified. For mixed/customized files, make a narrow reviewed merge that preserves project content, or report a conflict. Never delete `.engineering/`, `.claude/`, `.scratch/`, or all settings wholesale just because the starter once used them.
6. Fix callers and hook/settings entries before removing their implementation. A leftover active rule or dangling command can keep slowing the project even if most code was deleted. Trace instruction imports and nested project guidance within the affected configuration scope.
7. Add only missing essential references: current standards, native check commands, Matt tracker/domain configuration, explanation-before-pr behavior, and Git workflow settings. An optional architectural audit, model configuration, or verification-skill generator must not block this milestone.
8. Run relevant installation smoke checks and the project's agreed native verification. Compare with baseline failures when a baseline is available. Report an unavailable or pre-existing failing check honestly; do not demand that unrelated application debt be fixed before adoption can be used.
9. Show a short before/after workflow and the exact next development action. Provide a scoped rollback procedure for the transition changes.

### Preservation and recovery

If the target is supplied and applying to it is authorized, make the transition a dedicated infrastructure commit on an agreed migration branch where practical. Do not switch branches under active uncommitted work. A disposable worktree or clean copy can be used for validation without moving the user's workspace. Preserve staged/unstaged distinctions and unrelated files.

Deleting ignored old evidence/state requires explicit inspection because Git cannot recover untracked content. Keep unrelated local state. If a necessary file must be replaced outside Git, provide a bounded recoverable backup and state its location. Do not copy secrets into reports, snapshots, or backups indiscriminately.

Rollback should restore the transition's own changes, for example by reverting its dedicated commit, without resetting later application work. A baseline tag is useful context, not a reason to recommend `reset --hard` as routine recovery.

If a customized dormant file can safely remain disconnected, defer its removal and report it. If it still affects instructions, commands, or execution, resolve that conflict before claiming the overhead is removed. Do not leave hidden active requirements behind and call migration complete.

The minimal path does not rename application modules, reformat the whole repository, regenerate all docs, rebuild the tracker, convert OpenSpec content, migrate application dependencies, or introduce new test architecture. Larger improvements become separate proposals through the existing tracker only when requested.

## 5. Keep the application independent of continuing starter development

After the minimal transition, the application uses a known installed version and continues normal development while the starter changes. No per-session update check, remote source fetch, mandatory upgrade, or application-time digest validation is allowed.

Keep a small version/source record for installed starter additions and selected upstream skill pins. A compact file list or original template baseline is acceptable if necessary to safely update generated files; it must serve installation only and must not recreate the old runtime ownership model.

Provide an explicit external update path with preview and apply, pinned to a known starter release or commit. Allow scoped changes, such as just the explanation guidance or an optional review skill, without forcing adoption of unrelated features or new application dependencies. Group genuinely dependent changes as one coherent update and disclose the dependency.

Update only starter-provided sections and selected skills. Preserve project edits; where both sides changed, report a useful conflict instead of overwriting. Handle upstream skill version changes explicitly. Reapplying the same update must be a no-op. Removing a starter feature must remove its own known obsolete wiring without deleting user-owned extensions.

If a fully automated selective updater would delay the first milestone, ship a documented small, reviewable patch process first. Do not promise automated merging before it exists. Validate the essential sequence: minimally migrate an old installation, make an application edit, apply a later small starter update, and confirm that the application edit and customization survive.

## 6. Greenfield and ordinary brownfield setup

Expose one simple initializer and one preview/apply adoption entry point. Prefer the existing `./engineering` name if keeping it costs little. Setup should configure an existing agent workflow, not introduce a second task runner or workflow engine.

For greenfield, refuse an existing destination. Generate only shared instructions, standards, concise usage guidance, selected skills/configuration, and optional selected stack files. Configuration-only initialization is valid. Keep a Python seed only as an explicit option; do not impose Python application tools on other languages. Document installer prerequisites separately from application prerequisites. The generated payload excludes history, maintainer suites, legacy/OpenSpec migration code, and old verification/publication modules.

For brownfield, inspect capabilities rather than insist on exact filenames:

| Existing state | Adoption behavior |
| --- | --- |
| Equivalent instructions or standards exist | Reuse and reference them |
| Required guidance is missing | Create a concise file or section grounded in the repository |
| Existing documentation is incomplete | Propose or apply a bounded additive correction within adoption scope |
| Documentation and implementation disagree | Explain the discrepancy; do not assume code or prose is automatically intended behavior |
| Native commands are undocumented | Discover and test them where possible, then record them |
| Baseline tests fail | Record failures and propose repairs without hiding them |
| Code is difficult to test or maintain | Propose a bounded improvement with evidence and tradeoffs |
| Design history is unavailable | Mark rationale unknown; do not invent decisions |

Preserve package managers, existing CI, hooks, agent settings, team conventions, and tracker contents. A Makefile is optional. Never duplicate a useful existing standard merely to create CODING_STANDARDS.md. Avoid a full application audit by default; inspect setup and representative entry points, and deepen investigation only where needed. Large-scale remediation is optional work, not an adoption gate.

Preview is read-only for target project content and does not install dependencies. Before apply, recheck affected target content and refuse stale/conflicting writes. Do not silently overwrite local edits. Use simple transaction/recovery mechanics as needed; do not build a persistent approval or migration state machine. Repeat adoption must be idempotent.

Remove OpenSpec migration from the starter's active product. Existing OpenSpec artifacts in an adopted application are user content and remain untouched unless separately requested. Removing migration support does not authorize deleting another project's requirements.

## 7. Use Matt's setup and preserve skill ownership

Install selected upstream skills from inspected, recorded versions. Use Matt's `/setup-matt-pocock-skills` for tracker and domain-document setup, including triage configuration only when applicable. Preserve existing setup outputs and avoid repeating questions whose answers are already established. Local Markdown remains the suggested tracker for this user's new projects; respect the repository's existing choice.

Use its existing `docs/agents/issue-tracker.md` and domain guidance as the integration contract. Do not create a parallel tracker config, translate ticket formats unnecessarily, or change tracker status semantics. A feature PR into a personal branch must not automatically imply delivery to develop or closure of a team issue.

Keep Matt's upstream bodies unchanged wherever possible. Inspect the selected version's interaction between implementation, committed-diff review, and commits; make final-change coverage explicit without adding synthetic commits, a duplicate reviewer, or the old harness ordering. If an actual upstream integration inconsistency remains, report it and use a narrow documented compatibility decision rather than silently replacing native behavior.

Provide a short “what do you want to do?” guide for installed skills. Check runtime support and model dependencies before adding optional Pstack capabilities. Resolve exposed-name collisions at installation. Do not install all Pstack workflows or make its router a second owner of Matt's loop.

## 8. Git conventions and personal integration branches

Use a concise shared `docs/agents/git-workflow.md` or an existing equivalent. It records team integration branch, naming and commit conventions, allowed personal overrides, normal PR routing, and publication permissions. Defaults for a new project may suggest develop and Conventional Commits; inspect and respect existing conventions rather than creating branches blindly.

Use repository-local Git settings for personal choices where practical. For example, custom `agent.*` keys can record branch prefix, work base, PR base, push remote, and target remote/repository. Document that these are starter conventions; Git does not enforce them. Instructions must tell the agent how to read the effective values. A tiny deterministic resolver is appropriate only if it materially improves reliability.

Shared defaults apply first; personal overrides apply only to fields the project allows. Explicit task-specific instructions take precedence where authorized. Missing or invalid configuration must produce a clear question/error, not a silent fallback to main. Do not change machine-global Git settings or install hooks over existing hooks.

| Setting | Direct workflow example | Personal integration example |
| --- | --- | --- |
| Team integration | develop | develop |
| Feature starts from | origin/develop | origin/zek/integration |
| Feature name | feat/123-add-export | zek/feat/123-add-export |
| Feature PR target | develop | zek/integration |
| Promotion | Feature PR is the integration step | User raises zek/integration to develop |

Keep work base, review comparison base, immediate PR target, team integration branch, push remote, and target repository conceptually distinct. For normal feature work, review against the immediate intended PR target so unrelated personal-branch work does not inflate the feature diff. Support a fork without assuming push and PR-target repositories are identical.

Before implementation, inspect the current branch and resolve the intended branch safely. Never silently commit application work on a protected integration branch or move unrelated work. Before PR preparation, display source and target explicitly. Follow team naming; otherwise prefer meaningful branches and commits such as `feat(export): add CSV download`. Naming config is guidance unless a project chooses appropriate existing CI/hook enforcement; do not claim it guarantees compliance.

Default to PR-description preparation. If the user authorizes agent-created PRs to their personal branch, honor that scope and stop there. Do not promote to develop, auto-close team delivery issues, merge, or force-push as a side effect. Preserve the user's ability to create PRs manually.

## 9. Development quality and selected Pstack guidance

Matt owns planning, implementation, TDD, and Standards/Spec review. The repository's coding standards guide both implementation and review. Keep them concise, discoverable, and scoped to the languages in use.

Adopt these principles with concrete examples:

- Reduce reader effort: unnecessary indirection, hidden state, and scattered ownership matter more than raw line count.
- Inspect reuse and subtraction before adding a mechanism. Remove demonstrated dead or obsolete behavior within scope; do not widen every feature into a cleanup campaign.
- Model actual domain concepts where doing so removes invalid states or repeated rules. Keep simple local code when abstraction adds little.
- Validate at genuine trust boundaries and separate decisions from I/O where useful; retain checks at new boundaries rather than interpreting “trust types” as universal safety.
- Fix demonstrated causes. Do not hide defects with speculative retries, silent fallbacks, or branches unsupported by evidence.
- Prefer code that explains itself. Preserve comments explaining constraints, external quirks, contracts, or non-obvious reasons; remove narration. Keep legal notices, required tool directives, and useful API documentation. Do not automatically run Pstack's aggressive no-comments workflow.
- Turn recurring mechanical mistakes into appropriately small native checks; keep judgment calls as examples in standards and learning through Matt's retro.

Resolve timing explicitly: consider needed preparatory simplification during planning; perform authorized substantive refactoring as its own coherent work; keep Matt's red–green implementation cycles focused; examine new incidental complexity during review. Design heuristics such as DRY, file size, or number of helper layers do not become automatic blockers.

Test standards must require independently derived expected results, observable contracts, relevant failure behavior, and meaningful side-effect assertions. Avoid mocking away the behavior under test. Show a practical bug regression fails for the original defect and passes after the fix. Distinguish a real failing reproduction from environment/import failures.

Do not weaken assertions, remove tests, add skips, regenerate snapshots, or suppress checks merely to obtain green results. A genuine behavior change may justify an expectation change; explain it. Report exactly what ran and the remaining gaps. Use proportionate alternatives when a test would mostly exercise brittle mocks or unrelated infrastructure. Do not require mutation testing for every project.

## 10. Application verification without the old evidence platform

Tests, semantic review, and application verification answer different questions. Use existing test results without repeatedly rerunning them just to enter another stage. Run relevant native checks at appropriate completion boundaries and recheck affected behavior after corrections.

Use Pstack's project-specific verification concept when a runnable application exists. Inspect its existing scripts/tests before generating anything. A small `verify-<app>` skill or existing equivalent should explain launch/readiness, how to exercise the relevant user interface, observable results, necessary fixtures, and safe cleanup. Verify changed behavior at the matching surface: real CLI invocation, browser journey, API interaction, or library consumer example.

Execute at least one applicable recipe before claiming that the generated verification instructions work. Distinguish unavailable environments, stand-ins, missing credentials, and inconclusive outcomes. Do not weaken a journey to produce a pass. Use isolated test data and avoid live destructive effects. Clean up only processes and resources the run created.

In minimal migration, retain existing verification and record missing capabilities as follow-up; generation of this skill is not a prerequisite for resuming work. In greenfield, create it once there is meaningful runnable behavior rather than filling it with hypothetical commands. Maintain it when relevant app behavior changes, without creating a mandatory separate maintenance cycle.

Do not restore snapshot identity, evidence freshness/carry rules, required extra behavioral reviewers, remote source checks, acceptance ledgers, or publication state. Useful execution output can accompany a PR without becoming a framework.

## 11. Understanding and presentation before PR preparation

HumanLayer show-me provides the presentation. Pstack how/why methods provide deeper investigation when needed. Explain the actual code, ownership, and runtime flow; support historical rationale with commits, decisions, or other evidence, and label inference and unknowns.

Before every Matt pr invocation, provide a compact but sufficiently explanatory briefing: what changes for the user, one concrete example through the implementation, a useful diagram/sketch, why this design fits, key tradeoffs, and what verification demonstrated. Do not reduce the explanation to unexplained boxes and arrows or replace it with a long file-by-file transcript.

Use project policy and ordinary skill invocation to request this behavior, preserving upstream skills. Reuse gathered evidence and an unchanged recent explanation; refresh it after material corrections. Do not require a full multi-agent how/why investigation on every PR or a new approval record. The user may request deeper exploration at any point.

Matt owns the PR description. The configured Git workflow supplies its source/target context and any authorized creation action. No `/ship` platform is required.

## 12. Optional deeper reviews

Security review remains an explicitly user-invoked, scoped, read-only assessment. Cover relevant trust boundaries, authorization, sensitive data, injection, dependencies, and destructive effects. Report concrete evidence, plausible impact, and remediation. Ordinary review can still report obvious security defects. Do not invoke security review automatically through path-tier rules.

Structural assessment is explicitly user-invoked and advisory. Prefer Matt's `improve-codebase-architecture` for architectural investigation and visual improvement proposals. Add a small focused `/structural-review` only where Pstack's additional structural lens supplies a distinct useful capability; document the distinction and avoid two overlapping mandatory reviews.

Use Pstack's search for simplifications, clearer domain ownership, fewer unnecessary wrappers, and better boundaries. Give location, observed cost, smaller alternative, affected callers, and tradeoffs. Separate demonstrated defects from preferences. Do not emit a structural PASS/FAIL gate, block a PR, auto-refactor, or automatically file remediation work. The user chooses what to pursue.

More expensive capabilities such as competing design implementations or adversarial multi-model review can remain selectable extras. Their absence or unavailable model configuration must not block the default workflow or minimal migration.

## 13. Remove obsolete source and active blocker files

After preservation and dependency inspection, delete retired starter review/publication commands, evidence modules, carry-forward logic, install-role runtime gates, mandatory fingerprint repair, legacy OpenSpec tools, and tests/evals that exist solely to enforce those removed features. Remove stale policy paragraphs, hooks, CI requirements, generated references, and imports at the same time.

Keep native format/lint/type/test checks and useful secret protections. In a downstream application, preserve team-owned CI and branch protections; report required remote checks that a local config patch cannot change. Do not delete legitimate application checks to obtain apparent speed gains.

Retain only code needed for small onboarding, safe transition/update behavior, and selected useful capabilities. Maintainer tests belong in the starter source checkout. New applications must not inherit the source repository's history, migration tests, maintainer suites, or live local state. Historical implementation remains reachable through the preservation tag.

Keep one concise consumer guide and separate maintainer details. Remove contradictory duplicates across README, ENGINEERING, REVIEW, CLAUDE/AGENTS, nested instructions, and command files. Do not mandate feature documentation in every source folder. Optional Graft/navigation should stay independent and must not complicate the default or minimal path.

## 14. Delivery order and acceptance

1. Inspect and establish a complete baseline; create and verify the preservation tag and rebuild branch.
2. Specify the small target instructions/configuration and retire the superseded policy in the rebuild branch.
3. Deliver the minimal old-starter transition and focused preservation tests. Make it usable as its own milestone.
4. Complete the small greenfield/adoption interface and Matt setup integration.
5. Add Git configuration, explanation guidance, and selected verification/optional capabilities.
6. Remove remaining dead source and operational references; verify the consumer payload.
7. Prove a later selective update preserves an application's work and customizations.

Do not delay milestone 3 for optional features or a generalized updater. Reorder tightly coupled implementation work as needed, but maintain the early useful transition deliverable.

| Scenario | Acceptance evidence |
| --- | --- |
| Preservation | Annotated tag resolves to the real pre-rebuild baseline; dirty/untracked exclusions are explicit |
| Minimal old-starter transition | Ordinary implementation/check/review no longer invokes retired starter gates; source, tests, tasks, and custom rules remain intact |
| Modified legacy configuration | Custom content is merged safely or flagged; no blanket deletion |
| Repeated apply or stale preview | No duplicate changes; stale writes rejected without silent overwrite |
| Failure or rollback | No half-installed active configuration; recovery targets transition changes, not subsequent application work |
| Native checks | Relevant checks run; pre-existing failures are distinguished where established; no fabricated success |
| Ongoing development | A small representative application change can be developed without the old evidence/publication process |
| Selective future update | A later starter change preserves intervening application work and project customizations |
| Generic and existing non-Python projects | No mandatory Python application toolchain or competing task runner |
| Matt setup | Existing tracker and domain guidance reused; no duplicate skills with the same name |
| Git routing | Direct and personal-integration examples resolve correct work/review/PR bases and remotes; unknown refs fail clearly |
| Explanation | Final implementation is explained with a useful visual and example before pr |
| Application verification | A real relevant recipe is exercised where available; unavailable execution is disclosed |
| Optional reviews | Explicit invocation; structural findings advisory; no automatic remediation |
| Removal | No OpenSpec migration feature or dangling retired runtime dependencies in the delivered product |

Prioritize meaningful tests for file preservation, mixed ownership, repeatability, conflicts, partial failures, and update/remove boundaries. Avoid large suites asserting exact prompt wording or an elaborate new benchmark system. A practical workflow walkthrough is useful; label simulated instruction checks separately from actual agent execution. Compare observable workflow overhead before/after where feasible, but do not promise a numerical speed improvement without measuring it.

If the user's actual application is unavailable, deliver and test the transition using representative legacy fixtures and clearly state that live-project validation remains. Do not claim migration of the real project occurred.

## 15. Final implementation report

Report the preservation tag and commit, rebuild branch, minimal migration command, new setup/development flow, removed overhead, retained checks, future update procedure, and verification results. Identify unresolved customized files, remote CI requirements, or unavailable live-project validation. Include scoped recovery instructions. Keep the report concise and leave optional application refactors as separate proposals.

## Upstream references

Inspect the pinned versions actually selected; maps are discovery aids rather than the executable specification. Record upstream revision choices and honor attribution/licensing when adapting text.

- Matt skills: https://github.com/mattpocock/skills
- Matt map: https://erictechpro.github.io/super-board/mattpocock/
- Matt setup: https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md
- Matt TDD: https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md
- Matt architecture assessment: https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md
- Pstack: https://github.com/backnotprop/pstack
- Pstack map: https://erictechpro.github.io/super-board/pstack/
- Pstack app verification: https://github.com/backnotprop/pstack/blob/main/skills/create-verification-skill/SKILL.md
- Pstack how and why: https://github.com/backnotprop/pstack/tree/main/skills
- HumanLayer show-me: https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md
- HumanLayer explanation: https://www.humanlayer.dev/blog/show-me-skill
