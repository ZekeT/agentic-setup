# Link correction checks and retained evidence honestly

Type: grilling
Status: resolved
Blocked by: 01, 02
Parent: [Engineering v3-1d decision map](../map.md)

## Question

How should the harness link an issue PR's initial full applicable suite and independent review to later corrections, targeted checks, and retained evidence without claiming a fresh full-suite run on final content?

Define correction scope, independent review inputs, affected-behavior check selection, when uncertainty or cross-cutting impact requires broader/full checks, lineage and invalidation, and how consumers decide whether publication has sufficient current evidence. Distinguish documentation-only corrections, qualifying bookkeeping deltas, clean-rebase carry with full check reruns, and remote-tip refresh without content changes.

Use the resolved review and classification contracts. Establish who records the check-selection rationale and how the independent reviewer can reject insufficient scope; do not silently weaken the initial full applicable suite gate.

## Comments

### Initial fact-finding — 2026-10-06

Read-only delegated inspection found that `verification.py` preserves the previous complete record through `previous_evidence`, but ordinary changed inputs clear active checks/reports. Check execution runs the full declared plan; requirements always include `make check`. There is no targeted-correction selection or full-suite-anchor schema yet.

Current correction policy requires each required role to attest again, allowing justified retention of unchanged-area inspection in report prose. Active outcome calculation does not traverse historical failures; reviewers currently account for their resolution semantically. Clean-rebase carry has distinct strict conditions and reruns checks. Remote-tip-only refresh preserves unchanged identity; publication consumes current PASS and checks the recorded remote tip without rerunning suites.

Pending human decisions: check-selection ownership and escalation, affected reviewer roles, cumulative correction lineage and prior-failure handling, and truthful publication sufficiency. Existing accepted full-suite, documentation/bookkeeping, clean-rebase, and remote-tip boundaries remain settled. No implementation changed.

### Human agreement and new integration constraint

The user agreed to all four recommendations:

1. The implementer proposes correction checks with affected-behavior rationale; an independent reviewer validates scope and can require broader checks. Cross-cutting or uncertain impact requires the full applicable suite; documentation-only corrections use relevant documentation checks.
2. Review affected responsibilities: code fixes always receive fresh behavioral inspection; Standards, Spec, and security return when affected. Retaining other reviews requires independently checked justification, not unchanged bytes alone. Documentation and proven bookkeeping retain their agreed rules.
3. Link corrections to their predecessor and last successful full-suite snapshot; assess cumulative changes since that suite. Missing history, unresolved failures, or uncertain combined impact prevents reuse and requires fresh evidence.
4. Publication consumes honestly labelled earlier full-suite evidence plus current correction checks and independent review, with content identities explicit. Never claim that a historical suite ran on final revised content. Clean rebases still rerun full applicable checks; remote-tip-only refresh does not.

The same reply forbids modifying or wrapping Matt Pocock skills. These four policy choices are agreed, but their integration remains blocked by the reopened [Bind independent review to exact proposed content](01-exact-content-review.md). Leave this ticket open until compatibility is settled; agreement does not authorize altered upstream reviewer orchestration.

## Answer

Resolved through the user's agreement to the four correction-evidence recommendations and subsequent acceptance of native committed review and both semantic axes. The reopened integration blocker is now resolved.

- Preserve the initial full applicable suite for each code-changing issue PR. For corrections, the implementer proposes checks with an affected-behavior rationale; an independent reviewer validates adequacy and can require broader checks. Cross-cutting or uncertain impact requires the full applicable suite. Documentation-only corrections receive relevant documentation checks.
- Code corrections always receive fresh behavioral inspection. When native semantic correction review is needed, run both Standards and Spec unchanged, as settled in [Bind independent review to exact proposed content](01-exact-content-review.md). Security returns when its responsibilities are affected. Retained review coverage requires independently checked justification; unchanged bytes alone are insufficient. Documentation and proven bookkeeping retain their agreed classifications.
- Link every correction to its predecessor and the last successful full-suite snapshot. Assess cumulative changes since that suite, not only the latest delta. Missing history, unresolved failures, or uncertain combined impact prevents reuse and requires fresh evidence; a new passing check cannot erase an unresolved finding.
- Publication consumes earlier full-suite evidence plus current correction checks and independent review, explicitly identifying the content each covered. Do not claim the full suite ran on final revised content when it did not. Reuse sufficient current evidence without another execution at shipping.
- Keep strict clean-rebase carry conditions and full applicable check reruns. Remote-tip refresh alone does not require reruns when tested content is unchanged. Proven bookkeeping retains evidence only under its validated eligibility conditions.

Separate harness tooling implements evidence handling without modifying or wrapping Matt's skills. This accepted design does not authorize implementation or relax current gates.
