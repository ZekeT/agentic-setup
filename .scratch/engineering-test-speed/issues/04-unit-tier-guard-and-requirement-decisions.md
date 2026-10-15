# 04: Unit tier, subprocess guard and pure verification requirement decisions

**What to build:** Maintainers get a unit tier that runs in seconds with one ordinary pytest invocation and that refuses to start subprocesses. Verification requirement rules (path classification, tier floors, required checks, plan shape) are decided from a plain facts value, so each rule is unit tested by writing the facts down instead of building a repository. See the [spec](../spec.md), "Unit tier and guard" and "Facts value and pure decisions".

**Blocked by:** 02 (ADR and maintainer testing standard), 03 (batched Git reads). Both merged.

**Status:** merged (PR [#55](https://github.com/ZekeT/agentic-starter/pull/55), `0e6eea8`)

**Review tier:** sensitive (verification modules)

- [x] The existing, currently empty unit test directory holds the unit tier; it runs inside the existing engineering test target, and the fast loop is an ordinary pytest invocation on that directory
- [x] An automatically applied unit-tier fixture fails any test that starts a subprocess, naming the test and the attempted command; it does not apply to integration or end-to-end tests
- [x] A test shows that a unit test which starts a subprocess fails with the expected message
- [x] A plain, immutable requirements facts value (installation role at baseline and proposed, manifest ownership entries, project review settings, paths) is gathered once per operation and holds no repository handles
- [x] Path classification (project, managed integration, installation metadata, maintainer tooling, agent policy, prose documentation) is a pure function, unit tested per category
- [x] Per-path and overall tier floor is a pure function of role, ownership, settings and paths, unit tested per floor rule
- [x] Required checks and missing-check rejection derive purely from role, ownership and classified paths, unit tested
- [x] Tier-below-floor rejection and plan-shape validation (separated from filesystem path checks where possible) are unit tested, including each rejection message
- [x] Unit tests cover boundaries: empty, one and many paths; mixed prose and non-prose; base versus proposed role; settings that add floors
- [x] Decision functions read no files, start no processes and touch no clock or environment
- [x] Unit tests assert observable decisions (the returned result, or the validation error and its message) for a given facts value; they do not assert which helper ran, how many Git calls happened, or private intermediate structures
- [x] Unit-tier builders live in the unit tier's own conftest and never read the real repository
- [x] Each CLI-level scenario from the verification-requirements, review-tier and prose-assurance integration tests that only exercised a pure rule is removed only after an equivalent unit test exists that fails when the rule breaks; each removal is noted in this ticket
- [x] At least one end-to-end test per migrated rule group still shows the shell wires the gathered facts into the decision
- [x] Remaining end-to-end tests that need prepared repositories reuse the immutable shared preparation pattern (shared build, fresh writable copy, write guard) where safe
- [x] Verification record schema, snapshot identity, CLI surface and review-tier policy are unchanged
- [x] Local unit-tier and full-suite timings are recorded in this ticket
- [x] The maintainer engineering test standard no longer calls the subprocess guard "planned" or the decision seam future work once both land (follow-up from ticket 02)

## Comments

- 2026-10-15: implemented.
  - Unit tier: `.engineering/tests/unit/` runs inside `make engineering-test` (which already collects `.engineering/tests`). Fast loop: `uv run pytest .engineering/tests/unit -o addopts=""`. Its `conftest.py` holds an autouse guard that fails any test starting a subprocess (`subprocess.Popen`, `os.system`, `os.posix_spawn[p]`, `os.fork`/`forkpty`, `os.execv[e]`), naming the test node ID and the command; `test_guard.py` shows the message. Builders (`facts`, `path_facts`, `plan`) are fixtures in that conftest and build values by hand.
  - Facts value: `verification_facts.py` defines frozen `RequirementFacts` and `PathFacts` (mappings wrapped read-only) and `gather()`, which reads them once per requirement computation from the checkout and the batched baseline blobs: recorded and baseline role, proposed and baseline ownership modes, base and proposed review settings, navigation provider and Graft applicability, pinned source presence, and per planned path whether it is present, changed from the base, executable now or at the base. Configuration validation, manifest validation, review-settings parsing and pinned-source verification stay in `gather()` because they read files.
  - Decisions: `verification_requirements.py` now imports no I/O modules. `requirements(facts, plan)` composes `classify`, `tier_paths`/`path_floor`, `floor_non_prose_documentation`/`prose_reason`, `required_checks`, `reject_missing_checks` and `reject_below_floor`. Plan shape is `plan_shape(plan)` in `verification_snapshot.py`; `validate_plan(root, plan)` runs it and then the path containment checks.
  - Error precedence changed only when several faults occur at once: gathering errors (configuration, manifest, review settings, pinned source) now precede the Graft-disabled and missing-manifest rejections, and the pinned-source comparison runs before the missing-manifest rejection; unsafe-path errors now follow plan-shape errors. Single-fault messages are unchanged.
  - The refactored code passed all 171 tests of the five affected integration files before any test was removed. Each removed rule was then mutated in the source (12 mutations: base role, managed edit, metadata, base-executable, deleted document, maintainer metadata, Graft, project sensitive setting, review settings floor, pinned-source health, below-floor, pinned-source prose); each made at least one unit test fail.
  - Shared preparation: the `pristine` installations fixture (shared build, fresh copy per test) now has the write guard (`unchanged`). The per-test `repo` fixture was not converted: tests use its directory as `tmp_path`, so sharing it is not obviously safe.
  - Removed CLI scenarios, each with equivalent unit tests in `tests/unit/test_verification_requirements.py` or `test_verification_plan.py`:
    - `test_verification_requirements.py`: maintainer source requires suites (3 cases), maintainer configuration needs only project and health checks, maintainer manifest and install state are maintainer source, removing a maintainer target cannot lower requirements.
    - `test_review_tiers.py`: three of four plan-tier rejections; documentation tier needs review settings; documentation settings classify domain docs, not agent policy (5); project sensitive additions; settings cannot weaken starter rules; review settings floor at ordinary; three of four invalid review settings; build and agent scripts (4); consumer starter-sensitive paths (7 × 2 kinds); agent policy is never documentation (3 × 2); consumer README is documentation by default (2); mixed change takes the highest floor (2); required checks unchanged by tier (2); seven of eight maintainer destructive modules; other maintainer source floors at ordinary.
    - `test_prose_assurance.py`: six of seven content-only Markdown edits (requirement facts hold no content); the unsupported-format case of non-prose files; new prose document qualifies; mixed scope requires the suite; configuring documentation cannot lower its own requirements; changed agent instructions need the suite (2).
    - `test_review_settings_followups.py`: executed configuration under broad docs (2); Markdown default covers root and nested prose (3).
  - Wiring kept end to end: one plan-tier rejection and one invalid review setting through `prepare`; below-floor naming and acceptance; base and proposed review settings; one maintainer destructive module; base role switch; dropped baseline ownership; consumer managed edits, deletions and forged digests; missing manifest; deleted, executable and base-executable prose; prose-only checks, publication and the installed launcher; status recomputing the floor.
  - Record schema, snapshot identity, CLI output and review-tier policy are unchanged; `.engineering/template/files.json` distributes the new module and the manifest was regenerated.
- 2026-10-15, review correction: the native Spec review (snapshot `8426d6d1…`, CONCERNS) found that `gather()` read every planned path through `safe_path`, which rejects `.env.template`. The plan contract permits that path and the old code never read unowned paths, so such a plan stopped preparing. `gather()` now reads planned paths through `source_path`, as source inputs do; `test_public_environment_template_can_be_planned` (integration, because the read is the I/O shell) fails without the fix. Standards (PASS) suggested distinct parameter names for path facts in `floor_non_prose_documentation`/`prose_reason`; applied. The first `verify check` of that snapshot failed before running tests: `make check` and `make engineering-test` could not spawn `ruff` in the check copy (the `dev` tools are an optional extra in the repo `.venv`, not on `PATH`); rerun with the repo `.venv/bin` on `PATH`, matching the plan's recorded tools.
- Local measurements, 2026-10-15 (load average about 3–4.5):

  | Measure | Before | After |
  |---|---|---|
  | Unit tier (`tests/unit`) | 0 tests | 136 tests, 0.08 s |
  | Five affected integration files | 171 tests, 201 s | 94 tests (+136 unit), 142 s |
  | Full engineering pytest suite | 593 tests, 887 s (ticket 03) | 652 tests, 794 s |

  The full-suite count rises because 136 cheap unit tests replace 77 CLI cases (counting each parameter). The full suite remains dominated by publication and journey tests that tickets 05–07 address.
- 2026-10-15: published as PR [#55](https://github.com/ZekeT/agentic-starter/pull/55) and merged into `main` as `0e6eea8` (GitHub `mergedAt` 2026-10-15T06:30:14Z).
