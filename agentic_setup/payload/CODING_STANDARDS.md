# Coding standards

Make the smallest coherent change that solves the problem. Inspect reuse and
subtraction before adding a mechanism; remove obsolete code and wiring within
scope. Consolidate repeated decisions and avoid duplicate sources of truth,
speculative flexibility and unnecessary synchronized state. File size, line count
and DRY are judgment aids, not automatic blockers.

Reduce reader effort: prefer clear ownership and local, explicit decisions over
hidden state and unnecessary indirection. Interfaces should hide meaningful
complexity; avoid pass-through wrappers that add little value. Evaluate choices
through the experience of users, callers and maintainers. Prefer fewer finished
capabilities, clear feedback and useful failure behavior.

Understand data, invariants and access patterns before writing logic. Establish
only foundations needed by the planned work. Model domain concepts when this
removes invalid states, repeated rules or scattered conditionals; keep simple code
when an abstraction adds little. Use types to distinguish meaningful concepts and
prevent invalid states without unnecessary type complexity or unsafe casts.
Validate external inputs at trust boundaries before treating them as typed data.
Avoid redundant internal validation only where invariants remain guaranteed.
Separate decisions from I/O where that improves clarity and testing.

Consider how a design would look if a new requirement had existed from the start;
use that perspective to simplify within scope. Broader redesign remains separate
work. For coordinated internal API changes, inventory and migrate callers, then
remove obsolete paths in the same change. Preserve compatibility where external
consumers require it. Plan preparatory simplification separately; keep red–green
cycles focused and review incidental complexity afterward.

Fix demonstrated causes; do not hide failures behind unjustified retries, silent
fallbacks or default values. When repeated fixes depend on the same assumption and
fail, state and test that assumption before attempting another fix. For operations
intended to support retries or repeated execution, define behavior after success
and partial failure. Prevent duplicate effects and provide explicit recovery where
safe repetition is impossible. Before coordinating concurrent writers, consider
separate state ownership. When sharing is necessary, enforce coordination through
mechanisms such as locks or atomic operations, not instructions or convention.

Keep comments explaining rationale, constraints, contracts and external quirks,
plus legal notices, required tool directives and useful API documentation. Avoid
narration and repetitive boilerplate in comments and documentation.

Tests assert observable contracts, relevant failures and meaningful side effects.
Derive expected results independently from specifications, worked examples or known
values; do not recompute them with the implementation's logic or write assertions
that pass by construction. Test behavior rather than mirroring implementation
structure, and do not mock away the behavior under test. Reproduce a bug before
fixing it; distinguish that failure from broken environments/imports. Never weaken
assertions, add skips or suppress checks just to get green. Explain expectation
changes required by intended behavior changes. Use proportionate real
CLI/browser/API/library verification, reusing current test results. Report exactly
what ran and what remains unverified.

For this Python installer, use the standard library at runtime, pathlib for bounded
paths and argument lists for subprocesses. Reject symlink traversal and ambiguous
ownership. Preview must not write target files or install dependencies. Never scan
secrets. Native format, lint, type and test checks remain maintainer checks only.

These selected principles follow Pstack's emphasis on subtraction, domain ownership
and verification, and Matt Pocock's TDD workflow. They introduce no second router.
