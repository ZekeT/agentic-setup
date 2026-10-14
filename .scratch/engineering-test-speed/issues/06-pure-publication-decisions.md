# 06: Pure publication decisions

**What to build:** Publication gating (target, reviewed scope, review validity, authorization) is decided from a gathered facts value, reusing the verification facts where publication already consumes verification evidence, so publication rules are unit tested and only real-boundary publication scenarios stay end to end. See the [spec](../spec.md), "Facts value and pure decisions".

**Blocked by:** 05 (pure verification evidence decisions).

**Status:** ready-for-agent

**Review tier:** sensitive (publication modules)

- [ ] Publication gathers a plain, immutable facts value once per operation, reusing verification facts where it consumes verification evidence
- [ ] Target, reviewed-scope, review-validity and authorization gating are pure decisions, unit tested including each rejection message
- [ ] Each publication CLI-level scenario that only exercised a pure rule is removed only after an equivalent failing-when-broken unit test exists; each removal is noted in this ticket
- [ ] End-to-end tests remain for push and provider behavior (including the local Git HTTP server scenarios), recovery, and the greenfield journey, plus a small set proving the shell wires facts into decisions
- [ ] Publication behavior, CLI surface and messages are unchanged
- [ ] Local unit-tier and full-suite timings are recorded in this ticket
