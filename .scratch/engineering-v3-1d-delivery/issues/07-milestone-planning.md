# 07: Plan and recalibrate feature milestones

**What to build:** Standalone /milestones helps the user agree outcome-based feature groups after native /to-tickets and revisit stale plans as implementation reveals new information.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] Read the existing spec, tickets, and dependencies; recommend demonstrable outcomes or coherent integration points and explain boundaries rather than grouping by a fixed ticket count.
- [ ] Discuss the proposal and user-requested splits, combinations, renames, and moves before recording it. Surface dependency conflicts rather than silently rewriting requirements.
- [ ] Record outcomes, original ticket links, completion conditions, and review/acceptance state in a milestone section of the existing breakdown without copying ticket bodies.
- [ ] On later invocation, compare plans with implementation and available evidence, identify stale assumptions or scope, and recommend recalibration. Discuss substantive changes before updating agreed milestone and affected tracker content together.
- [ ] Preserve reasons, missing historical proof, and the distinction between implementation, verification, publication, merge, and acceptance. Existing implementation does not approve changed requirements; material scope changes use the native spec/ticket workflow.
- [ ] Recalibration is substantive planning, not mechanical bookkeeping. Readiness can be reported, but closure review and acceptance are not started automatically.
- [ ] Keep the skill standalone and Matt skills unchanged/unwrapped; installation does not adopt /implement-spec. Use the primary workspace only.
- [ ] Interaction scenarios cover user alterations, dependency conflicts, stale requirements, original-ticket references, missing evidence, and readiness without automatic closure. Ship the skill and appropriate consumer guidance; distinguish static contract coverage from actual model behavior.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
