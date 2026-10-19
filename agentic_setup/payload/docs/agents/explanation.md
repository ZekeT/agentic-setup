# Explain before preparing a PR

Before every Matt /pr invocation, give the user a compact show-me briefing:
what changes for them, one concrete example through the implementation, a useful
sketch or diagram, why the design fits, tradeoffs, and what verification proved.
Explain ownership and runtime flow. Cite historical reasons from commits/ADRs;
label inference and unknowns. Use deeper how/why investigation when needed.
Reuse a recent explanation only while it still covers the final changes.

For example, an export change might show:

```text
Export click → permission check → selected rows → CSV encoder → download
```

Explain which rows a particular user gets, where access is enforced and what the
CLI/browser/API test actually observed. Boxes alone are not an explanation.
HumanLayer's show-me skill can supply richer presentation. Its absence does not
block a concise Markdown/Mermaid briefing. Keep visuals proportionate to the change.
