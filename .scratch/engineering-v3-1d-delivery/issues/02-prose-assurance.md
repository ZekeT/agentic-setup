# 02: Give prose changes appropriate assurance

**What to build:** A prose-only change receives lightweight independent documentation review and relevant checks, while consequential documentation still receives assurance appropriate to its behavior.

**Blocked by:** [01: Use native review evidence through publication](01-native-review-evidence.md).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] Public verification classifies actual changed content alongside configured documentation locations, ownership, and risk constraints; a Markdown suffix, title, or assertion is insufficient.
- [ ] Prose-only changes require one independent documentation review and relevant documentation checks without an unrelated application suite.
- [ ] Policy, agent instructions, requirements, and changed executable examples receive stricter review and checks appropriate to their impact. An unchanged executable example elsewhere does not disqualify a prose-only correction.
- [ ] Mixed, unsupported, or uncertain changes take the stricter substantive route; attempts to lower their own requirements through configuration changes do not bypass existing safeguards.
- [ ] A public-command journey verifies a prose correction through publication, rejects missing documentation proof, and contrasts it with changed instructions and mixed code/documentation scope.
- [ ] Ship the classification contract, user-facing explanations, consumer distribution changes, and meaningful regression tests together. Mechanical bookkeeping and comment exemptions are not enabled by this slice.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
