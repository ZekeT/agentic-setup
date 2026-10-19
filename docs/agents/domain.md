# Domain documentation

This repository maintains the external setup tool, not an application template
that must be copied wholesale. [Product direction](../product-direction.md) records
the agreed decisions and exclusions for v3 and later features. Read relevant
sections when planning; update durable decisions explicitly when they change.

[Product context](../context/product.md) supplies the repository's domain vocabulary;
[architecture](../architecture.md) explains the installer/project boundary. Use these
locations for upstream glossary references rather than creating parallel stores.
Keep architectural reasons in `docs/adr/`. Existing v2 ADRs are historical and
superseded, not requirements for future work. Code and tests establish executable
behavior; `.scratch/` records feature scope, decisions and delivery status.

Generated and adopted projects own their own domain docs, ADRs and tracker. Their
setup guidance preserves existing choices; this repository's maintainer docs and
work items are not installed into them. No feature document or navigation tool is
mandatory for every source folder.
