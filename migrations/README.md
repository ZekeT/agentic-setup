# Local migration previews

Save HTML previews here from the Agentic Setup workspace:

```bash
./agentic adopt /path/to/project --minimal --html migrations/project-preview-1.html
```

Use `migrations/`, without a leading slash. Relative paths resolve from the directory
where you run the command. Choose a new filename for each preview; existing reports
are never overwritten. Reports are ignored by Git because they can contain target
project configuration. This README is the only tracked file in this directory.

Open reports locally in a browser. Previewing does not change the target. Resolve
conflicts by refining Agentic Setup and generating another preview; apply only after
explicit approval of that preview through the Agentic Setup CLI.
