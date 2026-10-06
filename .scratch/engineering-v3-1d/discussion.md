# Engineering v3-1d design discussion

Source: [intent](intent.md). Status: shared understanding confirmed by the user on 2026-10-05; ready for planning. Implementation is not authorized by this discussion. The consolidated decisions below supersede tentative choices in the round history.

## Latest constraint — supersedes adapter permission

The user subsequently ruled out modifying Matt Pocock skills or building wrappers on top of them. Earlier permission to specialize their orchestration through adapters is superseded. The replacement is now agreed: ordinary scoped checkpoint commits before unchanged native review, separate harness check/evidence/publication tools, and both native semantic axes whenever correction review is required. The four correction-evidence choices stand with that semantic-axis amendment. Other settled decisions remain in force.

## Settled direction

- Include semantic-review simplification, mechanical bookkeeping, duplicate-check removal and harness optimization, formatting scope, milestone review, evidence reuse, model-routed shipping, `/ssync`, and research conventions. Omit the proposed performance instrumentation/diagnostics and measurement work for now: no new timing, progress, slow-test reporting, benchmark report, or token telemetry requirement. The user's subsequent [compatibility decision](issues/09-migration-and-compatibility.md) removes the earlier Graphify migration preservation requirement; it does not mandate deletion during planning.
- Replace the relevant ADR 0002 obligations with the proposed ADR 0003 design: Matt's Standards and Spec reviewers, a distinct focused behavioral reviewer, and separate security review where applicable. Remove overlapping harness maintainability review and repeated authoritative checks. Broad architecture/maintainability/security assessments occur at explicit milestone close or release.
- Retain an initial full applicable suite for each code-changing issue PR, launched once through recorded harness execution. Later corrections receive independent review and checks specific to the fix and affected behavior; documentation-only fixes receive documentation checks. Cross-cutting or uncertain correction impact requires broader checks, including the full suite. Retained earlier results are not represented as a fresh full-suite run on final content.
- Substantive documentation receives one lightweight review and relevant checks; mechanically proven bookkeeping receives neither model review nor application tests. Mixed or ambiguous changes retain stricter substantive requirements. Qualifying bookkeeping-only deltas preserve code evidence. Clean rebases retain reviews only under existing carry conditions and rerun full applicable checks; remote-tip refresh alone does not.
- Use existing narrow status/link/evidence fields for `/ssync`; no new marked block or general tracker parser. Preserve surrounding prose, evidence caveats, and acceptance checkboxes. Skip ambiguous layouts. Explicit invocation authorizes one bookkeeping PR's creation/update, not merge; each status requires its own evidence and synchronization must be idempotent.
- Split formatting into application `fmt`, harness `engineering-fmt`, and explicit `fmt-all`; project-owned tooling formats explicitly selected intended files without wrapping upstream skills, as settled in [formatting and check optimization](issues/08-formatting-and-check-optimization.md). Keep research beside its spec with sources, findings, uncertainties, and decision implications.
- Reduce elapsed time, model tokens, and manual interventions through the agreed structural changes without adding a measurement workflow or promising a numeric improvement.
- Share policy and deterministic tooling between Claude Code and Codex, using thin runtime adapters and an explicit fallback when a preferred model is unavailable.

## Round 2 decisions

- Preferred semantic-review design: reuse Matt's Standards and Spec reviewers as the primary review; the harness must not repeat their work through additional overlapping reviews. Preserve the two findings axes. Exact integration remains open.
- Substantive documentation receives one lightweight independent review and relevant documentation checks, without the application suite. Mechanically validated status/link updates receive no model review. Policy, executable examples, and acceptance-criteria changes are not mechanical bookkeeping.
- Separate immediate security review covers changes affecting authentication, permissions, secrets, untrusted input, dependency execution, destructive operations, or verification/publication enforcement. Deterministically established non-behavioral comments may be exempt; agent-interpreted instructions are not inert comments. Ambiguity retains security review.
- Broader architecture, maintainability, and security review runs at explicit milestone close or release. Findings block milestone acceptance until resolved or explicitly accepted; ticket delivery follows its own review rules.
- Initially `/ssync` runs only on explicit invocation, authorizing observation, narrow bookkeeping changes, and creation/update of one bookkeeping PR, but not merge. Automatic invocation is deferred until idempotence is demonstrated.
- Test cadence was reopened here and refined in round 3 below.

## Round 3 decisions

- Working preference is option A: full applicable suites for every issue PR that changes code, removing duplicate execution and optimizing measured bottlenecks instead of moving integration assurance to milestones. The user is leaning toward A; quantify savings rather than promise a runtime reduction. Documentation and mechanical-bookkeeping exemptions remain as agreed.
- Runtime adapters may explicitly specialize upstream orchestration while keeping pinned skills unchanged: define check scope, present the complete proposed content to Matt's reviewers, and record their results once.
- A mechanically validated bookkeeping-only delta retains prior code-review and test evidence without new reviewers or code tests. It must not change logic, requirements, policy, or relevant verification inputs.
- `/ssync` records stages independently from authoritative evidence. Observed merge does not imply verification or human acceptance; missing evidence remains unknown. It never rewrites acceptance criteria.

## Round 4 decisions

- The implementer may launch the authoritative recorded checks once, with later review/shipping reusing valid evidence. The user remains concerned about eliminating behavioral inspection because harness review has caught bugs after Matt's review. Test execution ownership and independent behavioral judgment are distinct decisions; removal of that judgment is REOPENED pending investigation.
- A qualifying clean rebase may retain semantic reviews under existing carry conditions, but full applicable checks rerun on the new combined content. Refreshing the recorded remote tip without changing tested content does not require a rerun.
- Formatting defaults: `make fmt` covers application source/tests, `make engineering-fmt` covers harness source/tests, and `make fmt-all` covers both. The implementation adapter formats intended changed files; non-mutating checks cover the required scope.
- `/ssync` initially edits explicit status, delivery-link, and evidence fields only. It does not toggle acceptance-criteria checkboxes. Unknown layouts produce a skipped-item report rather than guessed edits.
- Shipping-model routing is configurable per runtime, with a clearly reported fallback to the current session if unavailable. Concrete defaults require runtime-support verification.
- Research notes live beside the spec and record the question, dated sources, findings, uncertainties, and decision implications. Link them from the spec; promote lasting terms and architectural decisions into the glossary and ADRs.

## Round 5 decision

- Retain Matt's Standards and Spec reviewers plus a separate fresh behavioral reviewer. Remove the overlapping harness maintainability review. The behavioral pass consumes existing authoritative suite evidence and probes changed behavior, failure paths, configuration interactions, and nearby regressions; it does not repeat the full suite or Standards review. This settles the concern reopened in round 4 and replaces the earlier single-pass goal with no duplicated review responsibilities. Separate targeted security review remains required when applicable.

## Round 6 feedback

- Correction cadence is REOPENED: the user prefers specific independent review of the fix and affected behavior rather than automatically regenerating full-suite evidence; documentation-only fixes especially should not trigger code suites. Exact check-selection and escalation rules remain to settle. This refines the per-issue full-suite preference; it does not remove that initial gate.
- Ambiguous or mixed changes follow the stricter substantive requirements. Markdown alone never proves eligibility for the bookkeeping exemption.
- A new marked bookkeeping block is NOT accepted. Explain its benefit and inspect existing formats before introducing another convention. The no-general-tracker-parser boundary remains.
- Broad before/after flow measurement and token telemetry are NOT accepted. The user questions token overhead, storage location, and actionability. Prefer a minimal proposal separating deterministic diagnostic data from agent-generated reporting.

## Facts established by source inspection

- Upstream implementation invokes committed-diff review before its final commit; an integration must cover the actual proposed content without modifying pinned upstream skills.
- Ordinary verification already permits one fresh session to submit two role reports. Reducing sessions alone does not necessarily simplify the review contract.
- Every plan currently requires `make check`; `.scratch/` bookkeeping is ordinary by default. It does not inherently require the full engineering suite.
- Root formatting includes engineering source and autofixes; `FORMAT_PATHS` already supports an explicit override.
- Remote-base movement alone does not invalidate snapshot identity; publication still requires the recorded remote tip to be refreshed.
- Behavioral inspection has demonstrated value beyond passing suites: local `migration-closure-behavioral-report.json` records a retained closed migration incorrectly reported as pending after 312 tests passed; `issue-04-behavioral-report.json` records `push.followTags` publishing an unrelated tag after 262 tests passed. Both are under `.engineering/state/verification/`. The records do not establish whether Matt's review preceded these findings or would have missed them. Reproductions had documented limits (fixture-faked migration gates and isolated Git transport reproduction respectively).
- The current verifier explicitly exercises changed behavior and nearby regressions; Matt's Spec prompt inspects the diff against requirements without an explicit behavioral-exercise obligation. Round 5 preserves that distinct inspection.

## Final round decisions

- Q22 revised accepted: targeted independent correction review and relevant checks, with broader verification when impact is cross-cutting or uncertain.
- Q24 revised accepted: narrowly recognized existing fields, preserving other content and skipping ambiguity.
- Q25 diagnostics proposal omitted for now, including its reduced version.

## Handoff boundaries

The latest answers in the [decision map](map.md) refine and, where explicitly stated, supersede earlier round history. Native review uses ordinary scoped checkpoint commits and unchanged upstream skills; no adapter intercepts their workflow. Classification, correction-evidence lineage, existing-field synchronization, milestones, formatting, and compatibility now have resolved contracts for specification. [Shipping routing](issues/07-shipping-routing.md) selects configurable defaults and reported current-session fallback using the dated research; account availability remains untested. The user confirmed the [coherent specification handoff](issues/10-specification-handoff.md) on 2026-10-07; the map is complete and ready for `/to-spec` followed by `/to-tickets`.

The prepared `/pr` description handoff was implemented and published separately in PR #46, as recorded in the shipping ticket; merge is not established by this discussion. Future specification must account for that work rather than assume it needs rebuilding. Other accepted target-design contracts remain pending implementation.

ADR 0002 remains current policy until the replacement is agreed and implemented. The proposed ADR records the replacement trade-offs; the glossary records resolved terms. No implementation, commit, or publication has been performed by this interview.
