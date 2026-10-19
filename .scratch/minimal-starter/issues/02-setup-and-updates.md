# 02: Setup and selective updates

**What to build:** Configuration-only initialization/adoption and explicit scoped updates.
**Blocked by:** 01: Minimal transition
**Status:** implemented; review corrections in progress

- [x] Initialization refuses existing destinations; Python seed is opt-in.
- [x] Matt setup contracts and skills are available from recorded versions.
- [x] Existing guidance is reused; skills never collide or silently upgrade.
- [x] Later selective update preserves application changes and customization.

Evidence: tests/test_transition.py, tests/test_recovery.py, tests/test_updates.py and tests/test_skills.py. Full native suite passed before review; focused regressions pass after corrections. Real pinned skill bundles were installed and reapplied in a disposable project. Live application migration remains unavailable.
