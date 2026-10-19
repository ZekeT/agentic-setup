# Starter architecture

The external `engineering` command inspects a target, builds a bounded preview,
then applies that exact preview. The target receives guidance and selected skills;
it does not receive the installer or maintainer tests.

`starter/files.py` owns safe file access and rollback. `starter/adopt.py` recognizes
legacy content and proposes guidance. The CLI presents conflicts and exact changes.
The legacy hash catalog serves installation only, never application development.
The prior architecture is archived at archive/pre-simplification-2026-10-19.
