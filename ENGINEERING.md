# Maintainer guide

The accepted rebuild spec is agentic-starter-directional-change-handover.md.
Consumer instructions live in README.md; do not copy this checkout into an app.

```bash
make setup
make fmt
make check
```

Only maintainers need uv, Ruff, mypy and pytest. Runtime installation uses Python
3.11+ standard library and Git. CI runs these native checks, no evidence platform.
`starter/payload` is the consumer guidance; maintainer tests/history/runtime state
are excluded. `starter/legacy.json` contains exact known historical file/section
hashes for safe removal, not a runtime ownership manifest. The tool never trusts a
target-provided manifest as permission to delete files.

Preservation: local annotated tag archive/pre-simplification-2026-10-19 resolves to
452d825ae58ad93d3ba66befedaacc30aa20318e, including the handover. Previous HEAD was
23a40cca6c066d4edaa4ecc0e13ffd8f860eeae7. Ignored environments, secrets, caches and
local state are excluded and untouched. The tag is local until explicitly pushed.
Rebuild branch: rebuild/minimal-starter. Keep normal history; no legacy source tree.
Tests use the baseline commit (not a remotely published tag) for disposable fixtures.

Removed dependency chain: launcher → old CLI → doctor/ownership/verification/carry/
publication/migration modules; old Make targets, CI evals and manifest generation;
review/ship adapters and extra reviewer agents; OpenSpec migration tools/fixtures;
maintainer tests enforcing those retired features. Protection hooks remain. Old
ADRs and tracker artifacts are historical context and not active workflow policy.
Ignored old state is dormant because no active launcher imports it.

Use public CLI/file outcomes for preservation, stale-preview, mixed ownership and
update tests. Use an injected filesystem failure only to test rollback; do not mock
the installer itself. Actual application migration remains unverified until a user
supplies and authorizes that repository. Simulated policy checks are not actual
agent execution or measured application speed improvements.

Selected upstream revisions and licenses are recorded by `engineering skills`.
Matt 4588b32: setup, TDD, implement, code-review and pr inspected; unchanged bodies.
HumanLayer 3c262914: show-me inspected, optional presentation.
Pstack 6f131f13: reader load, subtraction, root causes, domain/boundary discipline,
behavioral tests, how/why and verification generator inspected. The standards are
project-authored guidance; optional verification skills are copied unchanged with
license. No Pstack router or competing /tdd. Its how/why skills request model-specific
subagents, so they are not installed by default; use evidence-based investigation
without making that model configuration a prerequisite. No overlapping structural
skill is added; Matt's codebase-design is the available architecture aid at this pin.
