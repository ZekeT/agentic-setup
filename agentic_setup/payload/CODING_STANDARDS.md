# Coding standards

Reduce reader effort: prefer clear ownership and local, explicit decisions over
hidden state, unnecessary indirection and speculative helpers. Inspect reuse and
subtraction before adding a mechanism. Simplify demonstrated problems within scope.
Model domain concepts when this removes invalid states or repeated rules; keep
simple code when an abstraction adds little. Validate real trust boundaries.
Separate decisions from I/O where that makes behavior easier to understand.

Fix demonstrated causes; do not hide failures behind retries or silent fallbacks.
Keep comments explaining constraints, contracts and external quirks, plus legal
notices and useful API documentation. Avoid narration. File size and DRY are
judgment aids, not automatic blockers. Plan preparatory simplification separately;
keep red–green cycles focused and review incidental complexity afterward.

Tests assert observable contracts, independently derived expected results,
relevant failures and meaningful side effects. Do not mock away the behavior
under test. Reproduce a bug before fixing it; distinguish that failure from broken
environments/imports. Never weaken assertions, add skips or suppress checks just
to get green. Explain expectation changes required by intended behavior changes.
Use proportionate real CLI/browser/API/library verification, reusing current test
results. Report exactly what ran and what remains unverified.

For this Python installer, use the standard library at runtime, pathlib for bounded
paths and argument lists for subprocesses. Reject symlink traversal and ambiguous
ownership. Preview must not write target files or install dependencies. Never scan
secrets. Native format, lint, type and test checks remain maintainer checks only.

These selected principles follow Pstack's emphasis on subtraction, domain ownership
and verification, and Matt Pocock's TDD workflow. They introduce no second router.
