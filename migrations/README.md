# Local migration plans and previews

Agents: follow the [migration agent guide](../docs/migration-agent-guide.md) before
working on a live target. The format below supports that one-project-at-a-time process.

Keep each target's artifacts together under its workspace name:

```text
migrations/
└── project-name/
    ├── resolutions.json
    ├── replacements/
    ├── preview-001.html
    ├── preview-002.html
    └── backups/                 # only created by an approved resolution apply
```

From Agentic Setup, generate an automatically numbered report:

```bash
./agentic adopt /path/to/project-name --minimal --html
./agentic adopt /path/to/project-name --minimal --resolutions migrations/project-name/resolutions.json --html
```

Without a resolution file, reports go under this checkout's migrations/<workspace-name>/.
With one, reports go beside that file. `--html PATH` still selects an explicit new
filename. Relative paths resolve from your current directory; `/migrations/` would
mean the filesystem root. Names are never overwritten. If different projects share
a basename, use distinct external plan folders or explicit report paths. Every plan
binds the full canonical target path, so plans cannot be reused accidentally.

All project folders are ignored by Git. This README is the only tracked file here.
Plans, replacements, reports and recovery copies can contain project configuration;
keep them local. Never edit the target as a way to resolve a preview conflict.

## Resolution file (version 1)

```json
{
  "version": 1,
  "target": "/absolute/canonical/path/to/project-name",
  "operations": [
    {
      "path": ".claude/settings.local.json",
      "action": "json_remove",
      "expected_sha256": "SHA256_OF_CURRENT_TARGET_FILE",
      "reason": "Remove the retired publish permission; keep other permissions and hooks.",
      "pointer": ["permissions", "allow"],
      "value": "Bash(./engineering publish *)"
    }
  ]
}
```

Replace the hash placeholder with the current file's SHA-256 from the before/current
section of the HTML preview. Use null only when the file is absent. Reasons are
required and appear in the report. Each path may occur once; unknown keys/actions
are rejected. Operations are limited to adoption's inspected configuration paths.
Git paths, secrets, symlinks, traversal and application source/data paths are refused.

Supported actions (in addition to path, action, expected_sha256 and reason):

| Action | Fields | Meaning |
| --- | --- | --- |
| delete | none | Remove this exact existing file. |
| replace_text | old, new | Replace exactly one occurrence in the proposed content. |
| json_remove | pointer, value | Remove exactly one matching value from a JSON array selected by object keys; preserve other JSON values. |
| replace_file | replacement | Use the entire contents of a file relative to this plan, e.g. replacements/CLAUDE.md. |

Edits start from the default proposed contents, or current contents if no default
change exists. The hash always guards the current target file, not the default
proposal. Replacements are whole final files; supplying current bytes cancels a
default edit, but remaining active legacy wiring still blocks application.
JSON edits preserve values, not formatting. No shell commands or blanket conflict
suppression are supported. Existing template baselines remain upstream templates;
project overrides stay distinguishable during later selective updates.

## Review and apply

Save the resolutions here, generate a fresh HTML preview and refine it until ready.
Saving a plan is not approval. After explicit approval, use the same resolution file
and the report's token:

```bash
./agentic adopt /path/to/project-name --minimal --resolutions migrations/project-name/resolutions.json --apply --expect PREVIEW_TOKEN
```

Changing resolution text, replacement contents or target inputs invalidates the
preview. Plans describe one transition; regenerate them for later changes rather
than reusing a plan whose expected contents have already changed. Tracked local edits
still block apply. Explicitly resolved untracked/ignored
files can change only after originals are saved outside the target, under
backups/<preview-token>/before/. manifest.json records target, baseline, original
modes and before/after hashes. Apply refuses if it cannot create that recovery snapshot;
existing recovery directories are never overwritten. Inspect a failed/partial attempt
before retrying. Ordinary write failures still trigger the installer's in-memory rollback.
Recovery snapshots do not automatically revert later work or change Git history.
No restore command or automatic cleanup of snapshots is introduced here.
