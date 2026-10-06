# Choose portable shipping-model routing and fallback

Type: grilling
Status: resolved
Assignee: Codex session for zeke
Blocked by: 06
Parent: [Engineering v3-1d decision map](../map.md)

## Question

Given the runtime-support research, what configurable shipping-model routing should Claude Code and Codex expose, with what concrete defaults and explicitly reported fallback to the current session?

Choose runtime-specific configuration and dispatch contracts, capability/availability handling, fallback reporting, handoff inputs and results, and boundaries of the narrow shipping agent. Preserve existing publication authorization and evidence requirements; routing must not rerun valid checks or imply merge authority. Distinguish documented capability from account/session availability and avoid unsupported model identifiers.

## Comments

### Routing decision preparation

Loaded the resolved runtime research and checked current official subagent documentation. Codex exposes model and reasoning settings; Claude exposes model aliases/full IDs and effort settings. This session's Codex spawn schema advertises `gpt-6.1-sol` with `low`, while full-history forks inherit settings and cannot override them. Account-specific access and successful alternate-model execution remain untested.

Sources: https://learn.chatgpt.com/docs/agent-configuration/subagents and https://code.claude.com/docs/en/sub-agents . These establish controls, not cost savings, account entitlement, or a guarantee that requested and effective models always match.

Pending choices: dedicated shipping-agent defaults and per-runtime override; reported current-session fallback with serialized recovery; minimal handoff and shipping-only responsibilities. All proposals apply to the standalone harness shipping flow, not Matt skill orchestration. No configuration changes, alternate-model probes, or publication were performed.

## Answer

The user agreed to all three routing recommendations.

- Default dedicated shipping agents to `gpt-6.1-sol` with low reasoning in Codex and `sonnet` with low effort in Claude Code. Make each runtime's shipping-agent settings configurable without changing other agents. These are starting choices; no account entitlement, successful alternate-model invocation, or measured savings is claimed.
- If the preferred model cannot run, report why and continue in the current session within existing authorization. If another publisher has started, ensure it has stopped and reconcile completed Git/provider actions before resuming. Never run concurrent publishers or bypass a failed gate by changing models.
- Hand off pointers to accepted scope, branch, current evidence, target, and authorization rather than the implementation conversation. Validate these inputs, execute authorized shipping steps, and return the actual PR/MR URL or precise partial progress. No application fixes, reinterpretation of acceptance, repeated valid suites, or merge authority.
- Report requested settings and the actual model when observable; otherwise state the uncertainty. Respect runtime dispatch restrictions rather than pretending an override took effect.
- Routing belongs to the standalone harness shipping flow. Matt's skills remain unchanged and unwrapped.

### PR-skill boundary observation

The user asked whether this overlaps with Matt's `/pr`. Installed `pr/SKILL.md` defines PR-body presentation (Summary, Evidence, Merge Danger), not Git publication, model dispatch, verification gates, or retries. The existing harness `/ship` owns accepted-scope publication and evidence freshness. Potential duplication is limited to PR-writing guidance. Reusing the native `/pr` for body composition is a recommendation, not authorization to modify or wrap it or to add another publication workflow.

### Subsequent accepted PR-body handoff

The user subsequently approved consuming the native `/pr` description in `/ship` while retaining `.github/pull_request_template.md`. Native `/pr` composes the description; the harness captures that prepared body and publishes it under existing evidence and authorization gates, without a second body generator or an upstream skill wrapper. This boundary was implemented separately and published as [publish prepared PR descriptions](https://github.com/ZekeT/agentic-starter/pull/46). Publication was observed; merge is not recorded here. Shipping-model routing and the other target-design changes remain separate.
