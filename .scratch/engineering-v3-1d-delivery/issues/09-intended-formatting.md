# 09: Format only the intended scope

**What to build:** Developers can format explicitly selected application or harness files without touching unrelated work, with a deliberate command for the combined scope.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] Expose separate application fmt, harness engineering-fmt, and explicit combined fmt-all behavior through project-owned tooling, without upstream skill wrappers.
- [ ] Routine formatting takes an explicit intended-file selection before checkpoint commits and review. Empty selection does nothing; unsupported selections produce a clear error rather than widening scope.
- [ ] Formatting affects only intended supported files, including safe handling of filenames with spaces or option-like text; unrelated source and tracker files remain unchanged.
- [ ] Formatting is preparation rather than evidence of passing lint/review. Required verification remains non-mutating with respect to source content.
- [ ] Consumer updates preserve project-owned recipes and configuration; managed formatting changes appear through the existing preview/conflict contract.
- [ ] Public command tests cover application/harness/combined selection, empty input, unsupported or unsafe paths, unusual filenames, and untouched unrelated content. Deliver usage guidance and generated distribution changes together.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
