# Project instructions

Read README.md for the consumer workflow and CONTRIBUTING.md for maintainer setup.
Read the relevant decisions in [product direction](docs/product-direction.md)
when planning features. Feature specs and delivery status live in `.scratch/`.

Use Matt Pocock's planning, implementation, TDD and Standards/Spec review skills.
The original rebuild uses the product direction’s delivery order and test seams:
the external CLI and filesystem outcomes in disposable repositories. Subsequent
features define their own bounded scope while respecting that product direction.
Keep upstream skill bodies unchanged. Checkpoint the final intended changes before
committed-diff review; review any later corrections against the same scope.

Follow CODING_STANDARDS.md. Run native checks with `make check`; format with
`make fmt`. Verify meaningful CLI journeys using isolated projects. Report actual
results and gaps. There is no verification ledger, reviewer tier, ownership gate,
publication service, or mandatory extra reviewer. Security and architectural
assessment are user-invoked, advisory work.

Read source before changing it. Preserve application content and unrelated work.
For existing-project migration, follow docs/migration-agent-guide.md.
For live target projects, preview first and refine this setup tool until the user
approves the proposed transition. Only Agentic Setup commands may modify a live
target; never directly edit/delete its files, switch its branches, commit there or
run target-mutating commands as a workaround. Disposable test fixtures are separate.
Never read .env or its secret variants; .env.template documents names only.
Retain useful secret protections. Do not bypass failed native checks.
Do not push, create PRs, merge or force-push without scoped authorization.

## Agent skills

Use docs/agents/issue-tracker.md and docs/agents/domain.md. Preserve existing
tracker formats and statuses. Read docs/agents/git-workflow.md before branching
or preparing a PR. Before Matt's /pr, explain the final behavior, a concrete flow,
a useful sketch, design tradeoffs, and verification. Describe historical rationale
only where evidence exists. Local commits are authorized for this rebuild.
