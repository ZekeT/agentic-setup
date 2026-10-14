# Spec: Fast engineering test feedback

Status: ready-for-agent

Source: [issue 01](issues/01-faster-engineering-test-feedback.md) (triaged 2026-10-14). Seams and standard location confirmed with the user on 2026-10-14.

## Problem Statement

People developing the starter (in the maintainer checkout) run the engineering test suite on nearly every harness change, and it also runs inside every `verify check`. The suite now takes 20–30 minutes and has exceeded the 1800-second `verify check` command timeout. When that happens, verification is blocked entirely. Even when it does not, routine development has no fast feedback loop: waiting for a run takes longer than writing the change.

The slowness has two causes, both measured:

- **The tool is slow.** One `verify status` on a three-file repository takes about 0.8 s, almost all of it in 47 separate Git subprocess calls (about 15 ms each). A typical verification test chains several CLI calls (prepare, check, record, status) and takes about 9 s.
- **The rules can only be tested end to end.** Verification decisions (staleness, tier floor, path classification, report validation, completeness) read Git directly while they decide. A real repository driven through the CLI is the only place to test them, so every new rule has added another slow CLI-level scenario. There is no unit tier (the unit test directory is empty).

## Solution

Three changes, in order:

1. **Fewer Git calls.** The verification modules gather the Git data they need with batched plumbing calls instead of one subprocess per question. Observable behavior is unchanged. Real verification runs and the existing suite both get faster.
2. **Gather facts, then decide (functional core, imperative shell).** Each module family gets one step that reads all the repository facts it needs (Git objects, files, settings, stored records) into a plain data value. Pure decision functions take that value and return a decision; they do no I/O. Most scenarios move into a new in-process unit tier that builds the facts value by hand. End-to-end CLI tests remain only where the real command boundary is the contract. The work goes one module family at a time, verification first, then publication.
3. **Durable guidance and a guard.** An ADR records why. A short maintainer-only testing standard tells implementers and Standards reviewers that pure decision logic is tested at the decision seam, not through the CLI. The unit tier fails any test that starts a subprocess.

Target: unit tests finish in seconds during development, and the full authoritative suite inside `verify check` finishes in about 1–2 minutes once steps 1 and 2 land. These are local measurements recorded in tickets, not promises in the shipped harness. The 1800-second command timeout stays unchanged.

## User Stories

1. As a starter maintainer, I want the engineering test suite to finish well inside the `verify check` command timeout, so that verification is never blocked by suite duration.
2. As a starter maintainer, I want a unit tier that runs in seconds, so that I get feedback while editing verification and publication rules.
3. As a starter maintainer, I want to run only the unit tier with one ordinary pytest invocation, so that my fast loop needs no special tooling.
4. As a starter maintainer, I want the authoritative full suite to still include the unit tier and the remaining end-to-end tests, so that `verify check` stays the single authoritative run.
5. As a starter maintainer, I want `verify status`, `prepare`, `check` and `record` to make far fewer Git subprocess calls, so that real verification is faster, not just the tests.
6. As a starter maintainer, I want Git batching to leave every observable verification result unchanged, so that existing evidence, snapshots and stored records stay valid.
7. As a starter maintainer, I want snapshot identities computed after batching to equal those computed before for the same content, so that batching does not mark existing evidence stale.
8. As a starter maintainer, I want baseline content to still be read as regular blobs without Git filters, links or archive rules, so that batching keeps the existing isolation guarantees.
9. As a starter maintainer, I want Git calls to keep the isolated Git environment (no system/global configuration, no replace objects, no prompts), so that batching does not weaken the trust boundary.
10. As a starter maintainer, I want verification decisions computed from a plain facts value, so that I can test a rule by writing the facts down instead of building a repository.
11. As a starter maintainer, I want the tier floor and per-path floor rules to be a pure function of role, ownership, settings and paths, so that I can test each floor rule in isolation.
12. As a starter maintainer, I want path classification (project, managed integration, installation metadata, maintainer tooling, agent policy, prose documentation) to be a pure function, so that classification edge cases are cheap to cover.
13. As a starter maintainer, I want required checks for a plan derived purely from role, ownership and classified paths, so that missing-check rejections are unit tested.
14. As a starter maintainer, I want report validation (fields, roles, verdicts, independence, snapshot match, native-axis fields) to be unit tested, so that every rejection message is covered without CLI runs.
15. As a starter maintainer, I want record validation, including carried-report history and cyclic-history rejection, to be decided from plain data, so that carried-evidence rules are unit tested.
16. As a starter maintainer, I want outcome and completeness (PASS, FAIL, INCOMPLETE, missing roles, shared reviewers, handoff text) to be unit tested, so that status semantics are pinned cheaply.
17. As a starter maintainer, I want staleness (current snapshot and identity versus stored record) decided from two plain values, so that STALE behavior is unit tested.
18. As a starter maintainer, I want plan validation separated from filesystem path checks where possible, so that plan-shape rules are unit tested.
19. As a starter maintainer, I want the behavioral-PASS precondition (successful recorded authoritative checks that match the plan) to be a pure decision, so that it is unit tested.
20. As a starter maintainer, I want publication gating decisions (target, reviewed scope, review validity, authorization) computed from a gathered facts value, so that publication rules are unit tested after verification.
21. As a starter maintainer, I want the facts-gathering step to read each Git fact once per operation, so that the shell is both fast and easy to reason about.
22. As a starter maintainer, I want the facts value to be plain, immutable data with no handles to the repository, so that a decision cannot secretly do I/O.
23. As a starter maintainer, I want end-to-end tests kept for non-mutation of the user's working tree and index, so that the most important safety guarantee is still proven at the real boundary.
24. As a starter maintainer, I want end-to-end tests kept for hooks, so that hook wiring is proven with real processes.
25. As a starter maintainer, I want end-to-end tests kept for retries and lock serialization, so that concurrency behavior is proven for real.
26. As a starter maintainer, I want end-to-end tests kept for publication, including the local Git HTTP server scenarios, so that push and provider behavior is proven at the boundary.
27. As a starter maintainer, I want one greenfield journey kept end to end, so that the whole installed workflow is proven once.
28. As a starter maintainer, I want each CLI-level scenario that only exercised a pure rule replaced by a unit test of the same rule, so that coverage is preserved, not dropped.
29. As a starter maintainer, I want each migrated scenario to keep at least one end-to-end test showing that the shell wires the rule in, so that a unit test passing cannot hide a broken shell.
30. As a starter maintainer, I want the unit tier to fail any test that starts a subprocess (Git, CLI, make), so that slow tests cannot quietly enter the fast tier.
31. As a starter maintainer, I want the subprocess guard to fail with a message naming the test and the attempted command, so that I can fix a misplaced test immediately.
32. As a starter maintainer, I want the subprocess guard to apply only to the unit tier, so that integration and end-to-end tests are unaffected.
33. As a fresh Standards reviewer, I want a documented maintainer testing standard saying that pure decision logic is tested at its decision seam and not through the CLI, so that I can flag new CLI-level tests for pure logic as a standards violation.
34. As a fresh Standards reviewer, I want that standard to sit where Standards review finds its sources, so that I apply it without special instructions.
35. As an implementer of a future verification or publication rule, I want the standard and the ADR to tell me where the rule and its test belong, so that new work follows the pattern without rediscovering it.
36. As a consumer project, I want my distributed coding standards, testing guide and testing style left unchanged, so that a starter-internal decision does not alter my project; consumer testing style stays with the pinned upstream `/tdd` skill.
37. As a future maintainer, I want an ADR recording the measured root cause, the decision and the rejected alternatives, so that nobody reverts to CLI-only testing or reaches for parallelism first without knowing why.
38. As a starter maintainer, I want each ticket to record local before-and-after timings, so that progress toward the target is visible without benchmark tooling in the shipped harness.
39. As a starter maintainer, I want to decide on parallel test execution only after Git batching and the unit tier land, so that a new dependency (and its sensitive review tier) is added only if the remaining time still justifies it.
40. As a starter maintainer, I want the `verify check` command timeout unchanged, so that the fix is to the suite, not to the limit.
41. As a starter maintainer, I want each module-family migration delivered as its own ticket, so that reviews stay small and an overlapping change can be serialized.
42. As a starter maintainer, I want the code tickets to start only after PR #50 merges, from updated `main`, so that they do not conflict with its changes to verification requirements and tests.
43. As a starter maintainer, I want the existing immutable shared preparation pattern (shared build, fresh writable copy, write guard) reused where end-to-end tests still need prepared repositories, so that the remaining end-to-end tests are as cheap as they safely can be.

## Implementation Decisions

**Sequencing.** Tickets run in this order:

1. ADR and maintainer testing standard. This is documentation-tier and can land first, independently of PR #50.
2. Git batching in the verification modules.
3. Unit tier and subprocess guard.
4. Verification family: facts value and pure decisions, with scenarios migrated.
5. Publication family: the same.
6. Measure, then decide on parallel execution.

Ticket 3 may combine with 4 if the guard alone is too small to review on its own. Code tickets begin after PR #50 merges, on a fresh branch from updated `main`. Tickets that touch the same modules are serialized.

**Git batching (verification modules).**
- Replace per-question Git subprocesses with batched plumbing: one recursive tree listing per baseline, `cat-file --batch` (or `--batch-check`) for object content and existence, and one listing for tracked, untracked and unmerged state where the current code makes several calls.
- Baseline reads made during requirement computation (role from the install state, the manifest, settings) come from the same batched baseline content, not from separate `ls-tree` and `show` calls per file.
- Keep the isolated Git environment, regular-blob validation, rejection of tracked verification records, and no-filter reads exactly as today.
- Snapshot identity, stored record schema, CLI output and error messages are unchanged. No schema version bump.

**Facts value and pure decisions (verification family first).**
- One gathering step per operation reads everything the decisions need into a plain, immutable facts value: plan, baseline file entries and the needed baseline contents, proposed file fingerprints, the recorded and baseline installation role, the manifest ownership entries, project review settings, the stored record and its history, and the declared tool results.
- Decision functions take the facts value (plus the request: plan, report, snapshot token) and return a result or raise the existing validation error. They read no files, start no processes and touch no clock or environment.
- Decisions moved behind this seam include: path classification; per-path and overall tier floor; required checks; tier-below-floor rejection; plan-shape validation; report validation; stored-record validation including carried history; staleness; outcome and completeness; and the behavioral-PASS precondition.
- The imperative shell (prepare, check, record, status) becomes: acquire lock → gather facts → decide → perform the writes and executions the decision calls for → print. Materializing the isolated checkout, running checks and writing evidence stay in the shell.
- Existing module boundaries (requirements, snapshot, checkout, carry, semantic) are kept where they are cohesive. The facts value is a new concept owned by the verification family, not a generic utility. Module size stays within the maintainability contract.
- Publication follows the same pattern in its own ticket after verification lands, reusing the verification facts where publication already consumes verification evidence.

**Unit tier and guard.**
- The unit tier lives in the starter's existing, currently empty unit test directory and runs as part of the existing engineering test target. No new Make target is required. The fast loop is an ordinary pytest invocation on that directory.
- A unit-tier fixture, applied automatically to every unit test, fails any attempt to start a subprocess. It names the test and the attempted command, mirroring the write guard from ticket 10 of `engineering-v3-1d-delivery`.
- Unit tests build facts values directly. Small builders for common facts shapes are allowed in the unit tier's own conftest. Builders must not read the real repository.

**Durable guidance.**
- New ADR (0004) records: the measured root cause (Git subprocess count; rules interleaved with I/O), the decision (batching first, then facts value plus pure decisions, with the unit tier and guard), which end-to-end contracts remain, the unchanged timeout, parallelism deferred, and the rejected alternatives (parallelism first, raising the timeout, mocking Git in unit tests, dropping scenarios).
- A short maintainer-only testing standard goes in a non-distributed location that Standards review picks up as a standards source, linked from the ADR. It says: put pure decision logic behind the family's decision seam and unit test it there; keep CLI-level tests for real-boundary contracts; a new CLI-level test that only exercises a pure rule is a standards violation.
- The distributed coding standards, testing guide, ENGINEERING.md and the template manifest are not changed. No feature-local instruction file is added unless the standard proves insufficient.

**Review tiers.** Git batching and the facts refactor touch verification and publication modules, which are maintainer-sensitive paths, so those tickets take the sensitive tier. Adding a parallel-runner dependency would also be sensitive. The ADR and standard ticket is documentation-tier unless it touches agent-policy files.

## Testing Decisions

- **What makes a good test here:** it asserts an observable decision (the returned classification, floor, outcome, or the validation error and its message) for a given facts value. It does not assert which helper ran, how many Git calls happened, or private intermediate structures. Renaming a private function must not break a unit test.
- **Git batching:** the existing integration suite is the safety net and must stay green unchanged. No new seam, no call-count assertions and no timing assertions. Before-and-after timings are measured locally and recorded in the ticket.
- **Verification decisions:** unit tests at the facts-value seam cover each floor rule, each classification category, each plan and report rejection, carried-history acceptance and rejection, staleness, and every outcome status. Use boundaries: empty, one and many paths; mixed prose and non-prose; base versus proposed role; and settings that add floors.
- **Shell wiring:** for each migrated family, keep a small set of end-to-end CLI tests proving that gathered facts reach the decisions and that decisions drive the writes. Keep all real-boundary contract tests: non-mutation of the user's working tree and index, hooks, retries and locks, publication (including the local Git HTTP servers), and the greenfield journey.
- **Migration discipline:** a CLI-level scenario is removed only when an equivalent unit test exists and fails if the rule is broken. Each removal is noted in the ticket, so coverage is moved, not dropped.
- **Guard:** the subprocess guard has its own test showing that a unit test which starts a subprocess fails, with the expected message.
- **Prior art:** the immutable shared preparation and write guard in the engineering test support (shared build, fresh writable copy, teardown comparison); the existing verification, review-tier, verification-requirements and prose-assurance integration tests, which list the scenarios to migrate; and the distributed testing guide's rule that a unit test never touches the filesystem or subprocesses.
- **Authoritative run:** `verify check` still runs the full engineering test target, which includes the unit tier, the remaining integration and end-to-end tests, lint and types.

## Out of Scope

- Changing consumer projects' testing style, distributed coding standards or testing guide, or the template.
- Raising or removing the 1800-second `verify check` command timeout.
- Shipping benchmark tooling, timing reports, performance diagnostics or numeric speedup promises in the harness.
- Adding a parallel test runner in this spec. That decision follows the measurement ticket and, if chosen, gets its own sensitive-tier ticket.
- Replacing real-boundary guarantees (non-mutation, hooks, retries, publication) with mocks.
- Running the CLI in-process to save interpreter start-up. Measured at about 0.05 s per call, it is not worth it.
- Refactoring modules outside the verification and publication families, such as installation, updates, migration, doctor or graft.
- Changing verification record schema, snapshot identity, CLI surface or review-tier policy.

## Further Notes

- The measurements behind this spec are in the source issue's triage outcome: 9 s per typical verification test, 47 Git calls per `verify status`, and about 20 minutes (quiet machine) to 31 minutes (loaded machine) for 566 serial tests.
- PR #50 (ticket 02 of `engineering-v3-1d-delivery`) changes verification requirements and tests. All code tickets here wait for it to merge.
- When a long full run is unavoidable before this lands, check machine load first. The suite is near the timeout.
- Ticket breakdown follows via `/to-tickets` into this directory's `issues/`, numbered after the existing source issue.
