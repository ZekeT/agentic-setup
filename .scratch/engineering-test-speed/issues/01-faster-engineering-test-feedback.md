# 01: Make engineering test feedback fast enough for routine harness work

**What to build:** Harness developers get quick, trustworthy feedback from the engineering test suite during routine work, and the authoritative full run completes with comfortable headroom under the `verify check` command timeout.

**Blocked by:** None.

**Status:** broken down — see [spec](../spec.md) and tickets 02–07 below; tickets 02 and 03 merged; ticket 04 implemented, verification pending

## Problem

`make engineering-test` runs on nearly every harness change and inside every `verify check` of a harness change. It is almost entirely integration and end-to-end coverage: tests drive the public CLI in disposable Git repositories, each `verify prepare`/`check` copies the repository and spawns processes, and template builds, clones, fake-toolchain setup and local Git HTTP servers recur. There is no unit tier (`.engineering/tests/unit/` is empty) and no parallel runner, so ~570 tests run serially. A full run took about 20 minutes on 2026-10-10 (snapshot `7547c010…`), and later runs exceeded the 1800-second `verify check` command timeout, blocking verification entirely.

## Candidate directions (to decide in triage)

- Profile the suite locally (`--durations`) to find where time actually goes before choosing changes. Profiling is a local investigation, not a shipped diagnostic.
- Run tests in parallel (for example `pytest-xdist`); tests already isolate state in temporary directories. Adds a dependency, so it takes the sensitive review tier.
- Add a fast in-process unit tier for pure logic (requirement classification, tier floors, report validation) for development feedback, keeping integration tests authoritative.
- Extend the immutable-preparation pattern from ticket 10 of `engineering-v3-1d-delivery` (shared build, fresh writable copy per test, write guard) to fully prepared verification repositories.
- Revisit whether the `verify check` command timeout and suite size are proportionate.

## Constraints

- Keep observable-execution coverage where the contract depends on the real command boundary (non-mutation, hooks, retries, publication). Do not replace those guarantees with mocks or drop meaningful scenarios merely to save time.
- No numeric speedup promises or benchmark tooling in the shipped harness.

## Comments

Raised by the user on 2026-10-10 during ticket 10 of `engineering-v3-1d-delivery`: the suite runs very frequently during harness development and is slowing work down. Not yet triaged, specified or scheduled at the time (superseded: see Triage outcome and Breakdown below).

Local profile, 2026-10-10 (566 tests, serial, machine under unrelated desktop load of about 5 load average): 31 minutes in total, with no hang (5-minute per-test stack dump never fired). The slowest tests are the greenfield journey (94 s) and publication-family tests (about 15–31 s each: recovery, providers, body, native publication), then verification tests (about 15–20 s). Their cost comes from chained public-CLI calls (`complete()` runs prepare, check, and one record per role before publication runs). The same test measured identically on `main` and on the ticket 10 branch, so this is pre-existing cost, not a ticket 10 regression. Under that load the suite exceeds the 1800-second `verify check` command timeout. On a quieter machine the same suite took about 20 minutes.

## Triage outcome (2026-10-14, grilling session with the user)

**Root cause (measured).** The tests are slow because the tool is slow and the logic is untestable in isolation, not only because of serial execution:

- One ordinary verification test on a three-file repository took 9 s: 3 × `verify status` 2.5 s, 3 × `record` 2.5 s, 3 × `prepare` 2.4 s, 1 × `check` 1.3 s, test-side Git 0.3 s.
- A single `verify status` took 0.83 s, of which 0.78 s was 47 separate Git subprocesses (~15 ms each), mostly from repeated baseline and object reads. Python start-up is ~0.05 s, so running the CLI in-process would barely help.
- Decisions (status, staleness, tier floors, report validation, requirement classification) are interleaved with Git I/O, so the only available seam is a real repository driven through the CLI. Each new rule therefore added another CLI-level scenario.

**Decisions.**

1. **Git batching first, as its own ticket.** Reduce Git subprocesses in the verification modules (for example `git cat-file --batch`, single tree listings) without changing behavior. Benefits real use and the existing suite.
2. **Functional core, imperative shell.** Gather Git facts once, then pass plain data to pure decision functions. Move most scenarios to a unit tier in `.engineering/tests/unit/`. Keep end-to-end tests only for real-boundary contracts: non-mutation, hooks, retries, publication, and one greenfield journey. Do this incrementally, one module family per ticket, verification first, then publication.
3. **Target:** unit tests in seconds during development; the full authoritative suite inside `verify check` in about 1–2 minutes once 1 and 2 land. Measured locally and recorded in tickets; no numeric promises or benchmark tooling in the shipped harness. Parallel execution (`pytest-xdist`, sensitive tier) remains optional extra headroom, decided after 1 and 2.
4. **Keep the 1800 s `verify check` timeout** unchanged.
5. **Durable guidance so new work follows the approach:** an ADR (`docs/adr/0004-…`) recording why; a short testing standard (superseded: a maintainer-only location, see the note below and the spec) so fresh Standards review flags new CLI-level tests for pure logic; no extra feature-local instruction file unless that proves insufficient.
6. **Unit-tier guard:** `tests/unit/` fails any test that starts a subprocess (Git, CLI, make), mirroring ticket 10's write guard.
7. **Scope:** starter-only. Consumer testing style stays with the pinned upstream `/tdd` skill.

**Sequencing constraint.** PR #50 (ticket 02 of `engineering-v3-1d-delivery`) changes `verification_requirements.py` and verification tests. Code tickets here overlap it, so implement them after PR #50 merges, on a fresh branch from updated `main`. PR #50 merged on 2026-10-14 (`6a5b40c`), so this constraint is met.


Specified 2026-10-14 in [spec.md](../spec.md). Confirmed with the user: seams are a gathered facts value plus pure decision functions per module family; the testing standard lives in a maintainer-only (non-distributed) location, because the distributed coding standards and testing guide ship to consumers.

## Breakdown

Broken down 2026-10-14 via `/to-tickets`; breakdown approved by the user. Work the frontier: a ticket can start when all its blockers are done. Ticket 02 merged as PR [#53](https://github.com/ZekeT/agentic-starter/pull/53) (`881b8e9`); ticket 03 merged as PR [#54](https://github.com/ZekeT/agentic-starter/pull/54) (`210a983`); ticket 04 is the frontier.

The spec and tickets were published as PR [#51](https://github.com/ZekeT/agentic-starter/pull/51), merged into `main` as `3f4e617` (local time 2026-10-15 00:31 +0800; GitHub `mergedAt` 2026-10-14T16:31:56Z). The source-fetch maintenance fix that had to land before ticket 03 merged as PR [#52](https://github.com/ZekeT/agentic-starter/pull/52).

| Ticket | Blocked by | Review tier |
|---|---|---|
| [02: ADR 0004 and maintainer testing standard](02-adr-and-maintainer-testing-standard.md) | None | ordinary |
| [03: Batched Git reads in the verification modules](03-batched-git-reads-in-verification.md) | PR #50 merged (met 2026-10-14) | sensitive |
| [04: Unit tier, subprocess guard and pure verification requirement decisions](04-unit-tier-guard-and-requirement-decisions.md) | 02, 03 | sensitive |
| [05: Pure verification evidence decisions](05-pure-verification-evidence-decisions.md) | 04 | sensitive |
| [06: Pure publication decisions](06-pure-publication-decisions.md) | 05 | sensitive |
| [07: Measure the suite and decide on parallel execution](07-measure-and-decide-parallel-execution.md) | 06 | ordinary |

The spec's option to combine the unit tier and guard with the first migration was taken (ticket 04). The verification family is split into requirement decisions (04) and evidence decisions (05) to keep reviews small. Code tickets 03–06 are serialized because they touch the same modules.
