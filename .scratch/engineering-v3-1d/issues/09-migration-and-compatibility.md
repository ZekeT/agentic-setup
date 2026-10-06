# Preserve compatibility while evolving review evidence and distribution

Type: grilling
Status: resolved
Assignee: Codex session for zeke
Blocked by: 01, 02, 03, 04, 05, 07, 08
Parent: [Engineering v3-1d decision map](../map.md)

## Question

How should existing installations and in-flight work transition to the accepted review, evidence, formatting, and publication contracts without silently upgrading old proof or overwriting consumer-owned configuration?

Decide handling of existing evidence and saved publication plans, schema/version boundaries and unsupported readers, previewed consumer updates and local conflicts, and compatibility coverage for the retained Graphify migration route. Account for the separately published prepared-PR-body handoff without assuming it is merged or that all consumers have the new upstream skills. Keep Matt's skills unchanged and unwrapped; adoption of the installed evaluation-only `implement-spec` workflow is not implicit.

## Comments

Graduated from the migration and compatibility fog after the formatting and check-optimization decision resolved. Inspect current contracts before proposing transition choices. No migration strategy has yet been accepted through this ticket.

### Transition fact-finding

Current verification rejects unsupported record schemas for active use; prepare retains prior records as history and only considers reuse within its supported schema and identity rules. Publication authorization is bound to the presented plan; revised PR bodies require a revised plan without automatically repeating unchanged code checks. Consumer updates preserve project-owned configuration and local-only managed edits, but conflicting local/upstream managed edits block apply before writes. The legacy migration explicitly preserves `/graphify-out/` outside the new managed ignore region, with a regression test; this is not evidence that Graphify is a supported current navigation runtime.

Pending human choices: the evidence transition boundary, saved publication recovery, consumer update compatibility, and the retained legacy migration scope. Inspection only; no migration or implementation performed.

## Answer

The user agreed to Q1–Q3 and changed Q4: Graphify compatibility does not need to be preserved.

- Preserve old verification evidence as history and obtain fresh proof under the new review contract. Do not convert old maintainability reports into Standards and Spec reports. Unsupported schemas stop with clear recovery instructions rather than being interpreted as current proof.
- Preserve interrupted publication history and reconcile completed remote actions before retrying. Unchanged compatible plans retain retry authorization; changed plans require renewed presentation and applicable authorization. A PR-body-only change does not itself require rerunning unchanged code checks. Incompatible old evidence still follows the transition rule above.
- Use the existing preview-and-apply consumer update mechanism. Show configuration migrations explicitly, preserve project-owned settings and check recipes, and block conflicting managed-file edits. Keep upstream skill installation separate; harness updates do not implicitly adopt `/implement-spec`.
- Remove Graphify migration compatibility as a requirement of this effort. This supersedes its preservation requirement in the discussion and map. No dedicated Graphify compatibility work is required; this decision does not mandate removal or authorize deleting existing code during planning. Ordinary consumer ownership and conflict protections remain applicable.

These are accepted target-design decisions, not implementation or operational-policy changes.
