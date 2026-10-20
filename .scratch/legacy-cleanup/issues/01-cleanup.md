# Implement bounded cleanup

Status: complete (implementation only; live apply not authorized)

- [x] CLI preview and recoverable apply
- [x] Disposable-project tests and native checks
- [x] Standards and Spec review
- [x] UC3 HTML preview, no target writes

Final make check: 87 passed in 101.10s; Ruff and mypy passed.
Earlier full run failed because a report-wording edit left the source dirty during
the versioned-update test; committed it and reran the stable suite successfully.
Both review axes: zero remaining findings. UC3 preview-005.html, token
cd15eb461cc1e8ef96a7ee9d861f5d40f62940a720ed3a99fa2dcc8644118fc6.
