# 05: Carry honest evidence through corrections

**What to build:** A bounded correction can reach publication using independently validated current checks and honestly retained earlier coverage, with cumulative escalation when the change is no longer bounded.

**Blocked by:** [01: Use native review evidence through publication](01-native-review-evidence.md), [02: Give prose changes appropriate assurance](02-prose-assurance.md), [03: Verify and publish mechanical bookkeeping](03-mechanical-bookkeeping.md).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] Each correction links to its predecessor and last successful full-suite snapshot, identifying current content, executed checks, scope rationale, retained coverage, independent assessment, and unresolved findings.
- [ ] The implementer proposes affected-behavior checks; an independent reviewer can reject the selection and require broader checks. Cross-cutting or uncertain individual or cumulative impact requires the full applicable suite.
- [ ] Code corrections receive fresh behavioral inspection. Native semantic correction review uses both Standards and Spec when required; security returns when affected. Retaining other coverage requires independently checked justification rather than unchanged bytes alone.
- [ ] Documentation-only corrections follow their relevant-check route; validated bookkeeping retains proof only within its approved eligibility/input boundaries.
- [ ] Missing or untrustworthy history, broken anchors, unresolved prior failures, and uncertain combined impact prevent reuse. A later passing check cannot erase an unresolved finding.
- [ ] Status and publication distinguish historical full-suite coverage from current correction checks; sufficient lineage can pass without claiming the suite ran on final revised content or rerunning it at shipping.
- [ ] Preserve strict clean-rebase carry conditions and full applicable reruns on rebased content. Remote-tip-only refresh and content-preserving commits retain proof when identity safeguards permit.
- [ ] Public-command journeys cover several cumulative corrections, escalation, rejected check selection, historical failures, stale inputs, documentation/bookkeeping transitions, clean rebases, and remote refresh.
- [ ] Version any changed lineage contract explicitly, preserve prior history, and ship consumer transition and policy guidance. Do not prematurely enable inert-comment behavior if its separate ticket has not landed.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
