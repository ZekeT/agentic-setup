# Engineering test standard

Maintainer-only coding standard for tests of the Engineering harness itself
(`.engineering/engineering/` and `.engineering/tests/`). It is not distributed:
consumer projects follow the distributed testing guide and the pinned upstream
`/tdd` skill. Standards review applies it to harness changes. The reasons are in
[ADR 0004](../docs/adr/0004-facts-and-pure-decisions-for-engineering-tests.md).

## Rules

- **Put pure decision logic behind the family's decision seam and unit test it
  there.** A migrated family's shell gathers Git and filesystem facts into a
  plain data value, and decision functions take that value and return a
  classification, floor, outcome or validation error. Verification requirements
  are migrated: `verification_facts.py` gathers, `verification_requirements.py`
  decides, and plan shape is checked by `plan_shape`. Verification evidence and
  publication follow (tickets 05–06 of `engineering-test-speed`). New rules go
  into those functions, with unit tests in `.engineering/tests/unit/` that assert
  the observable decision for a given facts value, not which helper ran or how
  many Git calls happened. Unit-tier builders live in that directory's
  `conftest.py` and never read the real repository. Run the unit tier alone with
  `uv run pytest .engineering/tests/unit -o addopts=""`.
- **Keep CLI-level tests for real-boundary contracts:** non-mutation of the
  working tree and index, hooks, retries and locks, publication (including the
  local Git HTTP servers), wiring from gathered facts to decisions and writes,
  and the greenfield journey.
- **A new CLI-level test that only exercises a pure rule is a standards
  violation.** Move the rule behind the decision seam and test it there. A
  family whose decisions are not yet separated is not an exemption: add the new
  rule as a function over plain data and unit test it.
- **Unit tests start no subprocesses** (Git, the CLI, `make`); the unit tier's
  guard fails any test that does, naming it and the attempted command. Do not
  replace a real-boundary test with mocked Git.
- **Move coverage, do not drop it.** Remove a CLI scenario only when an
  equivalent unit test exists and fails if the rule breaks, and note the removal
  in the ticket.
