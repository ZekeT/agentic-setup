# Product context

Agentic Setup configures target workspaces with development conventions and selected
agent skills. Clone the tool separately and run `agentic` against an explicit target
workspace. Daily development uses the project's native checks and installed skills.

Development conventions cover personal workflow, Git preferences, standards and
configuration that complement Matt Pocock, Pstack and HumanLayer. A target workspace
owns its application code, documentation, scratch plans and local overrides.
A minimal transition removes recognized Agentic Starter overhead while preserving
application work. A selective update changes only requested development conventions.

The repository is `agentic-setup`; `agentic_setup/` implements the CLI. New target
metadata lives in `.agentic-setup/`; existing `.starter/` records remain supported.
A profile would mean a named bundle of conventions and skill selections, but no
profile mechanism is needed yet. See [product direction](../product-direction.md)
for decisions and future inspection/skill freshness reporting.
