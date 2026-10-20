# Export before/after HTML previews

Status: complete locally; publication pending

- [x] Render clear summary, conflicts, preserved notes and before/after comparisons.
- [x] Add safe preview-only HTML output to the planning commands.
- [x] Verify CLI behavior, preservation and bounded escaped content.
- [x] Generate the requested real-target report without target writes.
- [x] Complete native checks and Standards/Spec review.

## Validation

- First CLI test failed because --html was unavailable, then passed after implementation.
- Five public CLI tests cover before/after rendering, stable token, target preservation,
  conflicted plans, escaped content, existing/unsafe output, preview-only mode,
  binary/large contents, no-change plans and scoped guidance/skill commands.
- `make check`: lint, formatting, mypy and all 65 tests passed.
- Generated `/tmp/uc3-adoption-preview.html` through Agentic Setup only. Both existing
  conflicts remain visible; checked target file contents, untracked inventory and
  Git HEAD/index were unchanged. No apply or target mutation commands were run.
- Headless Chrome rendered the report summary and conflict cards. An extracted
  expanded Makefile comparison was also visually checked; fragment scrolling in
  headless screenshots produced a blank capture, so it was not used as evidence.
- Independent Standards and Spec reviews of `c0c68cf...c383cea`: zero findings each.
- No target migration, remote push or PR publication performed.
