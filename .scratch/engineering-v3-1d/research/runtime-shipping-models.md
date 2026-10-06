# Runtime shipping-model controls

Research date: 2026-10-05 (Asia/Singapore).
Question: which model and reasoning controls can a narrowly scoped shipping subagent actually use?

## Capture and scope

Created in isolated worktree `/private/tmp/engineering-v3-1d-runtime-routing`, branch `research/engineering-v3-1d-runtime-routing`, starting at `4c99de9595a78b8d91970fe06d7ea64ba50ace41`. The same report is copied into the main checkout as the linked planning artifact. It is uncommitted in both locations; the branch alone does not contain the report. Main remained on `main`. No shipping, model invocation probe, configuration mutation, or commit occurred.

## Observed local facts

Read-only CLI version commands reported Codex `0.159.0-alpha.12.1` and Claude Code `2.1.289`. Allowlisted settings inspection found user Codex `model = "gpt-6-astra"`, `model_reasoning_effort = "low"`; user Claude settings contain `model: sonnet`, `effortLevel: high`. Repository Claude settings and local settings contain none of the inspected model, effort, available-model or fallback fields. These are configuration observations, not effective-session or entitlement proof. No environment variables, credentials, or `.env` files were inspected.

The repository has no `.codex/` directory. Its [Claude reviewer definitions](../../../.claude/agents/) specify no model or effort, and its [shipping command](../../../.claude/commands/ship.md) does not dispatch a dedicated model-selected shipper. Existing publication policy still governs authorization and proof.

The actual collaboration tool exposed in this research session accepts `model` and `reasoning_effort` at spawn, but full-history forks inherit the parent's settings and reject overrides. Overrides require `fork_turns: none` or a positive history count and applicable user/skill authorization. The exposed model menu lists `gpt-6.1-sol`, `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna`, and `gpt-5.6-sol`; supported effort menus vary. This confirms an advertised dispatch surface, not successful invocation of every listed model. This research agent inherited its parent; no alternate model was tested. Source: session `collaboration.spawn_agent` schema and developer runtime instructions, observed on the research date.

## Official OpenAI documentation

Codex documents explicit spawn values, `[agents]` defaults, and custom agent `model` / `model_reasoning_effort` settings. Unspecified settings inherit; selecting a model without an effort can use that model's default. Custom agent files override resolved spawn/default values. Supported efforts and model access depend on the selected model and account. Thus a prompt requesting a model can guide dispatch, but prose alone is not evidence that dispatch selected it. The current client tool's fork restriction remains an additional concrete boundary. [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) (opened 2026-10-05).

## Official Claude Code documentation

Subagent definitions accept aliases, full model IDs, or `inherit`; per-invocation model selection outranks definition frontmatter, then the subagent-model environment default, then inheritance. A force override can change that behavior. `effort` frontmatter overrides session effort; extended thinking otherwise inherits. Current docs describe allowlist substitution, warnings, and `/tasks` model visibility. These documented version thresholds precede the observed installed version, but no live Claude subagent was launched to verify behavior. [Create custom subagents](https://code.claude.com/docs/en/sub-agents) (opened 2026-10-05).

Claude also supports configured availability fallback chains, including for subagents. It reports switches; authentication, billing, rate-limit, request-size and transport failures do not trigger those chains. The chain is not startup-validated, so configured entries do not prove access. Other documented automatic fallback behavior means requested and executed models can differ. [Model configuration](https://code.claude.com/docs/en/model-config) (opened 2026-10-05).

## Decision implications and unresolved facts

There are concrete routing controls in both runtimes; a shared policy can describe intent while adapters express actual controls. This is an inference from the sources, not an implemented interface or selected default.

No account-wide model inventory, managed-policy override, effective environment override, successful alternate-model request, or Codex automatic fallback guarantee was established. Detectable evidence includes dispatch rejection, request errors, and Claude's documented substitution/switch notices and task model display; absence of an error is not proof of the exact backend model. A future adapter must distinguish requested settings, observable execution, and unknowns. Routing defaults, fallback permission, and behavior when settings cannot be enforced remain for the human decision ticket. Existing publication failure recovery must not be conflated with model fallback.
