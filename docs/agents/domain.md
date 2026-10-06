# Domain documentation

Single-context repository. Durable product/domain knowledge belongs in
`docs/context/`; architectural decisions and rejected alternatives in `docs/adr/`.
Read only relevant documents. Keep stable feature instructions near the code,
or in `docs/features/`, covering purpose, interfaces, invariants and gotchas.

Use the installed upstream domain-modeling discipline. This project chooses
these document locations rather than requiring a root GLOSSARY.md or
GLOSSARY-MAP.md. `docs/context/product.md` is this project's domain glossary;
resolve upstream glossary references there. Do not create parallel context stores. Current executable behavior is established by code and
tests. Tracker artifacts describe decisions for work, not a canonical database
of all current behavior. Generated structural knowledge belongs to Graft.
