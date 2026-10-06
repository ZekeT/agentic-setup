# Engineering v3-1d decision map

Label: wayfinder:map

## Destination

Resolve the remaining Engineering v3-1d design questions into a specification-ready handoff for `/to-spec` → `/to-tickets`, covering the full settled scope in [the confirmed discussion](discussion.md). This map produces decisions, not implementation.

## Notes

- Destination and initial frontier confirmed by the user on 2026-10-05.
- Map complete: final specification handoff confirmed by the user on 2026-10-07. All child decisions are resolved; next step is `/to-spec` using this map and its linked latest answers, followed by `/to-tickets`.
- The consolidated settled direction in [the discussion](discussion.md) supersedes tentative round history and the earlier [intent](intent.md). Preserve those decisions; do not reopen them implicitly.
- [ADR 0003](../../docs/adr/0003-reuse-upstream-review-and-exempt-bookkeeping.md) records the accepted target design. ADR 0002 remains operational policy until its replacement is implemented.
- Use Wayfinder, grilling, and domain-modeling; research tickets also use the research skill. Consult the [product glossary](../../docs/context/product.md) and [configured tracker](../../docs/agents/issue-tracker.md).
- Use the local Markdown tracker: child issues live in `issues/`; query open, unclaimed children whose blockers are resolved, ordered by number. Claim before work. Resolve no more than one non-research ticket per session through the required human exchange.
- Research findings live beside the future spec, recording the question, dated primary sources, findings, uncertainties, and decision implications. Research establishes facts; routing preferences and other design choices remain human decisions.
- Preserve distinct Standards, Spec, behavioral, and applicable security responsibilities. Preserve initial full applicable suites, bounded correction checks with escalation, honest evidence lineage, strict treatment of mixed/ambiguous changes, and existing clean-rebase conditions.
- `/ssync` is explicitly invoked, edits narrowly recognized existing status/link/evidence fields, preserves prose and acceptance criteria, skips ambiguity, and authorizes one bookkeeping PR without merge. No new marked block or general tracker parser.
- Keep shared policy and deterministic tooling portable between Claude Code and Codex. Latest user constraint: do not modify Matt Pocock skills or build wrappers on top of them. This supersedes earlier adapter-specialization permission; native committed review is now the accepted integration.
- The user permits separate harness tools for checks, evidence storage, and publication gates, provided they do not intercept or replace Matt's workflow. This does not authorize skill wrappers or altered upstream orchestration.
- Charting does not authorize implementation, commits, publication, or operational-policy changes. Keep existing discussion, glossary, and ADR edits intact.

## Decisions so far

<!-- Resolution index only. The confirmed discussion is input, not a ticket resolved by this map. -->

- [Establish supported runtime shipping-model controls](issues/06-runtime-routing-research.md): concrete routing controls and runtime limits are documented; account access and routing defaults remain distinct from advertised settings.

- [Classify code, documentation, and mechanical bookkeeping](issues/02-change-classification.md): prove every bookkeeping edit, assess documentation by changed content, and limit comment exemptions to syntax-validated harmless cases.

- [Bind independent review to exact proposed content](issues/01-exact-content-review.md): use native review after ordinary checkpoint commits, with separate evidence tools and no skill wrappers.

- [Link correction checks and retained evidence honestly](issues/03-correction-evidence.md): independently validate targeted checks and cumulative evidence; retain both native semantic axes and label historical coverage honestly.

- [Synchronize existing tracker fields safely and idempotently](issues/04-ssync-contract.md): synchronize one effort through narrow existing fields and one reusable PR, preserving caveats and reconciling conflicts or uncertain retries.

- [Define milestone review triggers and acceptance](issues/05-milestone-review.md): a standalone `/milestones` skill plans and recalibrates feature milestones with the user; explicit closure triggers broad independent review and human acceptance.

- [Choose portable shipping-model routing and fallback](issues/07-shipping-routing.md): configurable Sol-low/Sonnet-low shipping agents, reported current-session fallback, and serialized publication using existing accepted evidence.

- [Bound formatting and remove duplicate check execution](issues/08-formatting-and-check-optimization.md): explicit intended-file formatting, proven check deduplication, and immutable fixture preparation with isolated test state.

- [Preserve compatibility while evolving review evidence and distribution](issues/09-migration-and-compatibility.md): fresh proof at the contract transition, reconciled publication retries, protected consumer updates, and no Graphify preservation requirement.

- [Confirm a coherent specification handoff](issues/10-specification-handoff.md): consolidated scope accepted for `/to-spec` → `/to-tickets`, accounting for separately published work and preserving current gates until implementation.

## Not yet specified

None. Final handoff confirmed; no unresolved decisions block specification.

## Out of scope

- Implementing the destination, creating implementation slices, or executing delivery during this map; hand off to `/to-spec` and `/to-tickets`.
- New performance instrumentation, diagnostics, timing/progress/slow-test reports, benchmarking reports, token telemetry, or numeric savings promises.
- Automatic `/ssync` invocation; initial operation is explicit only.
- Replacing pinned upstream skills, adding a general tracker parser, introducing a new marked bookkeeping block, or translating/dual-writing Wayfinder Maps artifacts.
- Merge authorization or unrelated repository changes.
