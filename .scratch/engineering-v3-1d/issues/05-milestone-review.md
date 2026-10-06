# Define milestone review triggers and acceptance

Type: grilling
Status: resolved
Assignee: Codex session for zeke
Parent: [Engineering v3-1d decision map](../map.md)

## Question

How are broad architecture, maintainability, and security reviews triggered at explicit milestone close or release, scoped, recorded, and accepted while ticket delivery retains its own immediate review obligations?

Specify who explicitly declares the milestone/release and its scope, review inputs and independent roles, where findings and acceptance live using existing conventions, treatment of unresolved or explicitly accepted findings, changed scope after review, and the distinction between ticket delivery and milestone acceptance. Preserve immediate security review for applicable ticket changes; milestone review must not silently replace it.

## Comments

### Initial fact-finding

Read-only inspection found no existing milestone-specific acceptance schema. The local tracker supports specs, issues, comments, and breakdowns. The engineering-v3-1c breakdown provides a useful precedent: an audit identifies an exact origin/main commit, included spec slices, exclusions, merged tickets, and evidence gaps, explicitly distinguishing its audit from a fresh full verification run.

Current review policy supplies evidence-based findings, human-directed corrections, and separate implementation/verification/acceptance/publication states. Existing maintainability review covers architecture-related concerns, while security has its own reviewer. Native Matt code-review supplies committed-diff Standards/Spec review, not a whole-system acceptance audit; no separate architecture reviewer is defined.

Pending decisions: explicit trigger and pinned scope; broad review roles and evidence reuse; durable findings and human acceptance; post-review scope changes. Immediate ticket security review and the no-skill-wrapper boundary remain settled. No review or implementation was executed by this planning session.

### Human response: feature milestone planning

The user accepted Q2 (one fresh architecture/maintainability reviewer plus separate broad security review), Q3 (breakdown-based findings and explicit human acceptance), and Q4 (independent refresh for affected changes with justified evidence reuse).

For Q1, the user requested a skill used after Matt's `/to-tickets` that reads the feature scope, recommends milestone groupings, discusses them with the user, supports user-defined alterations, and tracks that feature. Design this as a separate skill, not a modification or wrapper around Matt's skills. Skill-creator guidance was consulted for scope and interaction design; no skill implementation was created during Wayfinder.

The user's security comment was acknowledged with the existing distinction: broad security review occurs at milestone close/release, while immediate targeted security review remains conditional on security-sensitive ticket changes. It is not an exemption from that settled requirement.

Pending: milestone grouping criteria and treatment of user changes; invocation after `/to-tickets`; authoritative tracking location and readiness/close interaction. Q1 and final shared understanding remain open.

## Answer

Resolved through the user's agreement to Q2–Q7, with Q1 replaced by a standalone feature-milestone skill and explicit support for recalibrating stale plans during implementation.

### Plan and track feature milestones

Provide a separate `/milestones` skill used after Matt's `/to-tickets`, without modifying, intercepting, or wrapping Matt's skills. Read the feature spec and existing tickets, recommend milestone groupings, explain the boundaries, and discuss them with the user before recording the agreed plan.

Group by demonstrable feature outcomes or coherent integration points, respecting ticket dependencies rather than fixed ticket counts. The user may split, combine, rename, or move milestones. Surface dependency conflicts for discussion instead of silently rewriting tickets.

Keep a milestone section in the feature's existing breakdown, linking original tickets instead of copying their contents. Each milestone records its outcome, included tickets, completion conditions, and review/acceptance state. This is the feature-level tracking view; implementation, verification, publication, merge, and human acceptance remain distinct.

### Recalibrate during implementation

Revisit `/milestones` as implementation exposes changed assumptions, dependencies, or stale tickets. Compare the agreed plan with actual implementation and available review/delivery evidence; identify discrepancies and recommend updated groupings, ticket scope/dependencies, or completion conditions. Discuss substantive changes with the user, then update the agreed milestone plan and affected tracker content together, preserving the reason for the change and evidence gaps.

Implementation is evidence of what exists, not automatic approval to change requirements. Preserve settled decisions unless the user revises them. Material scope changes follow the existing specification/ticket workflow; do not replace it with custom orchestration. Recalibration is substantive planning, not the mechanical `/ssync` exemption. Do not infer acceptance from merged tickets or rewrite history to imply missing evidence existed.

### Trigger, review, and acceptance

On explicit invocation, the skill identifies milestones ready for review and recommends closure. The user's explicit instruction starts broad milestone/release review. Record included specs/tickets, exclusions, comparison baseline, and exact candidate commit for that review; the user decides acceptance.

One fresh reviewer covers architecture and maintainability together; a separate fresh reviewer covers broad security. They inspect combined changes and relevant system interactions using existing ticket evidence, requesting additional checks where evidence has gaps instead of automatically repeating all suites. Immediate targeted security review still applies to security-sensitive ticket changes. These are separate harness reviews, not skill wrappers.

Append the review outcome to the existing breakdown with detailed report links, scope, evidence gaps, findings, and the user's acceptance decision. Blocking findings need fixes or explicit human acceptance of the specific risk and rationale. Preference-only suggestions remain non-blocking. Risk acceptance does not turn failed checks or missing required evidence into a pass. Milestone acceptance does not authorize publication or merge.

After changes, independently review affected content and conclusions. Broaden review for material changes to scope, architecture, security boundaries, or cumulative impact. Retain justified unaffected evidence and bind final acceptance to the updated candidate.

This is an accepted design for later specification and implementation. The skill was not created or executed during this decision session; current operational gates remain unchanged.
