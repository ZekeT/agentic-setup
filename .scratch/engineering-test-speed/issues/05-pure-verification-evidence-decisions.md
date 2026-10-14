# 05: Pure verification evidence decisions

**What to build:** Report validation, stored-record validation with carried history, staleness, outcome and completeness, and the behavioral-PASS precondition are decided from a gathered facts value, and the verification commands become a thin shell: acquire lock, gather facts, decide, perform the writes and executions the decision calls for, print. Evidence rules are unit tested without CLI runs. See the [spec](../spec.md), "Facts value and pure decisions".

**Blocked by:** 04 (unit tier, guard and requirement decisions).

**Status:** ready-for-agent

**Review tier:** sensitive (verification modules)

- [ ] The verification facts value additionally carries the plan, baseline file entries and needed contents, proposed file fingerprints, the stored record and its history, and declared tool results; it stays plain, immutable and handle-free, and each Git fact is read once per operation
- [ ] `prepare`, `check`, `record` and `status` follow lock → gather → decide → write/execute → print; materializing the isolated checkout, running checks and writing evidence stay in the shell
- [ ] Report validation (fields, roles, verdicts, independence, snapshot match, native-axis fields) is unit tested, covering every rejection message
- [ ] Stored-record validation, including carried-report history acceptance and cyclic-history rejection, is unit tested
- [ ] Staleness is decided from the current snapshot and identity versus the stored record, unit tested for current and STALE
- [ ] Outcome and completeness (PASS, FAIL, INCOMPLETE, missing roles, shared reviewers, handoff text) are unit tested for every status
- [ ] The behavioral-PASS precondition (successful recorded authoritative checks that match the plan) is a pure decision, unit tested
- [ ] Decision functions read no files, start no processes and touch no clock or environment
- [ ] Unit tests assert observable decisions (the returned result, or the validation error and its message) for a given facts value; they do not assert which helper ran, how many Git calls happened, or private intermediate structures
- [ ] Each migrated CLI-level scenario from the verification, carried-evidence and native-evidence integration tests is removed only after an equivalent failing-when-broken unit test exists; each removal is noted in this ticket
- [ ] End-to-end tests remain for non-mutation of the user's working tree and index, hooks, retries and lock serialization, plus a small set proving gathered facts reach decisions and decisions drive writes
- [ ] Remaining end-to-end tests that need prepared repositories reuse the immutable shared preparation pattern (shared build, fresh writable copy, write guard) where safe
- [ ] Existing module boundaries (requirements, snapshot, checkout, carry, semantic) are kept where cohesive; module sizes stay within the maintainability contract
- [ ] Record schema, snapshot identity, CLI surface and review-tier policy are unchanged
- [ ] Local unit-tier and full-suite timings are recorded in this ticket
