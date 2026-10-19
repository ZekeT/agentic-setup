# Bounded legacy cleanup

Status: implementing

Retire the leftover .engineering directory and optionally
.scratch/agentic-setup-adoption after adoption. Follow docs/product-direction.md.
Only an explicit external CLI command may change a target, after a reviewed preview.

Use `agentic cleanup TARGET [--adoption-notes] [--archive PATH] [--html [PATH]]`.
Default archive parent: source migrations/<target>/cleanup-backups.
Apply requires --apply --expect TOKEN; HTML is preview-only.

Archive selected directories by same-filesystem rename, never recursive deletion or
copying through links. Preserve all bytes, modes, symlinks, ignored files and nested
snapshot contents without reading secrets. Refuse nested Git metadata, special files,
mount boundaries, symlink roots, source/target overlap and archive overlap. Inventory
metadata (including names, modes, inode, size, modification/change times and link
text) binds previews to current trees; this is not a content hash. Require quiescent
writers. Preserve unrelated dirty files, installed skills, hooks and Git state.
Remove only exact known obsolete Engineering ignore rules, displaying the diff.
Store original ignore bytes and manifest outside target. Roll back completed moves
and ignore edit on ordinary failure; retain evidence and report recovery failures.
Refuse stale previews and existing archives. Repeat after success is a no-op.

Testing uses the established public CLI and filesystem outcomes in disposable Git
projects. Inject filesystem failure only for rollback coverage. Verify read-only
preview, archival, symlinks, stale metadata, scope, failure, repeated apply and HTML.
No real target apply or application checks are authorized. Generate UC3 preview only.
