# Development workflow

Use the project's native commands recorded in docs/agents/checks.md. Read the
project's existing standards. Matt owns planning, implementation, TDD and
Standards/Spec review: /grill-me for unclear scope; /wayfinder for large uncertain
work; /to-spec and /to-tickets for agreed plans; /implement and /tdd for delivery;
/code-review for the final committed diff; /retro for recurring lessons.

Before implementation inspect Git status and docs/agents/git-workflow.md. Do not
switch branches underneath unrelated work or commit on protected integration
branches. Preserve source, tests, specs, task state, ADRs and team conventions.
Never read .env or secret variants; use .env.template for variable names only.

Run relevant native checks and exercise changed behavior at its real surface.
Reuse current results, recheck affected behavior after corrections and report gaps.
Keep red–green cycles focused; plan substantial preparatory refactors separately.
No starter runtime or installation metadata is needed during daily development.

## Agent skills

Use docs/agents/issue-tracker.md and docs/agents/domain.md. Run
/setup-matt-pocock-skills once to fill missing configuration; reuse existing answers.
Keep ticket checkboxes/status current, distinguishing implementation, review,
publication and team delivery. A PR into a personal branch is not team delivery.

Before /pr, follow docs/agents/explanation.md. Matt prepares the description.
Default to manual PR creation. Pushes and agent-created PRs require scoped user
permission; merging, force-pushing and promotion to team integration are separate.

Security review is user-invoked, scoped and read-only: inspect trust boundaries,
authorization, sensitive data, injection, dependencies and destructive effects;
report evidence, plausible impact and remediation. Architectural assessment is
user-invoked and advisory; use Matt's architecture/design skill and distinguish
observed defects from preferences. Do not auto-refactor or file remediation work.
