# Engineering v3-1d delivery breakdown

Source: [Engineering v3-1d specification](../engineering-v3-1d/spec.md)
Breakdown approved by the user: 2026-10-07.

This directory holds implementation tickets; the completed [Wayfinder map](../engineering-v3-1d/map.md) and its decision tickets remain unchanged. The linked specification is authoritative; it is not duplicated here.

## Delivery boundaries

- Work in the single primary workspace. Use a fresh implementation session per ticket and switch to the intended branch safely; do not create persistent Git worktrees. Disposable test repositories and probe copies remain permitted.
- Each ticket includes applicable behavior, tests, documentation, and distribution changes. Keep existing gates until their replacements are implemented and verified; no ticket may borrow an unimplemented exemption.
- Preserve native Matt skills unchanged and unwrapped. The merged skill update and prepared PR-body handoff are baseline behavior.
- Status, verification, human acceptance, publication, and observed merge are distinct. No acceptance criteria are satisfied merely by publishing this breakdown.
- All tickets are ready-for-agent in triage terms, but work starts only after their blockers complete. The prerequisite-free tickets are scheduling options, not an instruction to work concurrently.

## Tickets

| Ticket | Blocked by | Status | PR |
| --- | --- | --- | --- |
| [01: Use native review evidence through publication](issues/01-native-review-evidence.md) | None | implemented | — |
| [02: Give prose changes appropriate assurance](issues/02-prose-assurance.md) | 01 | ready-for-agent | — |
| [03: Verify and publish mechanical bookkeeping](issues/03-mechanical-bookkeeping.md) | 02 | ready-for-agent | — |
| [04: Recognize genuinely inert comment changes](issues/04-inert-comments.md) | 02 | ready-for-agent | — |
| [05: Carry honest evidence through corrections](issues/05-correction-lineage.md) | 01, 02, 03 | ready-for-agent | — |
| [06: Synchronize one effort through a reusable PR](issues/06-tracker-sync.md) | 03 | ready-for-agent | — |
| [07: Plan and recalibrate feature milestones](issues/07-milestone-planning.md) | None | ready-for-agent | — |
| [08: Review and accept a milestone candidate](issues/08-milestone-acceptance.md) | 05, 07 | ready-for-agent | — |
| [09: Format only the intended scope](issues/09-intended-formatting.md) | None | ready-for-agent | — |
| [10: Remove duplicate checks and isolate reused fixtures](issues/10-check-fixture-optimization.md) | None | ready-for-agent | — |
| [11: Route shipping with a truthful fallback](issues/11-shipping-routing.md) | None | ready-for-agent | — |
| [12: Verify consumer transition and interrupted delivery](issues/12-consumer-transition.md) | 01, 02, 03, 04, 05, 06, 07, 08, 09, 11 | ready-for-agent | — |

## Initial frontier

Start with [Use native review evidence through publication](issues/01-native-review-evidence.md) for the core assurance path. Other unblocked choices are milestone planning, intended-scope formatting, check/fixture optimization, and shipping routing.

## Feature milestones

No milestone groupings or closure reviews have been agreed for delivery yet. The planned standalone milestone skill is itself part of this work; this ticket breakdown does not claim that capability already exists.

## Evidence and handoff

Ticket 01 is implemented. The user authorized its two bounded review fixes on 2026-10-09; both are applied, consumer metadata is regenerated, and the corrected recovery regression passes. The following review found two evidence-recovery defects; the user authorized their fix on 2026-10-10. Earlier failed checks and findings remain historical evidence. See the ticket and local `native-review-evidence` verification record for current snapshot-bound full checks and independent reports; implementation status does not imply independent verification or human acceptance. The other tickets remain planning only. No human acceptance, PRs, or merges are recorded. Update individual tickets and this table together as work progresses. The final consumer journey depends on tickets 01–09 and 11; ticket 10 can be delivered independently and is not a consumer-transition blocker.
