# 11: Route shipping with a truthful fallback

**What to build:** Authorized shipping can use configurable runtime-specific agents and continue through a reported current-session fallback without changing accepted scope or duplicating publication.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [ ] Configure shipping model/effort independently of other agents, using accepted starting defaults of gpt-6.1-sol with low reasoning for Codex and sonnet with low effort for Claude Code.
- [ ] Dispatch through actual supported runtime controls and respect runtime restrictions. Report requested settings, observed effective settings when available, and uncertainty when exact execution is not observable.
- [ ] Pass pointers to accepted scope, branch, current evidence, target, authorization, and prepared publication plan instead of implementation conversation history.
- [ ] When the preferred shipper cannot run, report why and continue in the current session within existing authorization. Stop/reconcile any previous publisher and serialize Git/provider mutations; changing models cannot bypass gates.
- [ ] The shipper validates its inputs and returns a real PR/MR URL or precise partial progress and recovery guidance. It performs no application fixes, acceptance reinterpretation, repeated valid suites, force-push, or merge.
- [ ] Reuse the existing public publication interface and exact prepared-body handoff; retain the manual PR template. Do not rebuild PR #46 or require the later evidence contract before this ticket can start.
- [ ] Fake runtime/provider interaction tests cover rejected dispatch, substitution or unknown model identity, fallback, concurrent publisher prevention, uncertain remote outcomes, and unchanged authorization/body. Label untested account access and optional live model runs honestly.
- [ ] Deliver runtime adapters and configuration/update guidance without modifying Matt skills or adopting /implement-spec, and without creating persistent worktrees.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.
