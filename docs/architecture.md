# Starter architecture

Agentic Starter is an external setup entry point for greenfield and brownfield
projects. Its [product direction](product-direction.md) defines the scope.

```text
This repository                          Target project
engineering → starter/                   application source and native checks
               └─ payload/ ── selected → project instructions and docs/agents/
pinned upstream skills ────── selected → installed skills
                                         .starter/ installation baselines
                                         .scratch/ project work, when used
```

`engineering` is the CLI entry point; `starter/` is its Python implementation.
It replaces the old installer code, but stays in this source checkout. It is not
a runtime framework installed into applications. `starter/payload/` contains the
selected guidance templates; setup also creates missing project-specific references.
The target does not receive `engineering`, the `starter/` package, this repository's
`.scratch/`, product-direction docs, maintainer tests or Git history.

Each target owns its application, docs, tracker and native tools. Adoption preserves
existing content and configuration; initialization supplies missing guidance.
`.scratch/` is used when the project chooses Matt's local Markdown tracker and
starts recording work. It is not a shared tracker across projects. The target's
`.starter/` records template baselines and skill pins for explicit updates only;
ordinary development does not consult it or require access to this checkout.

This repository's own `.scratch/` tracks improvements to the setup tool. Its `docs/`
records product decisions, architecture and maintainer agent configuration. Its
`tests/` verifies installation and preservation behavior in disposable projects.

The external CLI inspects a target, builds a bounded preview, then applies that
exact preview. `starter/files.py` owns safe file access and rollback;
`starter/adopt.py` recognizes legacy content and proposes guidance. The legacy hash
catalog serves installation only. The previous implementation and its planning
artifacts remain available at `v2.1.0`.
