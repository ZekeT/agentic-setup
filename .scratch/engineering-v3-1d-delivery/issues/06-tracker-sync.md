# 06: Synchronize one effort through a reusable PR

**What to build:** Explicit /ssync reconciles supported implementation-tracker fields for one effort and safely creates or updates at most one bookkeeping PR.

**Blocked by:** [03: Verify and publish mechanical bookkeeping](03-mechanical-bookkeeping.md).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] Select one effort explicitly or ask when it is unclear; consider implementation tickets and their breakdown together, excluding Wayfinder decision statuses and synchronization PRs themselves.
- [ ] Initially update only recognized implementation-ticket bold Status values, uniquely identified breakdown status cells, and existing PR-link fields. Preserve prose, narrative evidence, caveats, and acceptance checkboxes.
- [ ] Use evidence for each individual delivery stage. Report unknown or conflicting evidence and skip duplicate, aggregate, ambiguous, or unsupported layouts without inventing assertions or a new format.
- [ ] Validate every changed byte through the bookkeeping contract before publication; no general tracker parser or marked bookkeeping block is introduced.
- [ ] Use a dedicated branch per effort and target and reuse its one open PR. Changed content creates a commit; unchanged invocation creates neither commit nor PR. After merge, create a new cycle only for new discrepancies.
- [ ] Extend exact-head publication recovery to support deliberate updates to the existing synchronization PR. Reconcile uncertain push/create outcomes and ambiguous provider results before retrying.
- [ ] Recheck source files and remote state before writing; stop on conflicts and preserve unrelated work without force-push. Use the single primary workspace and stop if a safe branch transition is not possible; do not create persistent worktrees.
- [ ] Explicit invocation authorizes at most one bookkeeping PR creation/update, not merge or future automatic invocation. Preserve applicable current publication proof and authorization.
- [ ] Real local Git with fake hosting tests proves no-op repeats, same-PR updates, post-merge cycles, conflicting edits, uncertain outcomes, and preservation of unsupported fields. Deliver command/skill guidance and distribution in this slice.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
