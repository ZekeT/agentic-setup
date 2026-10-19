# Explicit latest skill installation and updates

Status: implemented and reviewed locally; ready for PR

Implement latest-on-request `agentic skills install` and `agentic skills update`.
Default source is the selected bundle's upstream default branch. Resolve to a commit,
print it in preview, and support `--ref COMMIT` for exact replay. Keep `--from` as
an explicit clean local-checkout source with no network, accepting its HEAD instead
of requiring hard-coded pins. Existing bundle selection remains intentional; missing
or duplicate upstream skill names fail before writes. Do not silently replace the
selection with every upstream skill. Inspection remains offline.

Store source, resolved commit and installed file hashes per skill. Updates require
recorded ownership, canonical installed location, and unchanged managed files; report
conflicts for edited/deleted managed files, duplicate exposed names, unowned incoming
paths or source mismatches. Preserve unrelated skills, project-added files and target
work. Delete only unchanged recorded files removed upstream, with ownership independently
verified against the recorded upstream commit. Missing history blocks deletion. Preserve upstream licenses;
licenses are stored by resolved revision, so newer licenses never overwrite older copies. Preview never modifies the target;
apply uses the existing content/baseline token and committed-edit checks. Reapplication
must be a no-op. No automatic background fetching, execution of upstream scripts or
updates during ordinary development.

Legacy commit-only records: explicit install at that recorded revision may add hashes
only when all corresponding installed bytes match. Existing unrecorded skills remain
project-owned. Update without hashes reports how to establish that baseline; it must
not guess ownership or overwrite content. Existing .starter metadata remains supported.

Tests use the existing external CLI/filesystem seam and disposable Git repositories.
Exercise real local Git transport for fetching without requiring network in CI, then
smoke-test current upstream in an authorized disposable workspace. Cover stale previews,
local changes, additions/deletions, metadata compatibility and source safety. Review
committed changes with Standards/Spec axes. Publication/merge are separate steps.
