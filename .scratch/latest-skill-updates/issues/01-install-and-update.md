# Latest-on-request skill management

Status: complete locally; publication pending

- [x] Resolve latest/ref sources and retain explicit offline checkout support.
- [x] Record file ownership and preview/apply safe skill updates.
- [x] Support explicit verification of older commit-only records.
- [x] Cover preservation, conflicts and repeat application with CLI tests.
- [x] Document behavior, validate real upstream and run native checks/review.

Validation:
- `make check`: lint, formatting, typing and all 52 tests passed.
- Standards and Spec reviews passed after the upstream deletion ownership fix.
- Forged ownership and unavailable historical revisions have CLI regression coverage.
- Real upstream install, exact revision replay and unchanged update checks passed in disposable targets:
  - HumanLayer show-me: `653b6411c1f70c275a18e37673b042ff99f67ceb`.
  - Matt Pocock: `49dd158d1076134a641b33efb035946536778336`.
  - pstack verification: `6f131f137de64fdaf928278c0fd9ecec520ccbee`.
- Upstream skill instructions/scripts were not executed during these checks.
