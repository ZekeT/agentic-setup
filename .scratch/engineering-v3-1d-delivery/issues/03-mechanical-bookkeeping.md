# 03: Verify and publish mechanical bookkeeping

**What to build:** A narrowly supported tracker-value change can be validated and published without model review or application tests, while preserving the surrounding record and any justified code evidence.

**Blocked by:** [02: Give prose changes appropriate assurance](02-prose-assurance.md).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] Deterministic validation accounts for every changed byte and supported value span. Only uniquely recognized existing status, delivery-link, or supported evidence-pointer values can qualify, with evidence for the specific stage asserted.
- [ ] All other bytes remain unchanged, including prose, chronology, caveats, and acceptance checkboxes. Mode or other identity changes cannot be silently ignored.
- [ ] Unknown or duplicate fields, ambiguous identity, aggregate layouts, mixed changes, and unsupported edits fail exemption eligibility rather than receiving a guessed classification.
- [ ] Qualifying bookkeeping requires deterministic validation but neither model review nor application tests. Existing code evidence is retained only with validated eligibility and freshness; edits affecting verification inputs do not automatically preserve it.
- [ ] A merged PR cannot establish independent verification or human acceptance. Unknown or conflicting stage evidence cannot support a new assertion.
- [ ] Public-command tests demonstrate valid publication, preservation outside allowed spans, unchanged code evidence where justified, and rejection of deceptive or mixed edits. Existing publication authorization and recovery rules remain enforced.
- [ ] Deliver consumer updates and operating guidance without a general tracker parser or new marked bookkeeping block. Narrative evidence is not promoted into a supported machine field.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
