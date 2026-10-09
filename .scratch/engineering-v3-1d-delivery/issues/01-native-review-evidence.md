# 01: Use native review evidence through publication

**What to build:** A code-changing issue can be checkpointed, reviewed by native Matt skills, checked once, independently assessed, and published using evidence bound to its actual reviewed content.

**Blocked by:** None (can start immediately).

**Status:** implemented

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [x] Ordinary scoped checkpoint commits include all intended additions, deletions, and mode changes before native committed-diff review; later uncovered edits prevent publication.
- [x] Native Standards and Spec results are recorded as distinct semantic evidence bound to the reviewed commit, comparison context, and content identity. Replace the overlapping ticket-level harness maintainability pass without modifying, wrapping, copying, or intercepting upstream orchestration.
- [x] The implementer can execute the initial full applicable suite once through recorded harness execution. Fresh behavioral inspection consumes that evidence; separate targeted security review remains required for affected sensitive responsibilities.
- [x] Plan, tools, dependencies, explicit inputs, and content freshness remain enforced. Independent reviewers receive requirement/content pointers and factual evidence; missing independent roles remain INCOMPLETE rather than self-certified.
- [x] Captured content remains immutable, mutating probes use disposable copies, and evidence writes are serialized. Native workflow restrictions govern scheduling.
- [x] An explicit evidence-version transition preserves old records as history, requires fresh proof, and rejects unsupported schemas with recovery guidance. Old maintainability reports cannot become Standards or Spec proof.
- [x] A public-command journey proves initial check execution once, complete versus missing roles, stale/uncommitted content rejection, and publication consuming the current proof without repeating checks. Preserve exact prepared-body delivery, authorization, hooks, retry safety, and no merge authority.
- [x] Deliver applicable consumer metadata, transition guidance, runtime-facing instructions, and regression coverage with this slice. Activate only implemented policy replacements; later exemptions and correction reuse remain unavailable until their tickets land.

## Comments

Implemented on `feat/native-review-evidence`. The checked criteria describe implemented behavior and regression coverage, not human acceptance or publication.

- Evidence schema 3 records distinct native Standards/Spec reports with commit/comparison identities; older supported records remain history. Captured source is separate from check execution, and evidence/publication operations share a per-change lock.
- Public-command coverage: `.engineering/tests/integration/test_native_evidence.py`; existing verification, review-tier, clean-rebase, greenfield and publication journeys were updated to use ordinary scoped checkpoints and the new roles.
- Implementation-stage evidence: nine native-evidence scenarios passed; all 13 static policy evaluations passed; type checking passed. The full recorded run on implementation commit `c90ba8a` passed `make check`, `make engineering-check`, and all 13 static evaluations. `make engineering-test` reported 558 passed and one failed recovery assertion.
- Current independent verification: `.engineering/state/verification/native-review-evidence-plan.json` and `./engineering verify status --change native-review-evidence`. The local record identifies the exact snapshot, current check results, reviewer findings and missing roles. Implementation status and checked criteria do not assert independent PASS; consult that record. Reports/checks are ignored local evidence, not portable to another checkout.
- Historical review of snapshot `c0ccb37f782d2ebae2bbf04f585bb17eae771acfdd3de2348ec3341e3a955a95`: Standards and targeted Security passed; Spec identified contradictory native-review location instructions and Behavioral failed on the recovery test's old artifact path. These reports remain history and must not be relabelled as current proof.
- User authorized both bounded fixes on 2026-10-09. Distributed instructions now direct unchanged native review to the actual checkpointed repository and behavioral/security inspection to captured source. The recovery test reads `check_checkout` and retains its exact one-execution assertion; its targeted regression passed (1 test). Consumer metadata was regenerated. Fresh full checks and independent reports for the corrected scope belong in the current local record; no correction-check reuse or exemption is claimed.
- Review of snapshot `9d70e557…` (checkpoint `9cd440e`): Spec and Security PASS; Standards CONCERNS (subject-only commit messages, minor naming/duplication judgement calls); Behavioral FAIL with two blocking recovery defects: prepare crashed when a native reviewed commit had been pruned, and a removed earlier evidence folder broke carried-history reads. These reports remain history.
- User authorized the recovery fix on 2026-10-10. An unreadable schema-3 record is now preserved as non-reusable history, so prepare requires fresh proof; a pruned reviewed commit and missing carried history report actionable INCOMPLETE errors; `verification.md` documents the dependency. Regressions: `test_unavailable_reviewed_commit_is_history_not_proof` and `test_removed_history_folder_requires_fresh_proof`. Existing commits are not reworded because that would orphan their native review bindings.
- Review of snapshot `8d4ad67c…` (checkpoint `9f57115`, not recorded): Spec and Security PASS; Standards CONCERNS that prepare silently swallowed the reason for non-reuse; Security noted remaining raw git errors (e.g. unrelated `merge-base`) still crashed prepare. User authorized both fixes on 2026-10-10: prepare now reports `history_note` and treats any git failure while validating an existing record as non-reusable history. Regression: `test_unrelated_comparison_history_is_not_reused`.
- Follow-up (not in this ticket's scope): a raised check-execution error (timeout/interrupt) does not drop a carried behavioral report; pre-existing behavior.
- Follow-up (not in this ticket's scope): superseded `checks-*` disposable copies are never removed (~400–500 MB each).
- No human acceptance, push, PR/MR, or merge is recorded. Later documentation/bookkeeping exemptions and correction-check reuse remain unavailable.

