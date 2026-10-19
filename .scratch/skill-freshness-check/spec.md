# Explicit skill freshness check

Status: in progress

## Problem Statement

Target workspaces record upstream skill commits, but offline inspection cannot tell
whether upstream has advanced. Users need an explicit check before deciding to update.

## Solution

`agentic skills check TARGET [--bundle NAME]` reports upstream default-branch revisions
for recorded supported skills, without modifying the target or applying updates.

## User Stories

1. As a maintainer, I can check all recorded supported skills or one selected bundle.
2. I can distinguish matching, behind, ahead, diverged and unavailable history.
3. I see missing, duplicate and unrecorded installations without guessed provenance.
4. I can inspect legacy commit-only records in either supported metadata directory.
5. I get a useful partial report if one upstream is unavailable.
6. My project files, local customizations and Git state remain unchanged.

## Implementation Decisions

Use the existing safe metadata/location readers and temporary upstream resolver.
Only contact the configured bundle source; never use a target-provided URL.
Resolve each relevant source once. Fetch validated recorded hashes when required to
establish ancestry. No record means no online query. Unknown/custom sources and
malformed revisions are reported as unknown, with no inferred ownership.
Report upstream repository revisions, not per-skill content changes or compatibility.
Matching commits do not verify installed bytes. Local inspection stays offline.
Exit 0 for a complete revision check (including updates available and no records),
1 for incomplete/unknown comparisons, missing/duplicate recorded installations or errors.
No apply, ref, from, automatic updating or caching options for this online command.

## Testing Decisions

Use the existing agreed external CLI/filesystem seam with disposable Git repositories
and real local Git URL rewrites; test reports and unchanged target snapshots, including
Git state. Exercise latest, older revisions, missing history, source failures, metadata
compatibility, unknown provenance and filtering. Run native checks and Standards/Spec
review, plus a disposable real upstream smoke check.

## Out of Scope

Applying updates, content integrity certification, background checks, new bundles,
release/version changes and modifying real target projects. Publishing a PR is separate.
