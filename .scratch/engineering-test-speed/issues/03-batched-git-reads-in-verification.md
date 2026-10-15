# 03: Batched Git reads in the verification modules

**What to build:** `verify status`, `prepare`, `check` and `record` gather the Git data they need with batched plumbing calls instead of one subprocess per question, so real verification and the existing suite both get faster with no observable change. See the [spec](../spec.md), "Git batching (verification modules)".

**Blocked by:** PR #50 merged (external; met on 2026-10-14). Start on a fresh branch from updated `main`.

**Status:** merged (PR [#54](https://github.com/ZekeT/agentic-starter/pull/54), `210a983`)

**Review tier:** sensitive (verification modules)

- [x] Baseline listings use one recursive tree listing per baseline
- [x] Object content and existence come from batched `cat-file` reads rather than per-object subprocesses
- [x] Tracked, untracked and unmerged state come from one listing where the current code makes several calls
- [x] Baseline reads made during requirement computation (installation role, manifest, settings) come from the same batched baseline content
- [x] The isolated Git environment (no system/global config, no replace objects, no prompts), regular-blob validation, rejection of tracked verification records and no-filter reads are unchanged
- [x] Snapshot identity for the same content equals the pre-batching identity; stored record schema, CLI output and error messages are unchanged; no schema version bump
- [x] The existing engineering test suite passes with no test changes; no call-count or timing assertions are added
- [x] Local before-and-after timings (one `verify status`, one typical verification test, full suite) and Git call counts are recorded in this ticket

## Comments

- 2026-10-15: implemented.
  - Reads named by full object IDs (the baseline listing and blob batch) are reused within one process (`addressed_objects` in `verification_git.py`), so each baseline is listed and read once per operation. References such as `HEAD` are always read again; failures are never reused.
  - Requirement computation takes the baseline blobs read from the repository at the plan base (the same commit `materialize` sets as the checkout `HEAD`) instead of per-file `ls-tree`/`show` calls on the checkout. These reads now use the isolated Git environment. The docs-path executable check uses the baseline mode from the same listing.
  - Tracked and unmerged state come from one `ls-files --stage`; checkout validation lists tracked and untracked paths in one `ls-files --cached --others --exclude-standard`.
  - `verify` resolves the evidence location once per operation (before taking the lock) instead of twice.
  - Not changed: base resolution through `scripts/lib/change.sh` (`merge_base` and the base tip still spawn their own shell and `rev-parse` calls), the checkout clone, and publication modules.
  - Snapshot identity: on a fixture with a tracked edit, an untracked file and a Markdown edit, `prepare` with the pre-change tooling and then `status` and `prepare` with the new tooling all gave snapshot `93746bfb887f…`, not STALE, with the same floor.
  - No test files changed.
- Local measurements, 2026-10-15 (same machine, load average about 3–4 in both runs):

  | Measure | Before | After |
  |---|---|---|
  | Git calls: `verify prepare` (3-file fixture) | 52 | 29 |
  | Git calls: `verify check` | 87 | 49 |
  | Git calls: `verify record` | 47 | 26 |
  | Git calls: `verify status` | 47 | 26 |
  | One `verify status` | 0.86 s | 0.54 s |
  | `test_reuse_across_sessions_and_content_preserving_commit` | 9.57 s | 5.99 s |
  | Full engineering pytest suite (593 tests) | 1274 s | 887 s |
- 2026-10-15: published as PR [#54](https://github.com/ZekeT/agentic-starter/pull/54) and merged into `main` as `210a983` (GitHub `mergedAt` 2026-10-14T18:57:46Z).
