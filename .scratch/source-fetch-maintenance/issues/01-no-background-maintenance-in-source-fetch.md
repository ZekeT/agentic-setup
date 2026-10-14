# 01: Starter source fetch must not start background Git maintenance

**What to build:** Verifying a consumer update against a pinned starter source never fails because a background Git process is still writing to the temporary fetch repository. Verification Git commands start no background maintenance, so `prepare`, `status`, `check` and `record` with a `starter_source` give the same result every time.

**Blocked by:** None (can start immediately). Land before ticket 03 of `engineering-test-speed`, which touches the same verification Git code.

**Status:** implemented; independent verification pending (not accepted, published or merged)

**Review tier:** sensitive (verification modules)

- [x] A starter source fetch starts no `git maintenance` (or auto-gc) process, whatever Git's default auto-maintenance settings are
- [x] A regression test fails if any Git command during `verify prepare` with a pinned starter source starts background maintenance
- [x] The isolated Git environment (no system/global config, no replace objects, no prompts), transport restrictions and the 60-second timeout are unchanged
- [x] The existing starter-update integration tests pass unchanged

## Comments

Observed on 2026-10-14 in CI for PR #51 (docs only). Four starter-update tests failed with `[Errno 39] Directory not empty: '/tmp/engineering-source-…/.git…'`, on Git 2.55.0. `main` had passed three hours earlier on the same Git version, so the failure is intermittent.

Cause, confirmed locally with a trace: `git fetch` launches `git maintenance run --auto --quiet --detach` after it finishes. The isolated environment ignores global configuration, so Git's default auto-maintenance applies inside the temporary fetch repository. The detached process takes a lock under `.git/objects` while `TemporaryDirectory` cleanup deletes the tree, and the cleanup error replaces the real verification result. With `-c maintenance.auto=false` the child is not started.

The 2026-10-10 CI failure was the same race inside the tests' own fixture repositories, fixed then by quieting maintenance in fixtures only. Production fetches still raced.

Implemented 2026-10-14: the isolated verification Git environment now injects `maintenance.auto=false` and `gc.auto=0` through `GIT_CONFIG_COUNT`, which covers source fetches and every other verification Git command. A new starter-update integration test traces every Git child process during `verify prepare` and failed before the fix (two detached `git maintenance run --auto` starts); it passes after. The starter-update module passes (30 tests).

Correction 2026-10-14: the first authoritative run failed (79 failed, 84 errors) because the changed managed module's distribution fingerprints were not regenerated, so template builds and adoption rejected it with "template distribution hash mismatch". Regenerated with the manifest generator; the previous upstream hash is retained as `previous`, so installations on the current release update cleanly.
