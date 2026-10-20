# Preview project-specific resolutions

Status: complete locally; target application and publication pending

- [x] Validate external resolution plans and combine them with adoption proposals.
- [x] Bind preview tokens and save recovery before approved resolution applies.
- [x] Organize local reports and plans by target workspace.
- [x] Verify behavior at CLI/filesystem seams and complete native checks/review.
- [x] Prepare uc3-lane-watch resolutions and a new HTML preview without target writes.

## Validation and handoff

- First resolution CLI test failed because --resolutions did not exist, then passed;
  automatic --html naming likewise has a red-to-green public CLI regression.
- Eleven resolution tests cover actions, exact JSON matching, overrides, wrong targets,
  unsafe paths/inputs, stale hashes/tokens, dirty tracked edits, final-wiring checks,
  recovery failure, guarded apply and automatic report naming/placement.
- `make check`: lint, formatting, mypy and all 76 tests passed.
- Independent Standards and Spec reviews of `38856e6...0b73a3b`: zero findings each.
- Local seven-operation plan: migrations/uc3-lane-watch/resolutions.json; replacement
  content lives beside it under replacements/. These project artifacts are ignored.
- Generated preview-002.html through Agentic Setup: zero conflicts. Captured target
  contents, hooks, installed skills, untracked inventory and Git HEAD/index unchanged.
  No target apply, application commands or Git mutations were performed.
- Observed live target already on chore/adopt-agentic-setup at 1080702, with the
  security reviewer absent. The plan therefore omits a redundant deletion.
- Browser-rendered local preview visually checked. No recovery folder was created;
  snapshots are created only on an explicitly approved apply.
- The actual application has not been migrated or reverified by this task. Review
  the local HTML and regenerate after any project or resolution changes before apply.
