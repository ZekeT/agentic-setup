# Product context

Agentic Starter provides engineering invariants, navigation integration and safe installation/update tooling. Upstream skills own development workflows. Local Markdown tracking keeps work independent of the Git hosting provider.

## Language

**Feature milestone**:
An agreed grouping of work toward a demonstrable feature outcome or coherent integration point, with explicit completion conditions. Its scope may be recalibrated with the user as implementation reveals new information; delivery alone does not establish review or acceptance.

**Semantic review**:
Independent assessment of whether a proposed change follows repository standards and satisfies its originating requirements. Standards and Spec are separate review axes; executing automated checks is a separate activity.

**Mechanical bookkeeping**:
Status, delivery-link, or evidence-pointer updates whose permitted scope and supporting evidence can be validated mechanically. Changes to requirements, policy, executable examples, or implementation are outside this category.

**Behavioral review**:
Independent examination and probing of changed behavior, failure paths, and nearby regressions, informed by recorded automated-check evidence. It is distinct from checking conformance to the originating spec or merely executing the existing test suite.

**Maintainer checkout**:
The starter's own source repository, where the starter's implementation is developed and released.
_Avoid_: starter repo, source checkout

**Consumer project**:
Any project with the starter installed, whether it arrived by generation or adoption.
_Avoid_: generated application, adopted project, existing project (as distinct kinds)

**Installation route**:
How a consumer project obtained the starter: generation for a new project, adoption for an existing one.

**Installation role**:
The recorded standing of an installation: maintainer checkout or consumer project.

**Managed implementation**:
Starter-owned files in a consumer project that the starter replaces on update and the project does not edit.
_Avoid_: installed tooling, engineering files

**Project configuration**:
Starter settings owned by the project, which the starter validates and migrates but does not overwrite.
_Avoid_: engineering config

**Navigation**:
Optional derived knowledge of code structure, supplied by a navigation provider (Graft) or absent (`none`), in which case agents search and read source directly.
_Avoid_: indexing, graph (as the feature name)

**Optional capability**:
A feature a project enables deliberately, whose dependencies and gate obligations exist only while it is enabled.

**Capability content**:
Managed content an optional capability's dependency installs together while the capability is enabled and an update removes after it is disabled, such as Graft's launcher, skill, package pins and agent-policy navigation section. Project data it produced, such as the Graft index, is not capability content.

**Maintainer source**:
Content in the maintainer checkout that becomes managed implementation or proves it: templates, managed implementation, maintainer tests and evals.

**Review tier**:
The declared risk level of a proposed change — documentation, ordinary or sensitive — which decides the independent review it needs.
_Avoid_: review level, risk class

**Tier floor**:
The lowest review tier a change's paths allow; a change may declare a higher tier but never a lower one.

**Carried evidence**:
Reviewer reports from an earlier snapshot that remain current after a clean rebase left the change itself untouched; its checks still run again.
_Avoid_: reused review, inherited proof
