# 02: Give prose changes appropriate assurance

**What to build:** A prose-only change receives lightweight independent documentation review and relevant checks, while consequential documentation still receives assurance appropriate to its behavior.

**Blocked by:** [01: Use native review evidence through publication](01-native-review-evidence.md).

**Status:** file-type classification (user decision 2026-10-14) implemented on `feat/prose-assurance`; fresh independent verification pending

**Specification:** [Engineering v3-1d](../../engineering-v3-1d/spec.md)

- [x] Public verification classifies actual changed content alongside configured documentation locations, ownership, and risk constraints; a Markdown suffix, title, or assertion is insufficient.
- [x] Prose-only changes require one independent documentation review and relevant documentation checks without an unrelated application suite.
- [x] Policy, agent instructions, requirements, and changed executable examples receive stricter review and checks appropriate to their impact. An unchanged executable example elsewhere does not disqualify a prose-only correction.
- [x] Mixed, unsupported, or uncertain changes take the stricter substantive route; attempts to lower their own requirements through configuration changes do not bypass existing safeguards.
- [x] A public-command journey verifies a prose correction through publication, rejects missing documentation proof, and contrasts it with changed instructions and mixed code/documentation scope.
- [x] Ship the classification contract, user-facing explanations, consumer distribution changes, and meaningful regression tests together. Mechanical bookkeeping and comment exemptions are not enabled by this slice.

## Comments

Approved as part of the 12-ticket breakdown. No implementation, verification, acceptance, or delivery is recorded yet. Follow the specification and current repository policy; update this ticket and the breakdown with actual evidence at handoff.

Implemented on `feat/prose-assurance`. The checked criteria describe implemented behavior and regression coverage, not independent verification, human acceptance or publication.

- Design decision (user, 2026-10-11): the relevant documentation check is a new starter-owned `./engineering docs-check <paths>` (UTF-8 plus local link and heading-anchor resolution), required with the plan's sorted paths. It ships through the managed CLI, so consumer Makefiles and check recipes are unchanged.
- Classification: `verification_prose.py` inspects base and proposed content of each path that the configured documentation settings would floor at `documentation`. Only changed lines count, plus unchanged lines whose kind the change alters. Changed fenced code or fences, inline code spans, possibly indented code, raw HTML/comments, front matter and task-list items (acceptance criteria) floor the path at `ordinary` with the reason recorded as its rule. So do deletions, mode changes, non-UTF-8 bytes and non-Markdown files. Agent policy, review settings and sensitive rules are unchanged and run first.
- Routing: when every planned path is prose-only project documentation without a starter source, `docs-check` replaces `make check`. A Graft check, if configured, still applies. Mixed, managed or uncertain plans keep the full applicable suite. The documentation tier still records one behavioral report, so there is no evidence-schema change. Configuration edits stay `ordinary` and use the stricter of base and proposed settings.
- Tests: `test_prose_assurance.py` covers prose beside an unchanged example, each stricter content kind, uncertain changes, a new prose file, mixed scope, configuration self-lowering, changed agent instructions, the consumer launcher route, the `docs-check` command, and a prose correction through publication. Publication is refused without documentation proof, and the application suite is never run. Existing tier and requirement tests were updated to supply `docs-check` for prose. `test_documentation_only_change_passes_with_one_behavioral_report` was removed as superseded by the new route and journey tests.
- Docs and distribution: the verification guide gains a prose-only section and corrects an earlier claim that `make check` checks links. `ENGINEERING.md` and the verifier definition are updated. `markdown.py` and `verification_prose.py` are added to the template inventory, and the manifest and install metadata are regenerated. Bookkeeping and comment exemptions are not enabled.
- First review (snapshot `404134ce…`): all four checks passed (589 tests; 13/13 evals). Standards PASS and Spec PASS, both with non-blocking notes. Security FAIL and Behavioral FAIL:
  - The classifier missed code, task items and HTML inside list items and blockquotes, as well as tab and byte-order-mark variants, inline HTML, and the inner lines of HTML blocks.
  - A documentation path named like `-h.md` could switch off `docs-check` through argument parsing.
  - Some valid links (setext and blockquoted headings, headings containing links, `<…>` targets, `?query` suffixes) were reported as broken.

  These reports remain history.
- User authorized the corrections on 2026-10-14 (proposed items 1–3, with item 4 as a documented limit):
  - The scanner strips containers, expands tabs, drops a byte-order mark, detects HTML anywhere outside inline code and autolinks, and continues HTML blocks to the next blank line.
  - The required check is `./engineering docs-check -- <paths>`.
  - `docs-check` accepts the previously rejected valid link forms.
  - Each probe case has a regression test.
  - Documented limit: `docs-check` checks only the planned files, so links in other documents to a renamed heading are the documentation reviewer's responsibility (guide and verifier updated). Spec's note that ADRs and context docs fall under the default documentation setting is unchanged: it is a project configuration choice.
- Second review (snapshot `100f2e76…`): all four checks passed (600 tests; 13/13 evals). Spec PASS; Standards CONCERNS (judgement calls); Behavioral FAIL and Security FAIL. The findings: HTML blocks such as `<pre>` continue past blank lines; a blockquote nested inside a list item was not stripped; an escaped backtick turns a code span into raw HTML; fence edge cases; and regexes that can take more than 20 seconds on hostile lines. These reports remain history.
- Focused grilling after two unsuccessful correction attempts, agreed with the user on 2026-10-14:
  - Q1: replace the denylist with a document-level allowlist. Both base and proposed versions must use only supported Markdown: headings, paragraphs, tables, lists and blockquotes nested in any order, top-level fences, and inline code. Otherwise the whole document takes the stricter route, and the reason names the construct and line: raw HTML or any `<` outside inline code (including autolinks), front matter or a byte-order mark, a fence inside a container, an unclosed or invalid fence-like line, a backslash-escaped backtick, or a line over 1,000 characters.
  - Q2: no new dependency; use an in-house subset recognizer.
  - Q3: a 1,000-character line cap plus linear scanning.
  - Q4: fix the Standards judgement calls. Keep noun-style function names and the omitted `__future__` import, matching the existing modules.
  - Q5: fences inside containers are unsupported.
  - Q6a: indentation ambiguity leans lenient, so indented lines are prose. Fences stay strict.
  - Q6b (data: only 3 of 50 commits touching configured docs were documentation-only, and changed inline code was the most common trigger): only changed fenced lines and task-list items take the stricter route. Changed inline code counts as prose. This narrows the decision's "changing a command that users are told to execute requires validation" to fenced blocks. The accepted Wayfinder decision file is unchanged.
  - Q6c: lighter review for `.scratch` and experiment notes is a separate needs-triage follow-up, not part of this ticket.
  - Q7: `docs-check` stays best-effort on any Markdown.
  - Q8: reasons name the construct and line.
- Implemented the agreed design. Changes beyond the decisions:
  - Inline code may wrap across plain continuation lines of a paragraph, because CommonMark allows it and hard-wrapped docs use it. A span stays unbalanced (unsupported) if the next line is a fence, HTML, a heading, a setext underline, a new list item or a change in quote depth.
  - `docs-check` gains `markdown.run()` and resolves anchors for headings inside list items.
  - The publication test asserts which proof is missing.

  Standards follow-ups: a `Kind` literal type, a helper (`inspect_documentation`), `DOCS` imported in tests, `read_markdown`/`link_problems` names, and no walrus in `cli.py`. Noun-style function names and the omitted `__future__` import match the existing modules.
- Third review (snapshot `d6d922e3…`): all four checks passed (611 tests; 13/13 evals). Standards PASS and Spec PASS. Behavioral FAIL and Security FAIL, on two points: inline code wrapped across lines could hide raw HTML (this came from the multi-line span extension, not from a user decision), and editing the continuation lines of a wrapped task item counted as prose. Minor findings covered indented fences under list items, slow scans on very long input, and `markdown.py` missing from the sensitive module list. These reports remain history.
- User decision 2026-10-14 (to simplify and reduce cost, after an explicit explanation of the trade-off): classify by file type only. A path qualifies as prose-only documentation when it is a Markdown file (`.md`, `.markdown`) in a configured documentation location, is not executable and is not deleted. Its content is not inspected: changed fenced commands, inline code, HTML and task items all count as prose and receive the one documentation review plus `docs-check`. This decision supersedes, for this ticket:
  - the first criterion's "classifies actual changed content … a Markdown suffix … is insufficient";
  - the third criterion's stricter treatment of changed executable examples and requirements inside configured documentation;
  - the matching spec and decision lines ("A path, title, or model assertion alone cannot prove an exemption"; "Markdown is not inherently inert").

  Agent policy, review settings, sensitive and managed paths, mixed plans, starter sources and configuration self-lowering keep their stricter treatment. The Wayfinder decision file and spec are unchanged; this ticket records the superseding decision.
- Implemented the file-type decision:
  - `verification_prose.py` is removed. `inspect_documentation`/`prose_reason` check the suffix, presence and executable bit (base or proposed) and record `unsupported documentation format`, `deleted document` or `executable file`.
  - `markdown.py` keeps only best-effort `docs-check`, which skips long lines and is now a sensitive verification module.
  - Non-UTF-8 Markdown still classifies as prose but cannot pass `docs-check`.
  - The guide and verifier state that changed examples get only the documentation review, which must confirm they are correct.
- Fourth review (snapshot `d8f16917…`): all four checks passed (591 tests; 13/13 evals). Standards PASS, Spec PASS, Security PASS, Behavioral CONCERNS: the guide's tier rule still said "changed content is prose-only". The remaining items were non-blocking: slow anchor recomputation in `docs-check`, a pathspec-magic edge in the base-mode lookup, no test pinning `markdown.py` as sensitive, and naming nits. These reports remain history.
- User authorized fixing all of them on 2026-10-14. The guide wording is fixed and notes the 1000-character skip. `docs-check` caches anchors per file (800 headings: 3.6 s → 0.04 s). The base-mode lookup uses `:(literal)`. A test pins `markdown.py` as sensitive. Functions are renamed to `floor_non_prose_documentation` and `lines_outside_fences`.
