# 10: Remove duplicate checks and isolate reused fixtures

**What to build:** Required assurance runs without proven duplicate starter-owned checks, while reusable immutable test preparation reduces repeated setup without sharing writable state.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] Remove actual overlap in starter-owned check composition while preserving useful independent command behavior. Required coverage must have explicit execution evidence before a check is treated as already satisfied.
- [ ] Preserve consumer-owned check recipes; do not assume an adopted application gate includes harness health checks. Keep distinct application and engineering suites where applicable.
- [ ] Reuse immutable fixture preparation only with fresh writable copies. Preserve independent Git history, publication state, failure scenarios, and meaningful scenario coverage.
- [ ] Keep initial full applicable suite obligations and separate behavioral judgment. This optimization cannot relabel missing checks as PASS or drop tests merely to reduce runtime.
- [ ] Observable tests prove standalone commands retain their checks, composed execution avoids the identified duplicate, arbitrary consumer recipes remain safe, and writable fixture mutations do not leak.
- [ ] Deliver affected recipes, fixture behavior, distribution metadata, and instructions without adding diagnostics, benchmarks, token telemetry, or numeric speedup promises.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
