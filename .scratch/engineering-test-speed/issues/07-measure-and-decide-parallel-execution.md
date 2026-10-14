# 07: Measure the suite and decide on parallel execution

**What to build:** With Git batching and the unit tier landed, the maintainer knows how long the unit tier and the full authoritative suite take against the target (unit tier in seconds; full suite inside `verify check` in about 1–2 minutes) and makes an explicit decision on whether parallel test execution is still worth a new dependency. See the [spec](../spec.md), "Sequencing" step 6.

**Blocked by:** 06 (pure publication decisions).

**Status:** ready-for-agent (needs a human decision at the end)

**Review tier:** documentation

- [ ] Local timings for the unit tier and the full engineering test target are recorded in this ticket, with machine load noted
- [ ] The slowest remaining tests are listed with their durations from a local profile (profiling is local investigation, not shipped tooling)
- [ ] The human decides whether to adopt parallel execution; the decision and reason are recorded here
- [ ] If adopted, a separate sensitive-tier ticket is created for the parallel runner; this ticket adds no dependency
- [ ] The 1800-second `verify check` command timeout is unchanged and no benchmark tooling ships in the harness
