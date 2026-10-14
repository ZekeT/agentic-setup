# 10: Remove duplicate checks and isolate reused fixtures

**What to build:** Required assurance runs without proven duplicate starter-owned checks, while reusable immutable test preparation reduces repeated setup without sharing writable state.

**Blocked by:** None (can start immediately).

**Status:** merged

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [x] Remove actual overlap in starter-owned check composition while preserving useful independent command behavior. Required coverage must have explicit execution evidence before a check is treated as already satisfied.
- [x] Preserve consumer-owned check recipes; do not assume an adopted application gate includes harness health checks. Keep distinct application and engineering suites where applicable.
- [x] Reuse immutable fixture preparation only with fresh writable copies. Preserve independent Git history, publication state, failure scenarios, and meaningful scenario coverage.
- [x] Keep initial full applicable suite obligations and separate behavioral judgment. This optimization cannot relabel missing checks as PASS or drop tests merely to reduce runtime.
- [x] Observable tests prove standalone commands retain their checks, composed execution avoids the identified duplicate, arbitrary consumer recipes remain safe, and writable fixture mutations do not leak.
- [x] Deliver affected recipes, fixture behavior, distribution metadata, and instructions without adding diagnostics, benchmarks, token telemetry, or numeric speedup promises.

## Comments

Approved as part of the 12-ticket breakdown.

Implemented on `feat/check-fixture-optimization`. The checked criteria describe implemented behavior and regression coverage, not independent verification, human acceptance or publication.

- Identified duplicate: when a plan records both `make check` and `make engineering-check`, the starter's `make check` repeated doctor and maintainability. `verify check` now sets `ENGINEERING_HEALTH_RECORDED_SEPARATELY` only for the `make check` command, and only when `make engineering-check` is in the same plan; inherited values are stripped. The starter check script then skips its own doctor/maintainability pass. Coverage comes from the separately recorded health result, which outcome already requires before PASS. Standalone `make check` and `make engineering-check` keep both checks. Consumer-owned recipes ignore the signal and run unchanged. Required-check derivation is unchanged.
- Fixture reuse: one session-scoped consumer template build (`conftest.py` `built_template`/`generated`) replaces repeated builds in template, navigation, greenfield and requirements tests. The pinned-update source and consumer are prepared once per module and copied, including Git history, for each test. `immutable.unchanged` fails teardown if a test writes to shared preparation. Reproducibility and build-refusal tests still build fresh.
- Tests: `test_checks.py` (composed deferral, inherited-variable and consumer-recipe safety; existing standalone test keeps both checks) and `test_immutable.py` (shared-preparation write guard).
- Docs: `ENGINEERING.md`, `.engineering/docs/verification.md`, `.engineering/docs/testing.md`; manifest and install metadata regenerated. No diagnostics, benchmarks or speedup claims.
- First review (snapshot `7547c010…`, checkpoint `b617c9b`): all four checks passed (571 tests; 13/13 evals); Spec, Behavioral and Security PASS; Standards CONCERNS (mixed-idea commit, duplicated template build, naming and test-literal judgement calls). Behavioral and Security noted, non-blocking, that deferral trusts the reviewed `engineering-check` recipe and that an exported variable affects standalone `make check`; the user chose not to harden either. These reports remain history.
- User authorized on 2026-10-10: fix the Standards findings and Spec bookkeeping, split the commit, and remove unnecessary or tautological tests after auditing the whole suite. Removed as tautological in this ticket's additions: the copy-isolation test (only exercised `copytree`), a no-op guard assertion, and a standalone `engineering-check` assertion on a recipe that never reads the variable. Removed from the existing suite as redundant: `test_upstream_explicit_input_overlap_carries_nothing` (its forced plan change empties reports regardless of the overlap rule), `test_managed_implementation_edit_still_conflicts` (same scenario as `test_both_changed_conflicts_without_advancing_baselines`), `test_ordinary_roles_require_independent_sessions` (subsumed by the sensitive separate-session test), and `test_check_mutations_never_produce_current_proof` (merged into the native capture-immutability test); three body assertions implied by exact equality were also dropped. No unique behavior lost.
- Review of the rebuilt commits (snapshot `d48470a5…`): Spec PASS; Standards CONCERNS that the composed-execution test rebuilt the shared `repo` fixture and that the root `conftest.py` imported a test module. User authorized both fixes on 2026-10-10: the test now uses the shared fixture, and `template_build.py` holds the build helper. Two full check runs on that snapshot exceeded the 1800-second command timeout under unrelated machine load (profile: 566 passed in 31 minutes, no hang, same per-test time on `main`); suite speed is tracked separately in `.scratch/engineering-test-speed/`.
- Fresh full checks and independent reviews for the corrected scope are pending in the local verification record.
- 2026-10-10: final evidence on snapshot `887ec054…` PASS (all four checks: 566 tests, 13/13 evals; Standards, Spec, Behavioral, Security PASS). Human accepted the presented scope via /ship; published as PR #49 (not merged). Merge remains a separate human decision.
- 2026-10-10: CI on PR #49 failed `test_invalid_committed_source_distribution_is_rejected` (Git 2.55 on the runner). Cause: background loose-object maintenance after the test's commit raced the dumb-HTTP fixture server; the old per-test setup was slow enough to hide it. Reproduced locally by enabling the same maintenance task under Git 2.50 (fails before, passes after). Fix: disable automatic gc and maintenance in the update fixture repositories. Re-verification and renewed publication authorization are required before pushing.
- 2026-10-11: fix verified on snapshot `e8b420db…` PASS (all four checks: 566 tests, 13/13 evals; Standards, Spec, Behavioral, Security PASS; Behavioral reproduced the race 3/3 before the fix and 0/3 after). The human had closed PR #49 before the push; after /ship pushed the fix (no force-push), the human chose to reopen PR #49 at head `3605731`. CI passed on `3605731` (Git 2.55 runner: 566 tests, 13/13 evals). Not merged.
- 2026-10-11: PR #49 observed merged into `main` as `ea25766` (local time 01:28 +0800; GitHub `mergedAt` 2026-10-10T17:28:15Z).
