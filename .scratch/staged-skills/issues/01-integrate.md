# Integrate external skills installer

Status: complete

- [x] Staged preview and frozen offline apply
- [x] External lock/alias inspection and read-only check
- [x] Public CLI tests and real installer journey
- [x] Documentation, committed-diff Standards/Spec review
- [x] UC3 executable preview, no live apply

Validation: `make check` passed at 672edf2: Ruff, formatting, mypy (15 source
files), and 90 tests. Standards and Spec committed-diff reviews against f68b759
have no remaining findings through 672edf2. Regression tests reproduced and fixed
local-source symlink traversal and record-only freshness drift.

Real skills@1.7.2 installation ran in a disposable staging workspace. Frozen apply
succeeded with Node/npm absent from PATH after changing the upstream fixture;
reviewed bytes, aliases, lock data and unchanged app content were verified.

UC3 preview: `migrations/uc3-lane-watch/preview-007.html`, saved plan
`skills-001.json`, token
`ab33c4dd2abee62bdf2feed03c05ddc448472ef4409de6e723b1b3d192c636f3`.
The 21-skill saved snapshot, guards and Git baseline were revalidated read-only
against UC3 after corrections. No live apply, push, PR or publication performed.
User must review the HTML before running the frozen apply command.
