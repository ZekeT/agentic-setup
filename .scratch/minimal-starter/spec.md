# Minimal starter rebuild

Status: implemented; awaiting human review

The accepted spec and decisions are [product direction](../../docs/product-direction.md).
The CLI and resulting filesystem in disposable repositories are the test seams.
No live application is available or authorized. Delivery follows the original rebuild brief:

1. Preservation and policy replacement: complete; v2.1.0 (alias archive/pre-simplification-2026-10-19)
   at 452d825ae58ad93d3ba66befedaacc30aa20318e.
2. [Minimal transition](issues/01-minimal-transition.md).
3. [Setup and selective updates](issues/02-setup-and-updates.md).
4. [Workflow and final review](issues/03-workflow-and-review.md).

The archive excludes ignored environments, caches, secrets and local runtime state.
Historical v2 tickets and the obsolete Phase 2 idea are preserved at `v2.1.0`
and removed from this checkout. Their removal does not mark unfinished v2 work
as delivered; the v3 product direction supersedes that work.

## Verification and limits

Native `make check` after review corrections: Ruff check and format, mypy, and
14 tests passed (28.71 seconds). The final one-line provenance preservation fix
was reproduced red, then the full migration → application edit → update → repeat
adoption test passed green; Ruff/format/mypy were rerun successfully.

Real upstream smoke: Matt 4588b32, HumanLayer 3c262914 and Pstack 6f131f13 selected
bundles installed into a disposable project and repeated without changes. A real
CLI application ran before/after transition; later application work survived a
revert of the transition commit. Git-routing command walkthrough covered direct
and personal refs, feature comparison, distinct fork/target configuration and an
unknown ref. This is instruction verification, not an autonomous agent simulation.

Independent Matt Standards and Spec reviews identified preservation, skill naming,
discovery, workflow coverage and provenance issues; focused regressions cover fixes.
No additional reviewer tier, evidence service or publication record was introduced.

Limitations: no live application supplied or modified; unfamiliar .factory/.harness
layouts and customized active configuration need bounded manual reconciliation.
Standards discovery is heuristic; native candidates require inspection/execution.
Remote CI protections cannot be changed locally. At the initial implementation
handoff, tags and commits were local; no push, PR, promotion or merge had occurred. Consumer skill upgrades/removals use
reviewed scoped patches rather than automatic merges.

Version naming: the user selected v2.1.0 for preservation and v3.0.0 for the rebuilt starter.

The user subsequently authorized pushing v2.1.0 and v3.0.0 to origin. The descriptive archive alias stays local.
