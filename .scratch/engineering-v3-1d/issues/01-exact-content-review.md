# Bind independent review to exact proposed content

Type: grilling
Status: resolved
Assignee: Codex session for zeke
Parent: [Engineering v3-1d decision map](../map.md)

## Question

How should unmodified Matt Pocock skills review complete proposed content, with separate harness tools recording checks, evidence, and publication eligibility without intercepting or replacing the native workflow?

Resolve the review input/snapshot contract, treatment of uncommitted and untracked proposed files, fresh-session boundaries, recording each findings axis once, stale-result detection, and orchestration relative to formatting, recorded suite execution, and commits. Preserve the settled distinction between automated-check execution and independent behavioral judgment. Determine the handoff when a runtime cannot provide the required fresh reviewer.

Inspect installed upstream orchestration and harness evidence interfaces. Use the confirmed discussion and accepted target ADR as constraints; do not interpret their acceptance as authorization to implement.

## Comments

### Initial fact-finding — 2026-10-05

Claimed for the live Wayfinder design exchange; no resolution yet. Read-only delegated inspection established:

- Pinned `implement/SKILL.md` invokes review before its final commit; `code-review/SKILL.md` selects `git diff <fixed-point>...HEAD` and has no documented snapshot override. Standards and Spec are independent axes.
- `verification_checkout.py` already builds a scoped proposed working tree over the comparison base, including additions, deletions, and executable modes. Its HEAD/index remain at the base, so unchanged upstream committed-diff discovery sees an empty diff.
- `verification_snapshot.py` already binds content, plan, explicit inputs, and tool context; all committed PR paths must be included. Content-preserving commits can retain evidence. Existing validation does not bind a synthetic projection's HEAD/index.
- The evidence schema currently supports maintainability, behavioral, and security, so Standards/Spec need explicit target-design representation. Recorded suite execution and behavioral judgment are already separate artifacts.
- Candidate integration choices: narrowly specialize upstream diff discovery in a thin adapter while reading pinned reviewer briefs, or create and validate a synthetic review-only commit in isolation. Neither is implemented or selected.

Pending human choices: reviewer input mechanism; scheduling of semantic review versus initial recorded checks; isolation of reviewer probes. Preserve existing scope/freshness safeguards and INCOMPLETE handoff when independent reviewers are unavailable. Correction lineage remains in its own decision ticket.

## Prior answer — integration choice superseded

Resolved 2026-10-06 through the live human exchange: the user accepted all three recommendations.

- **Reviewer input:** thin runtime adapters specialize upstream diff discovery to present the complete harness-captured proposal, including intended uncommitted and untracked additions, deletions, and modes. Read the pinned upstream reviewer instructions unchanged; do not fork the skills or introduce synthetic review commits. Preserve existing declared-scope safeguards and snapshot freshness validation.
- **Timing:** format intended content, then capture the complete proposal. Standards and Spec review may run alongside the initial authoritative recorded suite against the same frozen identity. Behavioral review follows and consumes its results; it does not repeat the suite. Keep Standards, Spec, behavioral, and applicable security results distinct, with fresh independent reviewers and serialized evidence recording. A failed suite remains blocking evidence, never a passing behavioral result.
- **Probes:** keep canonical captured review content immutable. Run mutating experiments in disposable copies initialized from that content, and bind probe observations and their limitations to its identity so experiments cannot alter another review or the implementation workspace.
- Give reviewers requirement/spec/request and snapshot pointers plus factual check evidence, not implementation-session reasoning. If required fresh reviewers are unavailable, report INCOMPLETE with a fresh-session handoff; never self-certify.
- Content changes require freshness reassessment; content-preserving commits can retain evidence under the existing content-based safeguards. Detailed correction lineage and check escalation remain in [Link correction checks and retained evidence honestly](03-correction-evidence.md).

This resolves the review input and orchestration contract only. Classification, correction lineage, and later migration details remain with their respective tickets/fog. No operational policy or implementation changed.

## Reopened: no skill wrappers

The user explicitly ruled out modifying Matt Pocock skills or building wrappers on top of them. This supersedes the accepted adapter-specialized diff-discovery mechanism. Reopen the integration decision; do not implement that mechanism, copy upstream reviewer orchestration, or substitute a wrapper under another name.

The earlier content-identity, independent-review, and isolated-probe objectives remain constraints, but their compatibility and scheduling must be established using the unmodified skills. Clarify whether separate harness check/evidence tooling remains desired and how native committed-diff review fits, without assuming permission to wrap invocation. No replacement mechanism has been accepted.

### Confirmed tooling boundary

The user permits separate harness tools for checks, evidence storage, and publication gates, provided they do not intercept or replace Matt's workflow. Native review handoff remains to settle; no replacement orchestration is authorized.

The installed native `code-review` requires a nonempty committed diff to HEAD and always runs Standards plus Spec when a spec exists. `implement` places its final commit after review; it does not document working-tree review. Pending proposal: ordinary scoped checkpoint commits before native review, without custom diff discovery or synthetic review commits. Native two-axis correction review must also be reconciled with the affected-role preference.

## Answer

The user accepted both replacement choices in the live exchange. This answer supersedes the adapter-based mechanism in the prior answer.

- Use Matt's installed skills unchanged, without wrappers, copied orchestration, interception, or replacement of their workflow.
- Make ordinary scoped local checkpoint commits before native committed-diff review. No synthetic review commits or custom diff discovery. Intended additions and other proposed changes must be committed for native review to cover them; uncommitted later changes are not covered by that review.
- Separate harness tools may execute and record checks, store evidence, and enforce publication gates. Record the reviewed commit and content identity, and reject uncovered later changes. Local commits do not imply acceptance or publication authorization.
- Whenever native correction review is required, accept both Standards and Spec axes. Do not add affected-axis selection around the skill. This supersedes the earlier preference to rerun only an affected semantic axis.
- Preserve separate fresh behavioral inspection and applicable security review, exact evidence identity, and disposable copies for mutating probes. Behavioral inspection consumes recorded suite evidence. Missing required independent review remains INCOMPLETE with a fresh-session handoff.
- Parallel scheduling is permissible only where native workflow permits it; the earlier adapter-controlled overlap is not a requirement to intercept upstream orchestration.

The corresponding correction-evidence policy is recorded in [Link correction checks and retained evidence honestly](03-correction-evidence.md). These are target design decisions; current operational policy remains unchanged pending implementation.
