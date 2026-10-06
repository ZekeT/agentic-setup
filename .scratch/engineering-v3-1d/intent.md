**Your observations are largely supported. The biggest shortfall is overlapping review workflows combined with expensive verification—even for bookkeeping changes.** The harness already supports evidence reuse, but several surrounding policies undermine the savings.

I reviewed the implementation, installed Matt skills, CI configuration, and historical verification evidence. No files changed; I did not rerun the full suite.

1. **Duplicate reviews are built into the workflow.**

   Matt’s [`/implement`](/Users/zeke/Workspace/code/self/agentic-starter/.claude/skills/implement/SKILL.md:11) runs the full tests and then `/code-review`. That skill launches Standards and Spec reviewers. The harness separately requires maintainability and behavioral reports, plus security for sensitive changes.

   There is substantial overlap: Standards ↔ maintainability, Spec ↔ behavioral inspection. There is also an ordering mismatch: Matt reviews committed changes through `HEAD`, but `/implement` instructs it to commit **after** reviewing.

   **Recommendation:** use Matt’s Standards/Spec review as the primary semantic review, with an adapter that binds its findings to the actual proposed content and records evidence. Keep deterministic test execution separate. Simply substituting the existing skill would leave uncommitted changes and execution evidence uncovered.

2. **There is no genuinely inexpensive path for small changes.**

   The [requirements implementation](/Users/zeke/Workspace/code/self/agentic-starter/.engineering/engineering/verification_requirements.py:34) always requires `make check`. Documentation reduces reviewer roles, but not checks. Ordinary changes still require two reports, although one session can produce both.

   More significantly, tickets live under `.scratch/`, while the [documentation allowlist](/Users/zeke/Workspace/code/self/agentic-starter/.engineering/config.toml:27) only includes `docs/**/*.md`. A ticket-status update therefore defaults to ordinary review.

   **Recommendation:** separate executable changes, substantive documentation, and mechanical status updates. Review requirements should reflect what changed, not merely that a PR exists.

3. **Behavioral verification has a demonstrated runtime problem.**

   This is more than slow model reasoning. [Ticket 06’s history](/Users/zeke/Workspace/code/self/agentic-starter/.scratch/engineering-v3-1c/issues/06-navigation-upgrade-and-prerequisites.md:61) records two engineering-suite timeouts at 15 minutes. A later successful run took **841.48 seconds for 510 tests**; it also records a user-observed 21m18s run. The response was increasing the timeout to 30 minutes.

   The [runner](/Users/zeke/Workspace/code/self/agentic-starter/.engineering/engineering/verification_snapshot.py:107) buffers command output until completion and records no duration. Checks execute sequentially. `make check` also runs doctor/maintainability, which `make engineering-check` repeats when required.

   **Recommendation:** add per-command timing, visible progress, and pytest slow-test reporting first. Then optimize expensive fixtures and remove duplicate check execution. The evidence establishes suite latency, but does not identify which individual tests dominate it.

4. **`make fmt` does touch engineering files in this checkout.**

   The root [Makefile](/Users/zeke/Workspace/code/self/agentic-starter/Makefile:7) explicitly includes `.engineering/engineering` and `.engineering/tests`. It also runs Ruff autofixes, so changes can extend beyond whitespace.

   However, the [generated application Makefile](/Users/zeke/Workspace/code/self/agentic-starter/.engineering/template/Makefile:7) already limits formatting to application source and tests. This distinction matters: the problem is confirmed in the maintainer checkout, not every generated project.

   **Recommendation:** separate `fmt`, `engineering-fmt`, and an explicit `fmt-all`; support formatting the intended changed files. Keep whole-scope formatting checks non-mutating.

5. **Milestone reviews make sense, with targeted exceptions.**

   Security is already conditional, but the sensitive rules are broad: any Makefile, dependency manifest, workflow, or verification-module edit triggers three separate reviewer sessions—even a comment-only edit.

   I would use this policy:

   | Change | Proposed review |
   |---|---|
   | Mechanical status/link updates | Deterministic validation; no model review |
   | Small ordinary implementation | One semantic review pass plus relevant checks |
   | Security-sensitive behavior | Targeted security review before merge |
   | Milestone/release | Broader architecture, maintainability, and security review |

   Move **broad** maintainability/security assessments to milestones. Retain immediate security review for auth, permissions, dependency execution, untrusted input, and similar boundaries. Milestone-only security would defer consequential findings too long.

6. **Parallel work and bookkeeping still invalidate too much evidence.**

   [Clean-rebase carry-forward](/Users/zeke/Workspace/code/self/agentic-starter/.engineering/engineering/verification_carry.py:13) already exists. Unrelated base advancement can preserve reviews, but checks must run again after a qualifying rebase. Overlapping paths or changed plans prevent carry-forward.

   Shared breakdown files create predictable overlap. Post-publication status edits also change the verified snapshot—the ticket history explicitly documents this happening. Publication additionally [rejects a moved remote base tip](/Users/zeke/Workspace/code/self/agentic-starter/.engineering/engineering/publication.py:82), although refreshing preparation does not necessarily require repeating semantic review.

   **Recommendation:** batch shared tracking updates after delivery, keep implementation branches focused, and distinguish “refresh recorded base” from “rebase and re-review.” Moving-base errors should explain which evidence actually became stale.

7. **A cheaper `/ship` and `/ssync` are feasible, but need explicit implementation.**

   The current [`/ship`](/Users/zeke/Workspace/code/self/agentic-starter/.claude/commands/ship.md) has no model routing. Its job is mostly running the existing publication machinery, making it a good candidate for a narrowly scoped shipping agent.

   For Codex, model and reasoning settings can be assigned to a custom subagent; **GPT‑6.1 Sol with low reasoning** is a reasonable starting configuration for this bounded task. Merely mentioning a model in command prose does not guarantee routing. [Official configuration guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents). I have not verified Sonnet 5.5 availability or its runtime configuration.

   `/ssync` should:
   - Observe actual PR and merge state.
   - Update only status fields, delivery links, and evidence pointers.
   - Create or update one bookkeeping PR; do nothing when already synchronized.
   - Use deterministic validation without model review.
   - Avoid triggering another sync PR for its own bookkeeping PR.

   The exemption must depend on the **actual diff**, not a `chore:` title. Changes to acceptance criteria, specs, policy, or code should follow normal review. Automatic execution after merge also needs an event hook or an explicit later invocation.

8. **Matt’s research workflow is installed, but durable handoff conventions are thin.**

   The installed [`research` skill](/Users/zeke/Workspace/code/self/agentic-starter/.claude/skills/research/SKILL.md) already specifies primary sources and a saved Markdown report. The harness has domain and ADR locations, but no equally explicit research-note convention.

   **Recommendation:** keep task research beside its spec, with the question, sources, findings, uncertainties, and decision implications. Link it from the spec; promote lasting conclusions into domain docs or ADRs. This needs a small convention, not another workflow engine.

9. **Graphify is not currently wired into active navigation.**

   The references I found are [legacy migration handling](/Users/zeke/Workspace/code/self/agentic-starter/.engineering/engineering/migrate/legacy.py:220) and its regression test. They preserve the old cache ignore rule during migration. Those references serve compatibility and should not be deleted just because Graphify was removed.

**My priority order:** unify semantic review, add the mechanical-status exemption, instrument and optimize verification, separate formatting scopes, then implement model-routed shipping and `/ssync`. Those changes address the largest demonstrated sources of latency and token consumption.