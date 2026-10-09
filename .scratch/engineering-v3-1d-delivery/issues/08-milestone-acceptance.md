# 08: Review and accept a milestone candidate

**What to build:** An explicitly requested milestone or release review assesses a pinned combined candidate and records the human acceptance decision without implying publication or merge.

**Blocked by:** [05: Carry honest evidence through corrections](05-correction-lineage.md), [07: Plan and recalibrate feature milestones](07-milestone-planning.md).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] Require explicit user instruction to start closure review, even when readiness is reported. Pin included specs/tickets, exclusions, comparison baseline, and exact candidate commit.
- [ ] Use one fresh architecture/maintainability reviewer and a separate fresh broad security reviewer. Inspect combined changes and system interactions while preserving applicable targeted ticket security obligations.
- [ ] Consume existing ticket evidence and request additional checks for identified gaps; do not automatically repeat every suite. Missing required independent review remains explicit.
- [ ] Append scope, report links, coverage gaps, findings, and the human acceptance decision to the existing breakdown.
- [ ] Blocking findings require fixes or explicit acceptance of the specific risk with rationale; preference-only suggestions do not block. Risk acceptance cannot turn failed checks or absent required proof into PASS.
- [ ] After changes, independently refresh affected conclusions, broaden for material scope/architecture/security/cumulative impact, and justify retained evidence. Bind final acceptance to the updated candidate.
- [ ] Neither milestone acceptance nor completed ticket delivery grants publication or merge authority.
- [ ] Interaction and evidence-boundary tests exercise readiness versus closure, role independence, historical coverage, specific risk acceptance, missing proof, and changed candidates. Deliver the complete skill/review interaction and consumer guidance.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
