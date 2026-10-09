# 04: Recognize genuinely inert comment changes

**What to build:** Supported inert comment edits receive the agreed narrow exemption only when syntax-aware validation proves they cannot change executable behavior or meaningful directives.

**Blocked by:** [02: Give prose changes appropriate assurance](02-prose-assurance.md).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] The public classification result distinguishes proven inert comments from substantive code and mechanical bookkeeping; supported cases prove executable structure unchanged.
- [ ] Docstrings, tool directives, generated-file markers, and agent-consumed instructions are excluded. A comment prefix by itself never proves eligibility.
- [ ] Unsupported syntax, parse failures, ambiguous changes, mixed content, and relevant mode changes retain stricter requirements.
- [ ] Tests exercise equivalent executable structure, directive-like content, unsupported syntax, and mixed edits through the public assurance route, including publication refusal when stricter proof is missing.
- [ ] Document the supported syntax boundary, distribute the behavior with its tests, and preserve independent/security responsibilities whenever the inertness proof does not apply.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
