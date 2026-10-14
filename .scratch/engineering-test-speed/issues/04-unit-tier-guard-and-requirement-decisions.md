# 04: Unit tier, subprocess guard and pure verification requirement decisions

**What to build:** Maintainers get a unit tier that runs in seconds with one ordinary pytest invocation and that refuses to start subprocesses. Verification requirement rules (path classification, tier floors, required checks, plan shape) are decided from a plain facts value, so each rule is unit tested by writing the facts down instead of building a repository. See the [spec](../spec.md), "Unit tier and guard" and "Facts value and pure decisions".

**Blocked by:** 02 (ADR and maintainer testing standard), 03 (batched Git reads).

**Status:** ready-for-agent

**Review tier:** sensitive (verification modules)

- [ ] The existing, currently empty unit test directory holds the unit tier; it runs inside the existing engineering test target, and the fast loop is an ordinary pytest invocation on that directory
- [ ] An automatically applied unit-tier fixture fails any test that starts a subprocess, naming the test and the attempted command; it does not apply to integration or end-to-end tests
- [ ] A test shows that a unit test which starts a subprocess fails with the expected message
- [ ] A plain, immutable requirements facts value (installation role at baseline and proposed, manifest ownership entries, project review settings, paths) is gathered once per operation and holds no repository handles
- [ ] Path classification (project, managed integration, installation metadata, maintainer tooling, agent policy, prose documentation) is a pure function, unit tested per category
- [ ] Per-path and overall tier floor is a pure function of role, ownership, settings and paths, unit tested per floor rule
- [ ] Required checks and missing-check rejection derive purely from role, ownership and classified paths, unit tested
- [ ] Tier-below-floor rejection and plan-shape validation (separated from filesystem path checks where possible) are unit tested, including each rejection message
- [ ] Unit tests cover boundaries: empty, one and many paths; mixed prose and non-prose; base versus proposed role; settings that add floors
- [ ] Decision functions read no files, start no processes and touch no clock or environment
- [ ] Unit tests assert observable decisions (the returned result, or the validation error and its message) for a given facts value; they do not assert which helper ran, how many Git calls happened, or private intermediate structures
- [ ] Unit-tier builders live in the unit tier's own conftest and never read the real repository
- [ ] Each CLI-level scenario from the verification-requirements, review-tier and prose-assurance integration tests that only exercised a pure rule is removed only after an equivalent unit test exists that fails when the rule breaks; each removal is noted in this ticket
- [ ] At least one end-to-end test per migrated rule group still shows the shell wires the gathered facts into the decision
- [ ] Remaining end-to-end tests that need prepared repositories reuse the immutable shared preparation pattern (shared build, fresh writable copy, write guard) where safe
- [ ] Verification record schema, snapshot identity, CLI surface and review-tier policy are unchanged
- [ ] Local unit-tier and full-suite timings are recorded in this ticket
