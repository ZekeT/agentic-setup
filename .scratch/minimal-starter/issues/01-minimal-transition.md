# 01: Minimal transition

**What to build:** Safely remove old starter overhead through external preview/apply.
**Blocked by:** None
**Status:** implemented; awaiting human review

- [x] Preview leaves target untouched and explains actions/conflicts.
- [x] Apply preserves source, tasks, tests, custom instructions and useful hooks.
- [x] Known old wiring is removed; customized active wiring blocks completion.
- [x] Repeated apply is a no-op; stale plans and unsafe paths fail.
- [x] Native checks and scoped rollback are demonstrated in a disposable legacy project.

Evidence: tests/test_transition.py, tests/test_recovery.py, tests/test_updates.py and tests/test_skills.py. Full native suite passed before review; focused regressions pass after corrections. Real pinned skill bundles were installed and reapplied in a disposable project. Live application migration remains unavailable.
