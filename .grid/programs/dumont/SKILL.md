---
name: dumont
description: Load when connecting to any external tool or service — git, GitHub, Jira, or others. Dumont orchestrates drivers. Check which drivers are installed before starting external work.
metadata:
  version: "0.1.0"
  suggests: "working with git | github | external tool | connecting to external service | push | pull | open PR"
---

# Dumont — External Connector

Dumont is the uplink between the Grid and external systems. He orchestrates drivers — each driver is a skill that handles one external tool.

## Finding installed drivers

```bash
python3 .grid/programs/able/scripts/grid-state.py skills --search dumont/skills
```

## Loading a driver

Load the relevant driver skill before doing external work:

| Task | Driver to load |
|---|---|
| Working with git (commits, branches, history) | `dumont/skills/git` |
| Working with GitHub (PRs, issues, push/fetch) | `dumont/skills/github` *(not yet installed — use Anon)* |
| Working with Jira | `dumont/skills/jira` *(not yet installed — use Anon)* |

## Installing a driver

Drivers live in `.grid/programs/dumont/skills/<driver-name>/`. Each is a standalone agentskills.io skill — usable without Dumont if needed.

To install a driver from the Grid Design registry, ask the model:
> *"Install the <driver-name> driver for Dumont"*

To create a project-specific driver as an iso, follow the skill creation protocol in `maintain-skills`.

## Connection management

<!-- TODO: Design and implement the connection management pattern:
  - On first use of a driver, ask the user where connection configs should be stored (default: ~/.config/grid/connections/)
  - Record the chosen path in user.md (not the credentials themselves)
  - Write credentials to a chmod 600 file at that path (e.g. ~/.config/grid/connections/jira.env)
  - Each driver ships a connect.sh script that sources the 600 file and uses credentials internally
  - The model invokes connect.sh and receives only success/failure — raw credentials never enter the context window
  - Multiple projects share the same ~/.config/grid/connections/ — configure once, reuse everywhere
-->

## user.md

Project-specific driver preferences, default tool choices, or authentication notes belong in `user.md` alongside this file.
