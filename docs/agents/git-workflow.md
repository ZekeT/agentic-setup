# Git workflow

Before work, inspect current branch, status, remotes and existing team conventions.
Record the team's integration branch, branch/commit naming, push remote and target
repository here. New teams may choose develop and Conventional Commits; do not
create or assume these branches in an existing repository. Unresolved configuration
is a question to the user, never a silent fallback to main.

Personal overrides allowed: branch prefix, work base, immediate PR base and push
remote. Target repository changes require explicit team/task authorization.
Read shared defaults here first, then `git config --local --get agent.branchPrefix`,
`agent.workBase`, `agent.prBase`, `agent.pushRemote` and `agent.targetRepository`.
These are starter conventions, not Git enforcement. Task instructions take
precedence where authorized. Never write machine-global settings.

Keep these distinct: team integration branch; feature work base; review comparison
base (normally the immediate intended PR target); immediate PR target; push remote;
and PR target repository. Confirm refs with `git rev-parse --verify '<ref>^{commit}'`
and remote names with `git remote`. Missing or invalid refs require resolution.

| Choice | Direct example | Personal integration example |
| --- | --- | --- |
| Team integration | develop | develop |
| Work base | origin/develop | origin/zek/integration |
| Feature name | feat/123-export | zek/feat/123-export |
| Review base | origin/develop | origin/zek/integration |
| Immediate PR target | develop | zek/integration |
| Promotion | Feature PR integrates | Separate authorized PR to develop |

For a fork, push remote might be origin while target repository belongs to upstream.
Display source branch, comparison ref, target branch and repository before PR
preparation. Do not infer that push and target repositories are identical.

Use team naming, otherwise meaningful names such as feat/export and
`feat(export): add CSV download`. Default to description preparation and manual PR
creation. Authorization to create a PR to a personal branch stops there: no team
issue closure, promotion, merge or force-push as a side effect.

For this rebuild only: baseline is archive/pre-simplification-2026-10-19;
work branch is rebuild/minimal-starter. Local scoped commits are authorized.
No push, remote PR, promotion or merge is authorized.
