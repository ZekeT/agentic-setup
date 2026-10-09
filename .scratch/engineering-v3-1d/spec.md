# Engineering v3-1d: focused assurance and feature tracking

Status: ready-for-agent
Source: [Completed decision map](map.md)
Testing boundaries confirmed by the user: 2026-10-07.

## Problem Statement

Developers using Agentic Starter repeat checks and overlapping reviews when the underlying evidence remains valid. Small documentation corrections and tracker updates can trigger assurance work intended for code changes, while later corrections lack an explicit way to retain earlier coverage honestly. Broad feature-level assessment and ticket-by-ticket delivery are not clearly connected, and plans can become stale as implementation reveals new information.

The developer needs less repeated work without losing independent behavioral judgment, targeted security review, trustworthy evidence, or human control. They also need a feature-level planning and recalibration view, reliable tracker synchronization, bounded formatting, and inexpensive configurable shipping execution. These improvements must coexist with native Matt Pocock skills, without modifying or wrapping them.

## Solution

Use Matt's native Standards and Spec review as semantic evidence, supplemented by a separate behavioral review and security review when applicable. Run the initial full applicable suite once per code-changing issue PR, then use independently validated correction checks and explicit evidence lineage. Distinguish substantive documentation from mechanically proven bookkeeping and retain strict treatment of mixed or uncertain changes.

Provide explicit `/ssync` for narrow tracker synchronization and standalone `/milestones` for discussing feature outcomes, recalibrating plans, and initiating broad closure reviews. Separate application and harness formatting, remove proven duplicate checks, and route shipping through configurable runtime agents with a reported fallback. Preserve the existing prepared `/pr` description handoff, authorization gates, retry recovery, and consumer ownership protections.

This specifies the remaining target design. The merged skill update and `/pr` → `/ship` description handoff are baseline capabilities, not work to rebuild. Current operational policy remains in force until its replacements are implemented and verified.

## User Stories

1. As a developer, I want to use Matt's skills unchanged, so that upstream improvements remain usable without maintaining a fork or wrapper.
2. As a developer, I want ordinary scoped checkpoint commits before native review, so that the committed diff contains every proposed change.
3. As a reviewer, I want results bound to the reviewed commit and content, so that later unreviewed edits cannot inherit approval.
4. As a developer, I want Standards and Spec findings recorded separately, so that semantic responsibilities stay visible without a duplicate harness maintainability pass.
5. As a developer, I want fresh behavioral inspection beyond passing tests, so that changed behavior and nearby failures receive independent attention.
6. As a developer, I want targeted security review for security-sensitive changes, so that sensitive boundaries receive scrutiny when affected.
7. As a reviewer, I want isolated disposable probes, so that experiments cannot mutate the proposal or another reviewer's inputs.
8. As a developer, I want an explicit INCOMPLETE handoff when independent review is unavailable, so that self-review cannot masquerade as independent proof.
9. As a developer, I want one recorded initial full applicable suite for each code-changing issue PR, so that reviewers and shipping can reuse its results.
10. As an implementer, I want to propose correction checks with an affected-behavior rationale, so that bounded fixes do not automatically repeat unrelated checks.
11. As an independent reviewer, I want to reject insufficient correction checks, so that uncertain or cross-cutting changes receive broader verification.
12. As a reviewer, I want cumulative correction history since the last full suite, so that several small fixes cannot conceal a broad untested change.
13. As a developer, I want historical and current coverage labelled accurately, so that a prior suite is not presented as a run on final revised content.
14. As a developer, I want unresolved failures and missing history to prevent evidence reuse, so that a later passing check cannot hide a previous blocker.
15. As a developer, I want clean rebases and remote-tip refreshes treated distinctly, so that only changes requiring renewed checks trigger them.
16. As a documentation author, I want prose-only changes to receive lightweight review and relevant checks, so that application tests are not run without a behavioral reason.
17. As a reviewer, I want policy, instructions, requirements, and executable examples assessed by their impact, so that Markdown does not become an assurance loophole.
18. As a developer, I want mechanically proven bookkeeping exempt from model review and application tests, so that status updates do not repeat code assurance.
19. As a developer, I want ambiguous and mixed changes treated conservatively, so that exemptions require proof rather than a title or assertion.
20. As a developer, I want comment exemptions limited to proven inert syntax, so that directives and agent instructions retain appropriate scrutiny.
21. As a developer, I want `/ssync` to operate on one explicit effort, so that unrelated work and Wayfinder decisions remain untouched.
22. As a developer, I want tracker stages derived from evidence for each stage, so that merge cannot silently imply verification or acceptance.
23. As a developer, I want synchronization to preserve prose, caveats, and acceptance checkboxes, so that historical limitations remain visible.
24. As a developer, I want unsupported or ambiguous tracker layouts skipped with an explanation, so that automation does not guess at intent.
25. As a developer, I want repeated synchronization to reuse one PR or do nothing, so that retries do not create duplicate commits or PRs.
26. As a developer, I want concurrent edits and uncertain remote responses reconciled, so that synchronization cannot overwrite work or publish twice.
27. As a feature owner, I want `/milestones` to recommend outcome-based groups after `/to-tickets`, so that feature progress has meaningful completion points.
28. As a feature owner, I want to split, combine, rename, and move milestone groups through discussion, so that the plan reflects my priorities and dependencies.
29. As a feature owner, I want milestone tracking to link existing tickets, so that there is one authoritative copy of ticket requirements.
30. As a developer, I want to revisit milestones when implementation reveals stale assumptions, so that the plan and tickets can be recalibrated with the user.
31. As a feature owner, I want explicit control over closure review, so that readiness does not automatically trigger acceptance or publication.
32. As a feature owner, I want broad architecture/maintainability and security assessment at milestone close, so that integrated behavior receives review beyond individual tickets.
33. As a feature owner, I want acceptance tied to the reviewed candidate and explicit findings, so that later changes cannot silently inherit it.
34. As a developer, I want application, harness, and combined formatting scopes, so that routine formatting touches only intended files.
35. As a maintainer, I want proven duplicate checks removed while independent commands remain useful, so that efficiency does not weaken required coverage.
36. As a maintainer, I want immutable fixture preparation reused with isolated writable state, so that optimization cannot introduce cross-test contamination.
37. As a developer, I want configurable shipping model and effort settings per runtime, so that publication can use an appropriate execution cost.
38. As a developer, I want a reported current-session fallback when the preferred shipper cannot run, so that authorized publication can continue without hiding uncertainty.
39. As a developer, I want shipping to consume accepted scope and existing proof only, so that it cannot introduce fixes, repeat valid suites, or infer merge authority.
40. As a developer, I want my prepared PR description published unchanged, so that shipping does not replace it with another generated description.
41. As a consumer project owner, I want explicit schema transition and fresh proof under the new contract, so that old records are not silently relabelled as new assurance.
42. As a consumer project owner, I want previewed updates that preserve project configuration and stop on conflicts, so that upgrades cannot overwrite local decisions.
43. As a developer, I want interrupted publication history retained across upgrades, so that completed remote actions are reconciled before retrying.
44. As a developer, I want skill installation distinct from workflow adoption, so that installing `/implement-spec` does not switch me to its workflow.

## Implementation Decisions

### Native review and assurance responsibilities

- Keep pinned Matt skills unchanged. Do not copy their orchestration, intercept invocation, change diff discovery, select individual native semantic axes through a wrapper, or create synthetic review commits.
- Format intended content and make ordinary scoped checkpoint commits before native committed-diff review. Include proposed additions, deletions, and mode changes. Native review does not cover subsequent uncommitted edits. Commits remain separate from verification, human acceptance, and publication authorization.
- Separate harness tools execute and record checks, store evidence, and enforce publication eligibility. Bind semantic evidence to the native reviewed commit, comparison context, and exact content identity; reject uncovered later changes. Preserve existing plan, tool, dependency, and explicit-input freshness safeguards.
- Replace overlapping ticket-level harness maintainability review with native Standards and Spec evidence. Keep the axes distinct. Whenever native semantic correction review is required, accept both axes unchanged rather than adding selective orchestration.
- Preserve a separate fresh behavioral reviewer who examines changed behavior, failure paths, configuration interactions, and nearby regressions using recorded check evidence. This role does not repeat the semantic review or automatically rerun the full suite.
- Require separate targeted security review when security-sensitive responsibilities are affected, including permissions, secrets, untrusted input, dependency execution, destructive behavior, and evidence/publication enforcement. Broad milestone security review does not replace it.
- Provide independent reviewers with requirement and content pointers plus factual check evidence, not implementation-session reasoning. Keep captured source immutable; run mutating probes in disposable copies and record their identity and limitations. Serialize evidence writes. Missing independent review remains INCOMPLETE, with a fresh-session handoff.
- Permit parallel scheduling only where native workflow and runtime controls allow it. Shared policy and deterministic tooling remain portable; runtime-specific controls do not redefine the native skill workflow.

### Classification and exemptions

- Classify actual changed content together with configured document locations and existing ownership/risk constraints. A path, title, or model assertion alone cannot prove an exemption. Mixed or uncertain changes retain stricter substantive requirements.
- Mechanical bookkeeping must account deterministically for every changed byte. Permit only uniquely recognized existing status, delivery-link, or supported evidence-pointer values backed by evidence for the asserted stage. Preserve all other bytes, including chronology, prose, caveats, and acceptance checkboxes. Treat modes and other content-identity changes conservatively rather than ignoring them.
- Qualifying bookkeeping receives deterministic validation without model review or application tests. Retain code evidence only when eligibility and verification-input relationships justify it; a bookkeeping edit to a verification input does not automatically retain proof.
- Prose-only documentation changes receive one lightweight independent review and relevant documentation checks, without an unrelated application suite. Changed policy, agent instructions, requirements, and executable examples receive review and checks appropriate to their impact. An unchanged example elsewhere does not disqualify a prose correction.
- Support comment-only exemptions only where syntax-aware validation proves executable structure unchanged and excludes meaningful directives. Docstrings, tool directives, generated-file markers, and agent-consumed instructions are not inert comments. Unsupported syntax and uncertainty retain stricter treatment. This exemption is distinct from mechanical bookkeeping.

### Recorded checks and correction lineage

- Preserve the initial full applicable suite for every code-changing issue PR, executed once through recorded harness execution by the implementer and consumed by independent reviewers. Applicability continues to respect installation role, ownership, configuration, and affected behavior; application and engineering suites are not interchangeable.
- For a correction, the implementer proposes checks and an affected-behavior rationale. An independent reviewer validates adequacy and can require broader checks. Cross-cutting or uncertain individual or cumulative impact requires the full applicable suite. Documentation-only corrections follow the documentation rules.
- Code corrections always receive fresh behavioral inspection. Native semantic correction review uses both axes when required; security returns when its responsibilities are affected. Retaining other coverage requires an independently checked explanation of why it remains applicable, not unchanged bytes alone.
- Extend evidence to identify each correction's predecessor, last successful full-suite snapshot, current content, executed checks, independent scope assessment, retained coverage, and outstanding findings. Evaluate cumulative changes since the full-suite anchor. Missing or untrustworthy history, unresolved failures, or uncertain combined impact prevents reuse and requires fresh evidence.
- Publication may consume an earlier full suite together with sufficient current correction checks and review, explicitly identifying the content each result covers. Do not report historical coverage as a fresh full-suite run on final content. Human risk acceptance cannot convert failed checks or missing required proof into PASS.
- Preserve existing strict clean-rebase carry conditions: unchanged own patches, plans, tools, and checks, with no disqualifying upstream overlap, may carry reviews but require full applicable checks on the rebased content. A remote-tip refresh alone does not rerun checks when tested identity is unchanged. Content-preserving commits retain proof under existing safeguards.

### Explicit tracker synchronization

- `/ssync` is a standalone harness operation for one selected effort's implementation tickets and breakdown. Ask if the effort is not identifiable. Exclude Wayfinder decision statuses and synchronization PRs themselves.
- Initially support existing implementation-ticket bold Status fields, uniquely identified breakdown status cells, and existing PR-link fields. Change only supported value spans. Skip aggregate rows, duplicate fields, ambiguous ticket/PR identities, and unknown layouts, reporting the reason. Do not introduce a general tracker parser or marked bookkeeping block.
- Narrative evidence sections are not writable machine fields. Preserve them and report evidence gaps. The broader bookkeeping category does not imply that `/ssync` can rewrite every evidence pointer or narrative layout.
- Distinguish implementation, verification, human acceptance, publication, and observed merge. Evidence for one stage does not establish another; unknown or conflicting evidence must not produce an unsupported assertion.
- Use a dedicated synchronization branch per effort and target branch, with one reusable open bookkeeping PR. Add commits only for actual supported content changes. An unchanged invocation creates neither commit nor PR. After merge, start a new cycle only for new discrepancies. One explicit invocation authorizes at most one PR creation/update, not merge or future automatic runs.
- Isolate synchronization from unrelated work and recheck source files and remote state before writing. Stop on conflicts; never overwrite user changes or force-push. Reconcile uncertain push/create outcomes before retrying. Extend the existing exact-head publication recovery contract deliberately to support updates to the same synchronization PR; do not treat its current lookup behavior as already sufficient.

### Feature milestones and recalibration

- Provide standalone `/milestones` after native `/to-tickets`. Read the existing spec and tickets, recommend groupings by demonstrable feature outcome or coherent integration point, explain dependencies, and discuss alternatives before recording the user's plan. Do not group by fixed ticket counts.
- The user may split, combine, rename, or move groups. Surface dependency conflicts rather than silently editing requirements. Store a milestone section in the existing feature breakdown with outcomes, original ticket links, completion conditions, and review/acceptance state; do not duplicate ticket bodies.
- On subsequent invocation, compare the plan with implementation and available evidence to identify stale assumptions, scope, dependencies, and completion conditions. Discuss substantive changes, then update agreed milestone and affected tracker content together with reasons and evidence gaps. Implementation shows what exists; it does not approve changed requirements. Material scope changes use the existing specification/ticket workflow.
- Recalibration is substantive planning, not a bookkeeping exemption. Never infer human acceptance from merged tickets or backfill missing historical verification as though it occurred.
- The skill identifies readiness and recommends closure, but explicit user instruction starts broad milestone/release review. Pin included specs/tickets, exclusions, comparison baseline, and exact candidate commit. One fresh reviewer covers architecture and maintainability together; a separate fresh reviewer covers broad security.
- Review combined changes and relevant system interactions using existing ticket evidence. Request additional checks for gaps instead of automatically repeating all suites. Record detailed report links, scope, gaps, findings, and explicit human acceptance in the existing breakdown.
- Blocking findings require fixes or explicit acceptance of the specific risk and rationale; preference-only suggestions do not block. Risk acceptance does not bypass failed checks or missing required proof. Milestone acceptance grants neither publication nor merge authority.
- After changes, independently refresh affected content and conclusions. Broaden for material scope, architecture, security-boundary, or cumulative changes; justify retained unaffected evidence and bind acceptance to the final candidate.

### Formatting and bounded optimization

- Separate application `fmt`, harness `engineering-fmt`, and explicit combined `fmt-all`. Routine formatting takes an explicit intended-file selection before checkpoint commits and review. Empty selection does nothing; unsupported paths produce a clear error rather than expanding scope. Use project-owned tooling, without upstream wrappers.
- Formatting is preparation, not proof of successful lint or review. Required verification remains non-mutating with respect to source content.
- Remove proven duplicate execution from starter-owned recipes while keeping individual commands useful independently. In particular, overlapping harness health checks must have explicit coverage evidence before a requirement is treated as satisfied. Do not assume arbitrary consumer-owned check recipes contain those checks or rewrite them silently.
- Reuse immutable fixture preparation only with fresh writable copies. Preserve per-test Git history, publication state, failure cases, and initial full-suite obligations. Do not delete distinct application or engineering coverage as a supposed duplication.

### Shipping and runtime routing

- Preserve the merged native `/pr` description handoff: capture prepared Markdown, bind it to the presented publication plan, and publish the exact body. A revised body requires a revised presentation and applicable authorization but does not itself rerun unchanged code checks. Keep the existing manual GitHub template; do not add a second body generator.
- Configure dedicated shipping agents independently of other agents. Accepted starting defaults are `gpt-6.1-sol` with low reasoning for Codex and `sonnet` with low effort for Claude Code. These are configurable design choices, not proof of account access, exact backend execution, or cost savings.
- Dispatch through actual supported runtime controls. Report requested settings and the actual model when observable; otherwise state uncertainty. Respect runtime restrictions and substitutions rather than claiming a prose instruction changed the model.
- If the preferred agent cannot run, report why and continue in the current session within existing authorization. Ensure any prior publisher has stopped, reconcile completed Git/provider actions, and serialize publication. Changing models cannot bypass a failed gate.
- Hand off pointers to accepted scope, branch, current evidence, target, authorization, and prepared publication plan rather than the implementation conversation. The shipper validates those inputs and returns the actual PR/MR URL or precise partial progress and recovery instructions. It does not fix application code, reinterpret acceptance, repeat valid suites, or merge.

### Transition and consumer distribution

- Introduce an explicit versioned evidence transition for the changed review responsibilities and lineage contract. Preserve old records as history and obtain fresh proof under the new contract. Do not relabel old maintainability reports as Standards/Spec evidence. Unsupported schemas fail with clear recovery instructions rather than guessing.
- Preserve interrupted publication history and reconcile remote actions before retrying. Unchanged compatible plans retain authorization; changed plans require renewed presentation and applicable authorization. Incompatible verification still needs the new proof contract even when publication history remains useful.
- Distribute changes through existing preview-and-apply consumer updates. Show configuration migrations explicitly, preserve project-owned values and check recipes, and stop on conflicting managed edits. Keep dependency installation separate from harness updates; the installed evaluation-only `/implement-spec` does not become the default workflow.
- Graphify migration preservation is no longer a requirement. This does not mandate deleting unrelated legacy handling or weaken ordinary ownership/conflict protections.

## Testing Decisions

The user confirmed these boundaries on 2026-10-07. Prefer existing public seams and observable behavior over internal function structure. Tests should establish both the intended result and the refusal/preservation behavior when inputs are stale, ambiguous, conflicting, or unauthorized.

- **Primary boundary: public harness commands in disposable repositories.** Extend the existing CLI verification, review-tier, publication, recovery, provider, and linked-workspace test patterns. Use real local Git and isolated files, with fake hosting responses at the external boundary. Assert exit status, reported classification and coverage, recorded identities, resulting bytes, commit/PR counts, and untouched unrelated content.
- **Consumer boundary: installation and update journeys.** Extend existing generation, adoption, update, and greenfield journeys. Exercise old and unsupported schemas, historical record preservation, fresh-proof requirements, explicit configuration migrations, local-only edits, overlapping conflicts, both installation roles, and unchanged consumer check recipes. Required checks must be proved through their observable execution, not an internal mock that bypasses the contract being tested.
- **Human/runtime boundary: skill and routing interaction scenarios.** Use the existing eval approach for milestone proposals, user alterations, stale-ticket recalibration, explicit closure/acceptance, model selection failure, fallback reporting, and serialized publisher recovery. Fake runtime responses can prove dispatch and fallback contracts; static instruction checks cannot prove real model behavior or account entitlement. Keep optional model-backed runs and untested availability clearly labelled.
- **Review and evidence cases:** include uncovered uncommitted edits, stale commit/content identities, missing independent roles, isolated probe mutations, initial full-suite execution once, validated correction selection, cumulative broadening, unresolved earlier failures, missing anchors, justified retained coverage, clean rebases with reruns, and unchanged remote-tip refresh without reruns. Assert historical results remain historical.
- **Classification and synchronization cases:** cover prose-only edits beside unchanged examples; changed executable instructions; inert comments versus directives/docstrings; every-byte bookkeeping validation; acceptance-checkbox/prose preservation; unsupported layouts; duplicate/aggregate fields; merged-but-unverified tickets; no-op repeat; same-PR update; post-merge new cycle; conflicting edits; uncertain push/create outcomes; and exclusion of Wayfinder and synchronization statuses.
- **Milestone cases:** cover outcome-based grouping, dependency conflict discussion, user-requested regrouping, shared original ticket references, stale requirements, missing historical proof, readiness without automatic closure, broad role separation, specific risk acceptance without invented PASS, and changed candidate scope invalidating acceptance.
- **Formatting and optimization cases:** verify explicit file boundaries, empty and unsupported selections, source-preserving check execution, independent standalone commands, no unproven consumer check deduplication, and no writable fixture leakage. Preserve all applicable existing suites; reuse immutable preparation without reducing scenario coverage.
- **Shipping regression cases:** preserve exact prepared-body delivery, plan-bound authorization, hooks, base freshness, provider lookup, uncertain retries, and no force-push/merge. Verify model fallback does not grant authority, change accepted scope, or run concurrent publishers.
- No new performance measurement framework is required. A passing test must establish behavior or a meaningful boundary, not merely mirror an implementation or prove that an instruction contains a keyword.

## Out of Scope

- Modifying, wrapping, replacing, or copying Matt's skill orchestration; custom native-review diff discovery and synthetic review commits.
- Adopting the installed `/implement-spec` parallel integration workflow or changing the per-ticket implementation workflow implicitly.
- Automatic `/ssync`, a general tracker parser, a new marked bookkeeping block, or translation/dual-writing between tracker ecosystems.
- Eliminating independent behavioral review, treating milestone review as a replacement for applicable ticket security review, or removing the initial full applicable suite for code-changing issue PRs.
- New timing/progress diagnostics, slow-test reports, benchmarking systems, token telemetry, or numeric savings guarantees.
- Rebuilding the merged skill update or prepared PR-body handoff, removing the manual GitHub PR template, or treating this spec as a new publication workflow.
- Graphify runtime support, graph-format conversion, or a requirement to preserve Graphify migration compatibility. Unrelated legacy deletion is not required.
- Automatic acceptance, publication, merge, force-push, or unrelated repository changes.

## Further Notes

- Baseline: merged PRs [#46](https://github.com/ZekeT/agentic-starter/pull/46) and [#47](https://github.com/ZekeT/agentic-starter/pull/47), observed at main commit `c7e1e51a365ae0a17fe32db47e6a611f9fc31e81`. Their verification proves that delivered scope, not the unimplemented contracts in this spec.
- The [decision map](map.md) and latest Answer sections are the authoritative planning inputs. The [discussion](discussion.md) supplies context; earlier round alternatives and the [intent](intent.md) do not override later decisions. [ADR 0003](../../docs/adr/0003-reuse-upstream-review-and-exempt-bookkeeping.md) records the target rationale, while ADR 0002 remains operational until replacement implementation.
- [Runtime research](research/runtime-shipping-models.md) is dated evidence with explicit limitations. Its original capture/worktree descriptions are historical: the report is now merged, and temporary worktrees have been removed. Accepted routing defaults come from the resolved shipping decision, not the research's earlier open questions.
- Work in the user's single primary workspace; do not create additional persistent Git worktrees. Disposable test repositories and probe copies remain the approved isolation boundary. Synchronization must preserve unrelated work and stop when safe isolation or a branch transition is not possible.
- Preserve logical dependencies when using native `/to-tickets`: classification underpins bookkeeping synchronization; native review identity and evidence lineage underpin reuse and publication; milestone acceptance consumes ticket evidence; consumer transition covers the resulting contracts. Do not replace the existing Wayfinder decision tickets with implementation tickets.
- This local tracker specification is ready for native `/to-tickets`. It does not execute implementation, start a milestone review, or authorize a commit, push, PR, or merge.
