# Agentic Setup naming

Status: implemented and reviewed; publication in progress

## Problem Statement

Engineering and starter do not clearly describe a separately cloned tool that
configures and updates target workspaces with development conventions and skills.

## Solution

Use the accepted names in [product direction](../../docs/product-direction.md):
Agentic Setup, agentic-setup repository, agentic CLI, agentic_setup package,
development conventions, target workspace, .agentic-setup metadata, CONTRIBUTING.md.

## User Stories

1. As a maintainer, I want consistent names in commands, docs and CI.
2. As a user, I want skills install to identify the operation explicitly.
3. As a v3.0.0 user, I want existing installation history and custom guidance preserved.
4. As a reviewer, I want the existing rebuild PR to reflect the renamed product.

## Implementation Decisions

New targets use the new metadata directory. Existing published metadata and licenses
stay in place and remain authoritative. Conflicting old/new records are rejected.
Keep historical migration identifiers, upstream skill bodies and release tags intact.
Rename the GitHub repository and origin remote; retain the current branch and PR.
The local checkout directory can keep its existing name without affecting usage.

## Testing Decisions

Reuse the accepted external CLI/filesystem seam in disposable repositories. Extend
existing update preservation coverage to old metadata. Verify the renamed command,
skill installation grouping, native checks and actual published-tag compatibility.

## Out of Scope

Unified inspection, skill freshness/upgrade commands, profiles, merging the PR,
retagging v3.0.0 or renaming the active local workspace directory.

## Delivery

See [implementation ticket](issues/01-standardize-naming.md).

## Verification

`make check`: Ruff lint/format, mypy and 17 tests passed (38.61 seconds).
The renamed-command test failed before the rename; the legacy-metadata update case
failed before compatibility support. Both pass. Actual published v3.0.0 initialization
and pinned HumanLayer installation followed by renamed guidance update, skill
reinstallation and adoption preserved custom guidance, skill pins and licenses.
Repeated operations are no-ops. Ten local doc links and CLI help passed.

Matt Standards and Spec review of c8a1831...8921451 reported zero findings each.
GitHub repository is now ZekeT/agentic-setup; origin and PR #56 use the new name.
The PR description includes the rename and these results. Native local workspace
path and immutable published tags retain their existing names. No merge performed.
