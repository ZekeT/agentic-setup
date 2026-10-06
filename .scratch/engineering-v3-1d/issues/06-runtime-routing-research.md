# Establish supported runtime shipping-model controls

Type: research
Status: resolved
Assignee: runtime_research (Codex background research agent for zeke)
Parent: [Engineering v3-1d decision map](../map.md)

## Question

What model-selection and reasoning controls do the available Claude Code and Codex runtimes actually expose for a narrowly scoped shipping subagent, and what availability/fallback limits can be established from local configuration and current official primary sources?

Read local runtime adapters and safe configuration without reading secrets, then verify relevant current official documentation. Distinguish configurable model identifiers from models confirmed available in this session/account, dispatch-time controls from prose-only requests, and failures that can be detected versus unknown availability. Do not assume earlier suggested model names exist or are supported.

Record dated sources, findings, uncertainties, and implications in `research/runtime-shipping-models.md` beside the future spec. Capture findings on a throwaway `research/engineering-v3-1d-runtime-routing` branch in an isolated worktree without switching the main checkout or committing unrelated user work. Research may establish facts, not choose defaults or authorize shipping. Link the report and branch context in the resolution.

## Answer

Resolved 2026-10-05. [Runtime shipping-model controls](../research/runtime-shipping-models.md) records local versions/settings, current official documentation, dispatch controls, and availability limits. Both runtimes expose concrete model/effort selection; this Codex session restricts overrides on full-history forks, while Claude documents model substitution and fallback. Configured or advertised models are not proof of successful account access. No alternate-model invocation was tested, and no routing default or fallback policy was chosen.

Research was captured uncommitted in `/private/tmp/engineering-v3-1d-runtime-routing` on `research/engineering-v3-1d-runtime-routing`, based at `4c99de9595a78b8d91970fe06d7ea64ba50ace41`, then copied identically into the main checkout. The branch alone does not preserve the uncommitted report. Main remained on `main`; no commit or publication occurred.
