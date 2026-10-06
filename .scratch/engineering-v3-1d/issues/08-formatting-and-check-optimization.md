# Bound formatting and remove duplicate check execution

Type: grilling
Status: resolved
Assignee: Codex session for zeke
Blocked by: 01, 02, 03
Parent: [Engineering v3-1d decision map](../map.md)

## Question

How should the agreed application `fmt`, `engineering-fmt`, and explicit `fmt-all` split support intended-file formatting without upstream skill wrappers, and which duplicate checks or fixture setup may be removed without weakening the initial full applicable suite or correction-evidence contract?

Decide explicit formatting scope and failure behavior, the boundary between authoritative checks and independent behavioral inspection, and acceptable fixture reuse. Preserve non-mutating verification, exact evidence inputs, test isolation, and native Matt workflows. No new diagnostics, measurement workflow, or promised speedup.

## Comments

Graduated from the map after the review and correction-evidence decisions resolved. Pending human discussion; no implementation authorized by this ticket.

Read-only inspection found that maintainer `make fmt` currently spans application and harness paths, while the generated application's target already covers application paths only. `make check` executes doctor and maintainability, and `make engineering-check` repeats those checks when both gates are required. Application tests and the explicit engineering test suite cover different paths and are not duplicate executions. These findings support discussing scope and reuse; no checks were removed or executed for this planning ticket.

## Answer

The user agreed to all three recommendations in the live exchange.

- Preserve the application `fmt`, harness `engineering-fmt`, and explicit `fmt-all` split. Routine formatting uses an explicit intended-file selection before checkpoint commits and review. Empty selection does nothing; unsupported paths produce a clear error rather than expanding scope. Implement this in project-owned tooling without changing or wrapping Matt's skills. Formatting does not establish passing lint or verification; authoritative checks remain non-mutating.
- Remove proven overlap from starter-owned check recipes while keeping individual commands useful independently. Preserve consumer-owned check recipes. Treat a required check as already satisfied only with explicit evidence of coverage; never assume an adopted project's `make check` runs harness health checks. Application and engineering suites cover different scopes and remain required where applicable.
- Reuse immutable fixture preparation only, with isolated writable copies for each test. Preserve independent Git repositories, publication state, failure scenarios, and initial full applicable suites. Independent behavioral reviewers consume recorded suite evidence and may run focused probes without repeating a valid suite. No new benchmarking system or promised speedup.

These decisions complement the existing correction-evidence and freshness contracts; they do not authorize implementation or relax current operational gates.
