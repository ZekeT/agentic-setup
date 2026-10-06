# Synchronize existing tracker fields safely and idempotently

Type: grilling
Status: resolved
Assignee: Codex session for zeke
Blocked by: 02, 03
Parent: [Engineering v3-1d decision map](../map.md)

## Question

Which existing status, delivery-link, and evidence fields can `/ssync` recognize and update safely, and how does one explicit invocation create or update at most one bookkeeping PR idempotently?

Inspect actual tracker layouts to specify a narrow supported grammar and precise skip behavior. Preserve prose, evidence caveats, and acceptance checkboxes. Define authoritative evidence per stage, unknown/missing/conflicting evidence, relationship to qualifying bookkeeping validation, PR discovery and reuse, no-op behavior, self-sync avoidance, concurrent changes, and failure/retry handling.

Keep observation, implementation, independent verification, human acceptance, publication, and observed merge distinct. Use existing fields only; no new marked block, general tracker parser, automatic invocation, or merge authorization.

## Comments

### Initial fact-finding

Read-only inspection found implementation-ticket `**Status:**` fields, breakdown `Status` cells, and some dedicated `PR` cells. Other breakdowns embed PR links in status text. Ticket identity can be a relative path or directory-local number; aggregate rows and shared PRs prevent naive one-to-one mapping. Plain Wayfinder `Status:` fields express discussion state, not delivery state.

No consistent dedicated evidence-field grammar was established in the inspected tickets. Evidence/handoff sections contain chronological prose, failed checks, acceptance history and caveats; do not rewrite them as machine fields. The v3-1c publish-from-linked-worktree ticket and breakdown explicitly preserve missing historical independent-review evidence despite observed merge.

Existing provider lookup reuses only a single open PR with exact source/base/head identity. It does not support updating an existing PR after a new bookkeeping commit; it rejects ambiguous or closed matches, and uncertain create outcomes need provider reconciliation. A new standalone sync operation must define safe branch reuse, concurrency and retry behavior without modifying or wrapping Matt's skills.

Pending choices: bounded invocation scope; initial supported field shapes and skip rules; sync branch/PR lifecycle; conflict and uncertain-outcome handling. Existing per-stage evidence, no-merge, no-auto-invocation and bookkeeping-exemption constraints remain settled.

## Answer

Resolved through the user's explicit agreement to all four recommendations.

### Invocation scope

One explicit invocation synchronizes one selected effort directory, considering its implementation tickets and breakdown together. Exclude Wayfinder decision statuses. If the effort is not identifiable, ask rather than scan all historical efforts. This remains a standalone harness operation; do not modify or wrap Matt's skills.

### Supported fields and evidence

Initially recognize implementation-ticket `**Status:**` fields, uniquely identified breakdown status cells, and existing PR-link fields. Change only recognized value spans. Preserve all surrounding prose, evidence caveats, and acceptance checkboxes, with deterministic validation accounting for every changed byte. Skip aggregate rows, duplicate fields, and ambiguous identities rather than guessing.

Existing narrative evidence sections are not writable fields: preserve their chronology and report missing evidence without inventing a new format. Record stages only from evidence for that stage; observed merge does not establish verification or human acceptance. Unknown or conflicting evidence must not produce an unsupported status assertion. No new marked block or general tracker parser.

### Branch and PR lifecycle

Use a dedicated sync branch per effort and target branch. Reuse its single open bookkeeping PR, adding commits only when the desired tracker content changes. An unchanged invocation creates no commit or PR. After merge, begin another cycle only when new discrepancies exist. Exclude sync PRs themselves from synchronization. Explicit invocation authorizes creation or update of at most one bookkeeping PR, not merge or automatic future invocation.

### Concurrency and retries

Work in isolation and recheck source files and the remote branch before writing. Stop on conflicting edits; never force-push or overwrite human changes. After an uncertain push or PR response, inspect remote state before retrying so a successful operation is not duplicated. Ambiguous PR identity is not proof that no PR exists.

The existing exact-head publication lookup does not yet supply this update lifecycle. Its implementation must honor the above contract and the accepted mechanical-bookkeeping validator; this decision does not claim that capability already exists. No implementation or publication was performed by this decision session.
