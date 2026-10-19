# Check upstream skill revisions

Status: complete locally; publication pending

- [x] Add explicit read-only CLI check and revision reporting.
- [x] Cover ancestry, incomplete checks, metadata compatibility and preservation.
- [x] Document behavior and verify real upstream operation.
- [x] Pass native checks and Standards/Spec review.

## Validation

- First CLI regression failed because `skills check` did not exist, then passed after implementation.
- Eight focused CLI tests passed, including unchanged target/Git snapshots, ancestry,
  partial failures, bundle filtering, legacy records and unsafe metadata handling.
- `make check`: lint, format, mypy and all 60 tests passed.
- Real HumanLayer show-me install/check in a disposable target reported current at
  `653b6411c1f70c275a18e37673b042ff99f67ceb`; full target snapshot unchanged.
- Independent Standards and Spec reviews of `3e26669...b125095`: zero findings each.
- No real application migration, upstream skill execution or remote publication performed.
