> Historical ADR: superseded for the rebuilt starter by the directional-change handover.
> Retained for rationale; not active workflow policy.

# Facts and pure decisions for engineering tests

Status: accepted design (2026-10-14); implementation pending (tickets 03–07 of `engineering-test-speed`).

`make engineering-test` runs on nearly every harness change and inside every `verify check` of one. A serial run of about 570 tests took about 20 minutes on a quiet machine and 31 minutes under load, so it reached the unchanged 1800-second `verify check` command timeout and blocked verification.

Measurement located the cost in the tool, not only in the test runner. One ordinary verification test on a three-file repository took about 9 s, almost all of it in repeated `verify status`, `record`, `prepare` and `check` calls. A single `verify status` took 0.83 s, of which 0.78 s was 47 separate Git subprocesses (about 15 ms each), mostly repeated baseline and object reads. Python start-up was about 0.05 s, so running the CLI in-process would barely help. The structural cause is that verification and publication rules (status, staleness, tier floors, report validation, requirement classification) are interleaved with Git I/O. The only available seam was a real repository driven through the CLI, so each new rule added another slow CLI-level scenario.

We batch Git reads first, then separate facts from decisions:

1. **Git batching** reduces the subprocess count in the verification modules (for example one `git cat-file --batch` or one tree listing instead of per-path calls) without changing behavior. It speeds up real use and the existing suite, which stays green unchanged as its safety net.
2. **A facts value plus pure decisions**, one module family per ticket, verification first, then publication. The shell gathers Git facts once into a plain data value; pure functions take that value and return the decision. Unit tests in `.engineering/tests/unit/` cover each rule at that seam, and a guard fails any unit test that starts a subprocess (Git, the CLI, `make`), mirroring the existing write guard for shared fixtures.
3. **End-to-end tests remain for real-boundary contracts:** non-mutation of the user's working tree and index; hooks; retries and locks; publication, including the local Git HTTP servers; a small set of wiring tests per migrated family showing gathered facts reach the decisions and decisions drive the writes; and one greenfield journey. A CLI scenario is removed only when an equivalent unit test exists and fails if the rule breaks.

The 1800-second `verify check` command timeout is unchanged. Parallel test execution is deferred until the suite is measured after batching and migration; adopting it would add a dependency and take its own sensitive-tier ticket. The working target, recorded in tickets rather than promised by the harness, is unit tests in seconds and the authoritative suite in about one to two minutes.

New work follows this through the [maintainer engineering test standard](../../docs-maintainer/engineering-testing-standard.md), which Standards review applies. It is maintainer-only: consumer projects keep the distributed testing guide and the pinned upstream `/tdd` skill.

## Considered options

Recorded so the decision is not reopened in a loop:

- **Parallelism first** (for example `pytest-xdist`): rejected as the first step. It divides wall time without removing the 47 Git calls per status or the untestable interleaving, adds a dependency, and every new rule would still need a CLI scenario. It stays an option after measurement.
- **Raising the timeout:** rejected. It hides the cost rather than removing it, and slow feedback during development remains.
- **Mocking Git in unit tests:** rejected. Mocks encode assumptions about Git output and would replace guarantees that depend on the real command boundary. Pure decisions over a gathered facts value need no mocks, and real Git stays in the end-to-end tier.
- **Dropping scenarios:** rejected. Coverage moves to the unit tier with an equivalent failing test; it is not deleted to save time.
- **Running the CLI in-process:** rejected as not worth it at about 0.05 s per call.
