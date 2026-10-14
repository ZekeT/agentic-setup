# 02: ADR 0004 and maintainer testing standard

**What to build:** Future maintainers, implementers and fresh Standards reviewers can find out why engineering tests are structured around a facts value and pure decisions, and where a new verification or publication rule and its test belong. A new CLI-level test that only exercises a pure rule becomes a reviewable standards violation. See the [spec](../spec.md), "Durable guidance".

**Blocked by:** None (can start immediately; independent of PR #50).

**Status:** ready-for-agent

**Review tier:** documentation (unless it touches agent-policy files)

- [ ] ADR 0004 records the measured root cause (Git subprocess count: 47 calls per `verify status`, about 9 s per typical verification test; rules interleaved with I/O)
- [ ] ADR 0004 records the decision: Git batching first, then a facts value plus pure decisions per module family, with the unit tier and subprocess guard
- [ ] ADR 0004 lists the end-to-end contracts that remain (non-mutation of working tree and index, hooks, retries and locks, publication including local Git HTTP servers, one greenfield journey)
- [ ] ADR 0004 records the unchanged 1800-second `verify check` command timeout and that parallel execution is deferred until after measurement
- [ ] ADR 0004 records the rejected alternatives: parallelism first, raising the timeout, mocking Git in unit tests, dropping scenarios
- [ ] A short maintainer-only testing standard exists in a non-distributed location that Standards review picks up as a standards source, and the ADR links to it
- [ ] The standard says: put pure decision logic behind the family's decision seam and unit test it there; keep CLI-level tests for real-boundary contracts; a new CLI-level test that only exercises a pure rule is a standards violation
- [ ] The ADR index lists ADR 0004
- [ ] Distributed coding standards, the testing guide, ENGINEERING.md and the template manifest are unchanged; no feature-local instruction file is added
