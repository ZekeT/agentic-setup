# 03: Batched Git reads in the verification modules

**What to build:** `verify status`, `prepare`, `check` and `record` gather the Git data they need with batched plumbing calls instead of one subprocess per question, so real verification and the existing suite both get faster with no observable change. See the [spec](../spec.md), "Git batching (verification modules)".

**Blocked by:** PR #50 merged (external; met on 2026-10-14). Start on a fresh branch from updated `main`.

**Status:** ready-for-agent

**Review tier:** sensitive (verification modules)

- [ ] Baseline listings use one recursive tree listing per baseline
- [ ] Object content and existence come from batched `cat-file` reads rather than per-object subprocesses
- [ ] Tracked, untracked and unmerged state come from one listing where the current code makes several calls
- [ ] Baseline reads made during requirement computation (installation role, manifest, settings) come from the same batched baseline content
- [ ] The isolated Git environment (no system/global config, no replace objects, no prompts), regular-blob validation, rejection of tracked verification records and no-filter reads are unchanged
- [ ] Snapshot identity for the same content equals the pre-batching identity; stored record schema, CLI output and error messages are unchanged; no schema version bump
- [ ] The existing engineering test suite passes with no test changes; no call-count or timing assertions are added
- [ ] Local before-and-after timings (one `verify status`, one typical verification test, full suite) and Git call counts are recorded in this ticket
