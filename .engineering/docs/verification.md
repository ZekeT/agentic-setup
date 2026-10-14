# Reusable independent verification

Build, Verify, Accept and Publish are separate responsibilities. A local commit
is not proof or human acceptance. After implementation, hand off automatically to
fresh independent reviewers when supported. Review obtains missing evidence and
consumes current evidence. [Publication](publication.md) reuses current proof
without repeating semantic review or authoritative checks.

## Prepare the intended change

Discover the complete proposed PR scope against the comparison base, including
intended staged, unstaged and new files. Include requirement documents in tracked
context or explicit inputs when their bytes matter. Do not reduce scope just to
pass. Inspect check commands and version probes before running them: these are
explicit project-owned executables, not data downloaded by the evidence tool.

Keep plans, reports and records under ignored local
`.engineering/state/verification/`. Example `plan.json`:

```json
{
  "base": "main",
  "requirement": "The agreed request, or a ticket/spec pointer",
  "paths": ["src/example.py", "tests/test_example.py"],
  "checks": [["make", "check"]],
  "tools": [["python3", "--version"], ["uv", "--version"]],
  "inputs": [],
  "tier": "ordinary",
  "tier_reason": "Why this review tier fits the change"
}
```

Use exact paths including deletions, not directory/glob selectors. Commands are
argument arrays, without implicit shell interpolation. List actual relevant
runtimes/check tools in `tools`; status runs those read-only version probes, not
the suite. `inputs` names additional ignored non-secret files influencing results.
All tracked configuration/locks and ignored managed dependency evidence are
included automatically. A URL alone is not a requirement-content fingerprint.
Reviewers independently assess plan completeness and the declared review tier.

Planning reads the installation role, `maintainer` or `consumer`, from the
proposed `.engineering/state/install.json` in the verified content: the
committed state, or working bytes only when that path is in the plan's paths.
The stricter of the base and proposed roles applies (`maintainer` is stricter),
so a role change takes effect only after it merges.
An out-of-scope working edit never supplies or changes the role; `status`,
`check` and `record` re-validate it. Generation and adoption record
`consumer`; the maintainer checkout records `maintainer`. No role is ever
assumed: when it is missing, `prepare` fails INCOMPLETE and names the fix. From
a starter checkout, preview `engineering update <project>` and apply it; the
update records the role as an Engineering migration. An unknown role also fails.

Required checks follow the role and each path's ownership in the proposed
`.engineering/manifest.json` (the base manifest too, so dropping an entry
cannot lower them), never which Make targets exist:

| Changed path | Role | Required in addition to `make check` |
|---|---|---|
| Project configuration (`preserve` entries) | both | `make engineering-check` |
| Integration sections and hooks (`section`, `hooks`) | both | `make engineering-check` |
| `.engineering/manifest.json`, `.engineering/state/install.json` | consumer | `make engineering-check` |
| `.engineering/manifest.json`, `.engineering/state/install.json` | maintainer | `make engineering-check`, `make engineering-test`, `make engineering-evals` |
| Managed implementation (`file` entries) | maintainer | `make engineering-test`, `make engineering-evals` |
| Starter tooling under `.engineering/` `template/`, `tests/`, `evals/`, `scripts/`, `migrations/` | maintainer | `make engineering-test`, `make engineering-evals` |
| Managed implementation edited or deleted without a pinned source | consumer | Rejected: INCOMPLETE, never PASS |
| Managed implementation matching a pinned starter update source | consumer | `make engineering-check`; sensitive review |
| Any other path | both | nothing further |

A plan whose every path is prose-only project documentation (see
[Prose-only documentation](#prose-only-documentation)) requires
`./engineering docs-check --` with its sorted paths instead of `make check`.

When a plan records both `make check` and `make engineering-check`, `verify
check` tells the starter's check script that doctor and maintainability are
recorded separately, so `make check` does not repeat them. PASS still requires
the separate health result. Consumer-owned `make check` recipes run unchanged,
and standalone `make check` keeps both checks.

Consumer changes to `file`-owned managed bytes require the pinned-source route
below. Proposed manifest digests cannot vouch for those bytes. Without that
source, restore the file and obtain changes with `engineering update <project>`
from a starter checkout, or propose them upstream. In the maintainer checkout
installation metadata is maintainer source as well: the manifest is the
ownership contract every consumer receives.
Invalid project configuration fails preparation, naming the file. The recorded role is
trusted and fails closed: a consumer declaring `maintainer` must run suites it
lacks; a maintainer checkout proposing `consumer` keeps maintainer requirements
until that change merges. A role change is visible in the diff. Configured application roots require
`.engineering/bin/graft check` while `[navigation] provider = "graft"` (never
with `none`). Add project-specific checks as needed.
Formatting and graph building remain implementer preparation. Probes time out
after 15 seconds, each check after 30 minutes. uv stays offline with interpreter
downloads disabled.

```bash
./engineering verify prepare --change example --plan .engineering/state/verification/plan.json
./engineering verify status --change example
```

Prepare returns a snapshot and existing current proof or an INCOMPLETE handoff.
It does not run checks/reviewers. Status exits zero only for current complete
PASS; missing, stale, malformed or failed evidence is nonzero. Prepare and record
exit zero when bookkeeping succeeds even if proof is incomplete; inspect their
JSON status. No result grants acceptance or publication authorization.

Snapshots include tracked context, explicit inputs, working bytes/executable bits,
merge-base, plan and tool-version outputs. The base tip is advisory recorded data,
excluded from identity: fetching an advanced base without rebasing retains proof.
Content-preserving commits retain proof; changed identity inputs do not. Base movement is assessed locally without
fetching. Elapsed time alone does not invalidate proof. Plans with a starter
source additionally require a successful source fetch on each evidence operation.

Verification always prepares an isolated temporary checkout under ignored local
state. The JSON `checkout` path identifies captured source for behavioral and
security inspection. Native /code-review runs in the original repository at the
actual scoped checkpoint commit against its pinned fixed point. The capture keeps
HEAD at the comparison base; do not run native committed-diff discovery or create
review commits there. `verify check` runs commands in a separate disposable copy,
reported as `check_checkout`. The capture contains comparison-base context plus
intended working bytes and executable modes (committed, staged, unstaged and new
files, including deletions). A path's working bytes are the proposed final version;
index-only intermediate versions are not a second version of the PR. Unrelated
local edits and new files are excluded without stash, commit or workspace writes.
Committed changes outside `paths` fail preparation: they cannot be omitted from
the proposed PR. Include each side of a rename.

Version probes also run in isolation. Explicit `inputs` and installed dependency
evidence are copied and fingerprinted; tracked explicit inputs must be in `paths`.
Ignored environments, installed tool directories and caches are not silently
copied or linked from the working tree. Checks needing additional regular files
must declare them as inputs. Missing tools/dependencies or preparation failures
leave proof INCOMPLETE, never PASS. Install/prepare dependencies explicitly before
verification as needed; no command installs them on your behalf. This is content
isolation, not a security sandbox: approved project executables can access the
machine and absolute paths. Inspect commands and probes accordingly.

For the generated Python application, the implementer prepares the reported
checkout with `uv sync --offline --all-extras` before handing it to reviewers.
This installs locked development tools from the existing cache; `uv run` alone
does not select optional development dependencies in a new environment. If the
cache is missing packages, explicit dependency installation is needed before
the offline gate can pass. Declare the installed Matt skill outputs and required
Graft files as inputs for doctor/navigation. Maintainer Graft integration tests
need the full installed runtime, not just its package metadata. Do not copy a
populated working-tree Python environment or treat a missing executable as
successful verification.

The isolated checkout remains available for independent inspection and check
artifacts. Source mutations there invalidate proof; prepare again to build a
fresh checkout and clear reports. Old ignored checkouts can be removed when no
review is using them. Missing local checkouts require preparing fresh evidence.
Carried reports depend on every earlier evidence folder in their history, and
native reports depend on their reviewed commit. If either is removed or pruned,
status reports INCOMPLETE; prepare again keeps the old record as history,
explains why in `history_note`, and requires fresh checks and reports.
Symlinks, submodules/nonregular inputs, unmerged entries and secret paths fail
closed; the public `.env.template` is permitted. Secret/environment values are
not fingerprinted. Disclose material external/environment gaps; this is not a
hermetic snapshot of the machine or external services.

## Verify a consumer starter update

Apply the update from a starter checkout at the agreed revision, then include
all resulting changes (including new files, metadata and removals) in `paths`.
Add this optional field to the verification plan:

```json
"starter_source": {
  "repository": "https://github.com/ZekeT/agentic-starter.git",
  "commit": "<full-40-character-lowercase-commit-sha>",
  "tag": "refs/tags/<release-tag>"
}
```

Replace the placeholders. `commit` is mandatory; `tag` is optional and, when
present, must still resolve to that commit. Branch names, abbreviated hashes,
local checkout paths and `file://` URLs cannot serve as source authority.
Supported repository URL transports are HTTPS, HTTP, SSH and Git. Choose the
agreed starter repository and release: a pin proves byte identity, not publisher
identity or a signed release. Independent reviewers must assess that choice.

Use `tier: "sensitive"` and include `make check` and `make engineering-check`.
Source-backed updates always require separate behavioral, native Standards/Spec and
security reviewers. Consumer projects do not acquire maintainer test/eval
requirements. Application changes may accompany an update and remain subject to
normal scope, checks and review rules.

Every `prepare`, `status`, `check` and `record` operation fetches the named Git
objects into temporary storage. No source checkout filters, hooks or downloaded
scripts are executed to validate the source. Fetching and all Git object reads
use the same isolated environment: inherited `GIT_*` overrides and global/system
Git configuration are ignored, and replacement objects are disabled.
Git transport uses no interactive credentials; SSH can use an existing agent and
known host configuration. Each transport operation has a 60-second timeout.
An unreachable source, a tag resolving to another commit, or an inconsistent
source manifest leaves verification INCOMPLETE. There is no cached/offline
fallback. Normal plans without `starter_source` remain offline.

The source manifest is checked against the source distribution using the same
file mappings as generation and update. Proposed manifest metadata must match
that source (apart from the consumer's `project` settings). All proposed
`file`-owned bytes and executable modes must match the fetched distribution;
files owned as `file` in the base and absent from the source must be removed.
A forged digest, dropped manifest entry, omitted changed path or missing new
managed file cannot authorize an update. Installation baselines must agree too.
Integration sections and project-owned configuration retain their normal review
rules; source proof does not attest arbitrary application or integration edits.

The evidence snapshot includes the repository, commit, fetched revision object
(including an annotated tag object), source manifest and its SHA-256 fingerprint.
The command result exposes the source identity for reviewers. A changed source
invalidates reusable proof and prevents report carry-forward. A changed tag
object pointing to the same commit changes snapshot identity too. Source
working-tree edits cannot affect proof: only the fetched commit is authority.

## Review tiers

Each plan declares a review tier with a reason. The tier decides the required
reviewer roles; it never adds or removes checks.

| Tier | Required reports | Sessions |
|---|---|---|
| `documentation` | behavioral | one fresh session |
| `ordinary` | standards, spec, behavioral | separate fresh sessions |
| `sensitive` | standards, spec, behavioral, security | a separate fresh session per role |

Preparation computes a tier floor from the changed paths and rejects a plan that
declares less, naming each path and the rule that set the floor. A mixed change
takes the highest path floor. Declare a higher tier with a reason when risk the
paths cannot show applies, such as authentication, secrets or untrusted input.
Starter-owned rules always apply:

- `sensitive`: dependency manifests and locks (`pyproject.toml`, `uv.lock`,
  `package*.json`, `.engineering/dependencies.toml`), `.claude/settings*.json`,
  hooks, `.pre-commit-config.yaml`, `.envrc`, `.claude/statusline.sh`, `.github/workflows/**`, make recipes
  (`Makefile`, `GNUmakefile`, `makefile`, `*.mk`), `.engineering/scripts/**`
  and Engineering launchers. In the maintainer checkout also the dependency
  (including Graft), skill-installation, apply, transaction, update, migration,
  publication and verification modules (including the `docs-check` module).
- `ordinary`: agent policy is never documentation: `CLAUDE.md`, `AGENTS.md`,
  `.claude/**` including skills, `REVIEW.md`, `ENGINEERING.md`, Engineering docs
  and agent docs. Changes to `.engineering/config.toml`, which holds the review
  settings, are at least `ordinary`.
- `documentation`: a path the project's review settings list as documentation
  that no rule above catches, when it is a prose-only file (present,
  non-executable Markdown; see Prose-only documentation). Every other path is
  `ordinary`.

Review settings live in project configuration:

```toml
[review]
documentation = ["README.md", "docs/**/*.md"]
sensitive = []
```

`documentation` names paths eligible for the documentation tier, such as domain
context and ADRs; `sensitive` adds project paths that always need security
review. A pattern without `/` matches a file name at any depth; other patterns
match the repository path, where `*` also crosses directories and `**/` includes zero directories; a leading `/`
anchors a file name to the root. Project settings add to the starter rules and
can never reduce them. The floor evaluates both the base and the proposed
settings and keeps the stricter result for each path, so a change cannot lower
its own review. Invalid settings fail planning.

### Prose-only documentation

Prose is decided by file type, not content: a path the review settings list as
documentation is prose-only when it is a present, non-executable Markdown file
(`.md`, `.markdown`). Anything else in a configured location floors at
`ordinary` with a recorded reason: `unsupported documentation format`,
`deleted document` or `executable file`. Content is not inspected, so changed
examples, inline code, HTML and task items in configured documentation are all
prose; the documentation reviewer reads every changed line. Keep requirements
and acceptance criteria out of configured documentation locations when they
need full review. Agent policy, review settings and sensitive paths never
qualify.

When every planned path is prose-only project documentation, the plan needs
`./engineering docs-check -- <paths>` (paths sorted; `--` keeps a path such as
`-h.md` from being read as an option) instead of `make check`; a
configured Graft check still applies. A mixed, managed or pinned-source plan
keeps the full applicable suite. `docs-check` reads each file as UTF-8 and
reports local link targets and heading anchors (ATX, setext and blockquoted
headings, GitHub-style slugs) that do not resolve; external URLs are not fetched
and `?query` suffixes are ignored. Lines over 1000 characters are skipped. It
checks only the planned files: a heading
rename can break anchors in other documents, which the documentation reviewer
must look for. It runs without the application environment, so add project
checks to the plan when prose needs more. One fresh documentation
review, recorded as the behavioral role, checks the changed claims against the
code, tests and recorded decisions (domain context and ADRs) and reports
contradictions. Configuration edits that would widen documentation are
`ordinary` themselves and the floor uses the stricter of base and proposed
settings, so they cannot lower their own route.

Native Standards and Spec are distinct semantic reports from the unchanged
upstream /code-review skill. Each role uses a separate fresh session. Shared
reviewer identifiers are rejected for ordinary and sensitive changes. Scheduling
must follow the native workflow and runtime restrictions; the harness never
invokes, wraps, copies or selects native axes.

Evidence schema 3 replaces ticket-level maintainability proof. Schema 1 and 2
records are preserved through `previous_evidence` when preparing fresh evidence;
old reports and checks cannot satisfy the new contract. Run `verify prepare`
with the current plan, checkpoint intended content, and obtain fresh recorded
checks and required independent reports. Unsupported versions fail with recovery
guidance: use compatible tooling or archive the unsupported record before preparing
again. Never relabel maintainability as Standards or Spec. Publication history
and authorization files are retained, but incompatible verification cannot publish.
A changed publication plan still needs renewed presentation and authorization.
Configuration and consumer check recipes do not change in this transition.

## Obtain fresh evidence

Fresh reviewers for the roles the tier requires receive only the
branch/request/spec/ticket and captured-content pointers plus factual check evidence. They independently discover requirements,
actual scope and prepared plan; no implementer reasoning/self-review is handed
over. The plan is a discoverable scope/execution contract, not proof.

Format intended content and make ordinary scoped checkpoint commits before native
committed-diff review. Include additions, deletions and executable modes. Do not
create synthetic review commits. Capture the snapshot and `checkout` path before
inspecting or running anything.
Behavioral and security reviewers inspect source and diffs inside that checkout,
including its uncommitted/new files relative to the comparison base. Native
Standards and Spec use the unchanged skill in the original checkpointed repository,
with its committed diff against the pinned fixed point. Invoke evidence commands
from the original repository, where the plan and records live. The implementer
executes the initial full applicable suite once through:

```bash
./engineering verify check --change example --snapshot <prepared-token>
```

This records argv, stdout, stderr and exit codes, clearing old check and behavioral
proof first so interruption cannot leave an old PASS. Source mutations prevent
current proof. Avoid secrets in commands/reports and inspect output before sharing.

Each reviewer supplies a report in ignored local storage:

```json
{
  "snapshot": "identity captured before review",
  "role": "behavioral",
  "reviewer": "fresh reviewer session identifier",
  "independent": true,
  "verdict": "PASS",
  "summary": "Observed behavior and relevant coverage",
  "findings": [],
  "coverage_gaps": ["Explicitly state what remains unverified"]
}
```

Roles are `standards`, `spec`, `behavioral`, `security`; verdicts are `PASS`, `FAIL`
or `CONCERNS`. Findings are readable strings with evidence/references. Behavioral
PASS requires successful recorded authoritative checks. Non-PASS reports prevent
PASS; missing roles the tier requires remain INCOMPLETE.

```bash
./engineering verify record --change example --report .engineering/state/verification/report.json
./engineering verify status --change example
```

For native `standards` and `spec` reports also supply `reviewed_commit` and
`comparison_base` as full commit IDs captured from the actual native invocation.
The snapshot binds plan, tools, dependencies, explicit inputs and content; these
fields bind the committed review and its three-dot comparison. The reviewed
commit must contain all prepared changes and its comparison must resolve to the
prepared merge base. Subsequent uncovered edits invalidate publication. A
content-preserving commit can retain proof; a commit alone proves no review.

Fresh behavioral inspection consumes the recorded suite and inspects changed
behavior, failure paths, configuration interactions and nearby regressions.
Do not repeat valid checks just to inspect behavior. Security remains a separate
targeted responsibility for sensitive changes, including evidence enforcement.

Captured content is immutable review input. `verify check` executes in a separate
copy exposed as `check_checkout`; source mutations there reject check evidence
without modifying `checkout`. For other mutating probes use disposable copies and
report source snapshot, commands, results and limitations. Ignored build artifacts
are not proof of unchanged source. Never modify another reviewer's capture.

Serialize evidence writes: run checks before recording the behavioral report and
record reports one at a time. A per-change lock refuses concurrent verification
and publication operations; retry after the active operation finishes. Never edit stored records manually. If inputs change,
prepare again and obtain fresh proof; never relabel old findings with a new token.
Outside the clean-rebase exception below, changed inputs clear active reports and checks. Preparation saves the previous
record in the new checkout's sibling `previous.json`, exposed as
`previous_evidence`. It remains historical evidence; only the automatic carry-forward below can
rebind its reports to current proof.

## Carried evidence after a clean rebase

`verify prepare` automatically carries reports when the merge-base advances and
each scoped path's own patch is identical, the plan, tools and required checks
are unchanged, and no upstream path changed between merge-bases intersects the
plan's paths or explicit inputs. Installed dependency evidence must also match.
The previous checkout must remain intact. Base-tip movement alone preserves
current proof; the latest prepare records the current advisory tip.

Each carried report records `carried_from` naming its prior snapshot. Previous
records remain available through `previous_evidence`. Only prepare may rebind
reports; submitting a report with `carried_from` or manually relabelling old
reports is forbidden.

A carried snapshot starts with no checks and is INCOMPLETE until `verify check`
passes. For carried snapshots only, this deterministic rerun preserves carried reports
and grants no self-review permission. The initial suite may also be run by the
implementer; neither execution replaces independent inspection. A failing check yields FAIL and drops the behavioral report; a fresh
independent behavioral reviewer must investigate and attest after correction.
Without carried reports, checks still clear behavioral proof before running.
Interrupted runs cannot satisfy the full required check list.

Any changed patch, plan, tools, checks or overlapping upstream path carries
nothing. Follow the review-corrections procedure using the previous evidence.
Publication accepts current carried PASS evidence without another review round,
but still requires the remote base tip to equal the latest prepared tip. Human
acceptance of the current presented scope remains required.

## Interpret proof honestly

The tool validates freshness and reviewer attestations, but does not authenticate
a model/session, launch a runtime-specific agent, or prove that an asserted
independent review occurred. Actual independent sessions and runtime instructions
provide that boundary. Never fabricate reports from implementer self-review.
If fresh reviewers are unavailable, leave INCOMPLETE evidence and hand off the
branch/request pointer, plan and missing roles to a fresh session. Shipping waits.

Before reuse, compare the plan with the actual request, scope and applicable
checks. PASS for the wrong requirement or omitted relevant input is insufficient.
Human acceptance remains separate. Put a concise scope/evidence/gaps summary in
the eventual PR, not local bookkeeping. Another checkout without records
regenerates verification. This is not a ticket tracker or workflow database.

## Review corrections

After human-directed fixes, prepare the same change with its current complete
scope. The previous evidence reference preserves the old snapshot, reports,
checks and checkout pointer for comparison, including findings still unresolved.
Never edit history or relabel an old report with the current token. Missing or
untrustworthy history requires fresh review of the relevant areas.

Fresh independent reviewers compare the prior and current proposed content and
inspect the fix and affected behavior. In each new report's `summary`, identify
resolved and remaining finding evidence, the correction inspected, and any retained
unchanged-area evidence by previous record path, snapshot and role. Explain why
that coverage remains applicable, including relevant dependencies and call sites;
unchanged file bytes alone do not prove unaffected behavior. Use `coverage_gaps`
for limits. Each required role supplies a current independent attestation; a
reviewer can incorporate justified prior coverage without repeating that inspection.
Changed requirements, scope, architecture, check configuration or tools require
broader inspection as appropriate. Historical failures cannot be ignored: explain
resolution or retain the finding and a non-PASS verdict.

The implementer runs `verify check` for the current snapshot after code fixes;
the fresh behavioral reviewer consumes those results and records observed behavior.
Native semantic correction review obtains both axes unchanged after checkpointing.
Selective correction checks and exemptions are not available until their later
implementation tickets land. Old checks cannot satisfy the new snapshot.
The tool validates freshness, not the semantic validity of retention justifications
or human fix authorization. Follow REVIEW.md for human direction, the two-attempt
pause and settled-decision escalation. Present the corrected scope and evidence
for human acceptance; history does not transfer acceptance to changed content.
