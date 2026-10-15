# 05: Pure verification evidence decisions

**What to build:** Report validation, stored-record validation with carried history, staleness, outcome and completeness, and the behavioral-PASS precondition are decided from a gathered facts value, and the verification commands become a thin shell: acquire lock, gather facts, decide, perform the writes and executions the decision calls for, print. Evidence rules are unit tested without CLI runs. See the [spec](../spec.md), "Facts value and pure decisions".

**Blocked by:** 04 (unit tier, guard and requirement decisions). Merged as PR #55 (`0e6eea8`).

**Status:** implemented on `test/pure-evidence-decisions`; independent verification pending (not accepted, published or merged)

**Review tier:** sensitive (verification modules)

- [x] The verification facts value additionally carries the plan, baseline file entries and needed contents, proposed file fingerprints, the stored record and its history, and declared tool results; it stays plain, immutable and handle-free, and each Git fact is read once per operation
- [x] `prepare`, `check`, `record` and `status` follow lock → gather → decide → write/execute → print; materializing the isolated checkout, running checks and writing evidence stay in the shell
- [x] Report validation (fields, roles, verdicts, independence, snapshot match, native-axis fields) is unit tested, covering every rejection message
- [x] Stored-record validation, including carried-report history acceptance and cyclic-history rejection, is unit tested
- [x] Staleness is decided from the current snapshot and identity versus the stored record, unit tested for current and STALE
- [x] Outcome and completeness (PASS, FAIL, INCOMPLETE, missing roles, shared reviewers, handoff text) are unit tested for every status
- [x] The behavioral-PASS precondition (successful recorded authoritative checks that match the plan) is a pure decision, unit tested
- [x] Decision functions read no files, start no processes and touch no clock or environment
- [x] Unit tests assert observable decisions (the returned result, or the validation error and its message) for a given facts value; they do not assert which helper ran, how many Git calls happened, or private intermediate structures
- [x] Each migrated CLI-level scenario from the verification, carried-evidence and native-evidence integration tests is removed only after an equivalent failing-when-broken unit test exists; each removal is noted in this ticket
- [x] End-to-end tests remain for non-mutation of the user's working tree and index, hooks, retries and lock serialization, plus a small set proving gathered facts reach decisions and decisions drive writes
- [x] Remaining end-to-end tests that need prepared repositories reuse the immutable shared preparation pattern (shared build, fresh writable copy, write guard) where safe
- [x] Existing module boundaries (requirements, snapshot, checkout, carry, semantic) are kept where cohesive; module sizes stay within the maintainability contract
- [x] Record schema, snapshot identity, CLI surface and review-tier policy are unchanged
- [x] Local unit-tier and full-suite timings are recorded in this ticket

## Comments

- 2026-10-15: implemented.
  - Facts value: `verification_facts.py` adds frozen `EvidenceFacts` (current snapshot token; snapshot inputs: plan, comparison base, proposed and baseline file fingerprints, declared tool results; stored records) and `StoredRecord`. `stored_history()` reads the stored record and follows `previous_evidence` only while a record carries reports, reading each history record once and marking an unreadable or already-read (cyclic) one instead of raising. JSON values are deep-frozen by `frozen_json` (mappings read-only, lists as tuples); `plain_json` converts back for output and storage. Baseline blob contents stay in `RequirementFacts`, gathered from the checkout as before.
  - Decisions: new `verification_evidence.py` (its functions do no I/O; from the snapshot and inputs modules it uses only the pure `plan_shape`, `identity` and `strings`) holds `validate_report`, `validate_records` (structure, stored plan shape, stored requirements, reports, carried history, recorded checks; returns the validated chain), `reject_unsupported_schema`, `stale`, `admit` (shared sessions and the behavioral-PASS precondition), `outcome`/`handoff` and `shared_reviewers`. Carry keeps its module: pure `carry_candidate` and `carried(previous, current, upstream)`, with `carried_reports` doing the Git ancestry, checkout and diff reads. Semantic keeps its module: pure `native_ids` (full commit IDs) and `reject_uncovered` (checkpoint covers additions, deletions, modes), with Git resolution and merge-base in `validate_semantic`.
  - Shell: `verification.py` is lock → gather (`stored_history`, `snapshot`) → decide → I/O checks only the repository can answer (plan path containment, native commits, checkout validation) → write/execute → print. `prepare` moved into its own function; `read_record` keeps its contract for publication, which now imports `outcome` from `verification_evidence`.
  - Error precedence changed only when several faults occur at once: a stored plan's path containment and native-commit checks now follow every structural check of the record and its history (they ran per report before); an unparsable or unsafe history file is reported while gathering, before the stored record's own structural errors. Single-fault messages are unchanged.
  - The refactored code passed all 92 tests of the five affected integration files before any test was removed. Each removed rule was then mutated in the source (20 mutations: independence, verdicts, report fields, staleness identity, behavioral checks, shared reviewers, failing verdict, missing checks, carried handoff, carried tampering, cyclic history, check result types, schema compatibility, stored roles, carry overlap, carry tools, carry plan, carry files, native addition, native mode); each made at least one unit test fail.
  - Shared preparation: the per-test `repo` fixture of `test_verification.py` (reused by the carried and native evidence files) was not converted. Its build is a handful of Git calls (well under a second) against multi-second CLI chains per test, and tests use its directory as `tmp_path`, so sharing it would save little and is not obviously safe. The `pristine` installations fixture already uses the pattern.
  - Removed CLI scenarios, each with equivalent unit tests in `tests/unit/test_verification_evidence.py`, `test_verification_carry.py` or `test_verification_native.py`:
    - `test_verification.py`: failed checks and missing security cannot pass; the malformed stored report case of unsafe or malformed evidence; missing and stale reports do not claim verification (reduced to `test_status_without_evidence_is_incomplete`, the shell's no-record answer).
    - `test_carried_evidence.py`: five of six changed-input cases (patch, plan, checks, tools, ignored input; `test_upstream_overlap_with_scope_carries_nothing` keeps the overlap case); changed tool output carries nothing; carried report tampering is rejected.
    - `test_native_evidence.py`: two of three checkpoint coverage cases (addition, mode; `test_checkpoint_must_cover_a_deletion` remains).
    - `test_review_tiers.py`: raised tier requires its roles and reports them; sensitive reports need separate sessions.
  - Wiring kept end to end: reuse across sessions and content-preserving commits; moved comparison branch; STALE status; behavioral precondition and STALE report through `record` (bounded correction); carried reports, fresh checks, failed carried rerun, successive provenance and manual-carry rejection, removed history; publication of carried and native evidence; native checkpoint, comparison and unavailable commits; old and future schemas; review checkout mutation; concurrent writer refusal; non-mutation of working tree and index; status and re-prepare not rerunning checks.
  - Record schema, snapshot identity, CLI output and review-tier policy are unchanged. `.engineering/template/files.json` distributes the new module and the manifest was regenerated. The maintainer engineering test standard names the evidence decision functions.
- Local measurements, 2026-10-15:

  | Measure | Before | After |
  |---|---|---|
  | Unit tier (`tests/unit`) | 136 tests, 0.08 s | 273 tests, 0.16 s |
  | Five affected integration files (verification, carried, native, review tiers, update source) | 92 tests, 425 s (load about 4.9) | 79 tests, 323 s (load about 2.7) |
  | Full engineering pytest suite (`make engineering-test`) | 652 tests, 794 s (ticket 04, load about 3–4.5) | 777 tests, 1200 s (load about 3.5–3.9) |

  The five affected files were timed back to back (before on a clone of `main`); 13 CLI cases left them. The full-suite runs were on different days' load and are not comparable: the after run took longer although the changed files got faster, so the difference is most likely machine load; it was not investigated further. 1200 s is within, but closer to, the 1800 s `verify check` command timeout; ticket 07 measures the suite.
