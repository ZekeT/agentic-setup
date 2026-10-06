# Reuse upstream review and exempt mechanical bookkeeping

Status: accepted design (2026-10-05); implementation pending. Supersedes the relevant review and check decisions in ADR 0002 as the agreed target design. ADR 0002 remains operational policy until the replacement is implemented.

Integration amendment: use Matt Pocock skills unchanged, without wrappers. Ordinary scoped checkpoint commits precede native committed-diff review. Separate harness tools handle checks, evidence storage, and publication gates without intercepting or replacing the native workflow.

Use Matt's independent Standards and Spec reviews as primary semantic evidence, preserving both axes and binding their results to the complete proposed content. Remove the overlapping harness maintainability review, but retain a separate fresh behavioral reviewer to probe changed behavior, failure paths, configuration interactions, and nearby regressions. That reviewer consumes recorded authoritative suite results rather than repeating the suite or Standards review. Historical behavioral findings despite green suites justify retaining this independent judgment. Bind native review evidence to the reviewed commit and reject uncovered later changes. When native correction review is required, retain both Standards and Spec axes rather than selecting one through custom orchestration. Separate security review remains required for security-sensitive behavior; broader assessments occur at explicit milestone close or release.

Mechanical bookkeeping receives deterministic validation without model review or application tests. A qualifying bookkeeping-only delta preserves existing code evidence. Substantive documentation receives lightweight independent review and relevant checks. These exceptions deliberately reduce assurance compared with ADR 0002's universal checks and path-only floor; they require validation of actual content, not trust in a title or author-declared category. Policy, requirements changes, and executable content do not qualify as bookkeeping.

Retain an initial full applicable suite per code-changing issue PR, run through the harness once by the implementer and reused by reviewers and shipping. Subsequent corrections receive independent review and checks specific to the fix and affected behavior; documentation-only fixes receive documentation checks. Cross-cutting or uncertain impact broadens verification up to the full suite. Retained earlier results must not be represented as a full-suite run on final revised content. This accepts narrower regression coverage for bounded corrections rather than repeating every check for every fix.

Qualifying clean rebases retain reviewer evidence under the existing carry conditions but rerun full applicable checks on the new combined content. Refreshing a remote tip without changing tested content does not require a rerun. Mixed or ambiguous content receives the stricter substantive requirements. Bookkeeping validation recognizes narrowly permitted existing fields without introducing a new ticket format or general tracker parser.

Performance instrumentation, diagnostics, benchmarking reports, and token telemetry are omitted for now. Cost improvements come from removing duplicate work and bounded optimization, without a promised numeric reduction. The user confirmed shared understanding; design acceptance does not authorize implementation or relax current gates.

## Considered options

- A new combined semantic reviewer: does not remove duplication if Matt's reviewers still run during implementation.
- Eliminating the separate behavioral pass: rejected for now because its explicit behavioral probing and fresh perspective have demonstrated value beyond passing automated tests. Extending the Spec reviewer could be reconsidered with evidence of equivalent coverage.
- Targeted-only tests per issue PR: could lower latency further, but the current preference is to measure deduplication and optimization before reducing integration coverage.
- Universal review and test reruns after status edits: spends assurance effort on unchanged logic; mechanically validated deltas provide a narrower alternative.
