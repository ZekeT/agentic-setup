# Classify code, documentation, and mechanical bookkeeping

Type: grilling
Status: resolved
Assignee: Codex session for zeke
Parent: [Engineering v3-1d decision map](../map.md)

## Question

What deterministic content rules and supporting evidence distinguish code changes, substantive documentation, and qualifying mechanical bookkeeping, and select their review/check obligations?

Specify positive eligibility and rejection conditions, handling of mixed or ambiguous changes, security-sensitive instructions and policy, executable examples, requirements and acceptance criteria, comment-only exemptions, and verification inputs. Markdown paths or change titles alone cannot establish an exemption. Explain how narrowly recognized existing fields can be validated without a general tracker parser or a new marked block.

Use concrete existing repository examples. The classification contract should permit a qualifying bookkeeping-only delta to retain code evidence while requiring lightweight independent review and relevant checks for substantive documentation.

## Comments

### Initial fact-finding — 2026-10-06

Current classification in `verification_requirements.py` uses paths and ownership; every plan still requires `make check`. Agent policy paths cannot use the documentation floor. The target exemption therefore needs a new content-validation/check-selection contract, not just a tier rename.

Existing tracker examples include `**Status:**` lines, plain `Status:` lines, and table cells. Engineering v3-1c's publish-from-linked-worktree ticket and breakdown explicitly pair observed merge with missing historical independent-review evidence. Evidence sections also contain historical prose that must not be rewritten as current status. A narrow validator can anchor unique known fields and require equality outside supported value spans; whether such a proof is accepted is pending the human exchange.

Existing snapshots bind content, modes, plans, explicit inputs and tool context. Bookkeeping in a verification input cannot automatically preserve proof. Pending decisions: exact mechanical-proof boundary, documentation eligibility/check routing, and safe scope of comment-only exemptions. No classifier or policy implementation changed.

## Answer

Resolved 2026-10-06 through the live human exchange: the user agreed to all three classification recommendations.

### Mechanical bookkeeping

Require deterministic accounting for every changed byte. Only uniquely recognized existing status, delivery-link, or evidence-pointer values may change, with evidence supporting the particular stage asserted. Require byte-for-byte preservation outside those values, including surrounding prose, caveats, and acceptance checkboxes. A merged PR does not establish verification or human acceptance.

Unknown or ambiguous layouts fail exemption eligibility; `/ssync` skips them rather than guessing. Mixed changes retain the stricter substantive requirements. A title, Markdown suffix, or agent assertion cannot establish eligibility. No new marked block or general tracker parser is introduced. Changes affecting verification inputs cannot automatically retain prior evidence; the correction-evidence contract must establish whether retention is justified.

Qualifying bookkeeping receives deterministic validation without model review or application tests, as already settled. Exact supported field grammar belongs to [Synchronize existing tracker fields safely and idempotently](04-ssync-contract.md).

### Substantive documentation

Use configured documentation locations together with inspection of the actual changed content. Prose-only changes receive one independent documentation review and relevant documentation checks. Changes to agent instructions, policy, requirements, or executable examples receive stricter review and checks appropriate to their impact; Markdown is not inherently inert.

An unchanged executable example elsewhere in a document does not disqualify a prose correction. Fixing a README explanation can qualify; changing a command that users are told to execute requires validation of that command. Mixed or uncertain content follows stricter requirements. This does not make policy or executable-example changes mechanical bookkeeping.

### Comment-only exemptions

Initially recognize only supported cases where syntax-aware validation proves executable structure unchanged and rules out meaningful directives. Exclude docstrings, tool directives, generated-file markers, and agent-consumed instructions. Unsupported or uncertain cases retain the stricter classification. A comment prefix alone is insufficient proof; this narrow exemption does not make comments mechanical bookkeeping.

This is the accepted target classification contract, not an implementation or a change to current gates. Correction lineage/check escalation and `/ssync` grammar remain in their respective decision tickets.
