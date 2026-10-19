# Agentic Setup architecture

Agentic Setup is an external setup entry point for greenfield and brownfield
projects. Its [product direction](product-direction.md) defines the scope.

```text
This repository                          Target project
agentic → agentic_setup/                  application source and native checks
               └─ payload/ ── selected → project instructions and docs/agents/
pinned upstream skills ────── selected → installed skills
                                         .agentic-setup/ installation baselines
                                         .scratch/ project work, when used
```

`agentic` is the CLI entry point; `agentic_setup/` is its Python implementation.
It replaces the old installer code, but stays in this source checkout. It is not
a runtime framework installed into applications. `agentic_setup/payload/` contains the
selected guidance templates; setup also creates missing project-specific references.
The target does not receive `agentic`, the `agentic_setup/` package, this repository's
`.scratch/`, product-direction docs, maintainer tests or Git history.

Each target owns its application, docs, tracker and native tools. Adoption preserves
existing content and configuration; initialization supplies missing guidance.
`.scratch/` is used when the project chooses Matt's local Markdown tracker and
starts recording work. It is not a shared tracker across projects. The target's
`.agentic-setup/` records template baselines and skill pins for explicit updates only;
ordinary development does not consult it or require access to this checkout.
Existing v3.0.0 targets retain their `.starter/` records and licenses in place.

This repository's own `.scratch/` tracks improvements to the setup tool. Its `docs/`
records product decisions, architecture and maintainer agent configuration. Its
`tests/` verifies installation and preservation behavior in disposable projects.

`agentic inspect` reports local setup, legacy remnants, convention differences and
recorded skills without building or applying a mutation plan. It reuses bounded file
access and the existing template/legacy catalogs; it never executes target commands
or fetches upstream.

The adoption/update CLI inspects a target, builds a bounded preview, then applies that
exact preview. `agentic_setup/files.py` owns safe file access and rollback;
`agentic_setup/adopt.py` recognizes legacy content and proposes guidance. The legacy hash
catalog serves installation only. The previous implementation and its planning
artifacts remain available at `v2.1.0`.

Skill operations resolve the selected upstream in a temporary external checkout, or
use an explicitly provided clean local checkout without fetching. The resolved commit
and copied-file hashes make subsequent updates bounded and explicit. `--ref` replays a
previewed revision; moving latest revisions invalidate old apply tokens. Licensing is
retained by revision. Older commit-only records need exact-byte verification before
new ownership baselines can be established. This is installation metadata only.

`agentic skills check` reuses that temporary source resolver for explicit online revision
comparisons, without generating or applying a mutation plan. It groups recorded skills
by configured bundle source, compares Git ancestry and reports partial failures. Target
metadata supplies recorded hashes only, never remote URLs. It does not verify installed
contents or certify compatibility; `inspect` remains offline and `skills update` previews
actual file changes separately.
