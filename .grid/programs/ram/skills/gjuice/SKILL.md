---
name: gjuice
description: Use when tracking tasks, bugs, decisions, or any work worth remembering across sessions. A local, model-friendly issue management system — no external service required. Load when the user mentions issues, backlog, tasks to track, or what to work on next.
compatibility: Requires Python 3.8+
metadata:
  version: "0.1.0"
  suggests: "user wants to remember something for later | user mentions backlog, keeping track, or not forgetting | user needs persistent task tracking across sessions"
---

# Gjuice — Local Issue Management

A lightweight, persistent issue tracker that lives in your project. No external service. No account. Works offline. Fully readable by humans and models alike.

Issues are stored in `.grid/programs/ram/skills/gjuice/issues.js`. This is the **single source of truth** for tracked tasks.

## Setup

On first use, ask the user: *"What should gjuice call this project in the browser viewer?"* Suggest from the project iso or git remote if available. Create `gjuice.config.js` with a minimal seed:

```js
window.GJUICE_CONFIG = {
  "projectName": "<project name>"
};
```

Then populate statuses, priorities, types and areas using `--config-add` (see **Config management** below). `issues.js` is created automatically on the first `--add`.

## Loading current state

Run from the project root:

```bash
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py              # active issues
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --all        # all issues
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --id 42      # single issue (full detail)
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --last       # most recent issue by id
```

## Schema

```js
{
  id:          1,                     // numeric, auto-incremented — use for reference ("issue 42")
  title:       "Gerund form title",   // e.g. "Implementing X", "Deciding Y"
  type:        1,                     // numeric id — resolves to label via gjuice.config.js
  area:        1,                     // numeric id if areas configured; open string if areas: [] in config
  status:      1,                     // numeric id — resolves to label via gjuice.config.js; terminal statuses set completedAt
  priority:    1,                     // numeric id — resolves to label via gjuice.config.js
  createdAt:   "2026-01-01T10:00:00+00:00",
  completedAt: "2026-01-01T11:00:00+00:00",  // set when terminal status is reached
  description: "Full description. Optional.",
  solution:    "How it was resolved. Set when done."
}
```

## Config management

All categories (statuses, priorities, types, areas) are defined in `gjuice.config.js` and managed through the script. **Never edit the config file manually.**

```bash
# List everything
python3 .../gjuice.py --config-list

# Add entries
python3 .../gjuice.py --config-add type     --label "Security" --bg-light "#fee2e2" --fg-light "#991b1b" --bg-dark "#4a1010" --fg-dark "#fca5a5"
python3 .../gjuice.py --config-add area     --label "api"      --bg-light "#dbeafe" --fg-light "#1e40af" --bg-dark "#1e3a5f" --fg-dark "#93c5fd"
python3 .../gjuice.py --config-add priority --label "critical" --bg-light "#fee2e2" --fg-light "#991b1b" --bg-dark "#4a1010" --fg-dark "#fca5a5"
python3 .../gjuice.py --config-add status   --label "wontfix" --terminal \
    --bg-light "#f1f5f9" --fg-light "#475569" --bg-dark "#1e2433" --fg-dark "#94a3b8"

# Update an entry by id
python3 .../gjuice.py --config-update type 3 --label "Design Decision"
python3 .../gjuice.py --config-update status 3 --no-terminal

# Remove an entry (blocked if any issue uses that id)
python3 .../gjuice.py --config-remove area 4
```

### terminal flag (statuses only)

`terminal: true` marks a status as "closed". Effects:
- Sets `completedAt` when an issue moves to this status
- `--done` uses the first terminal status; `--reopen` uses the first non-terminal
- Default view (no `--all`) hides terminal-status issues
- Summary separator appears before terminal issues

Use `--terminal` to mark a status as closed, `--no-terminal` to revert it.

### Color palette for new entries

When the user asks to add a type or area and provides no colors, auto-assign the next unused pair cycling through:

| Pair | bgLight | fgLight | bgDark | fgDark |
|---|---|---|---|---|
| 1 | `#dbeafe` | `#1e40af` | `#1e3a5f` | `#93c5fd` |
| 2 | `#fef3c7` | `#92400e` | `#3d2e00` | `#fcd34d` |
| 3 | `#d1fae5` | `#065f46` | `#064e3b` | `#6ee7b7` |
| 4 | `#ede9fe` | `#5b21b6` | `#2e1a6e` | `#c4b5fd` |
| 5 | `#fee2e2` | `#991b1b` | `#4a1010` | `#fca5a5` |
| 6 | `#fce7f3` | `#9d174d` | `#4a0e2e` | `#f9a8d4` |
| 7 | `#ecfdf5` | `#065f46` | `#022c22` | `#6ee7b7` |
| 8 | `#fff7ed` | `#c2410c` | `#431407` | `#fb923c` |
| 9 | `#f0f9ff` | `#0369a1` | `#0c2a3e` | `#7dd3fc` |
| 10 | `#faf5ff` | `#7e22ce` | `#2e1a6e` | `#d8b4fe` |

Cycle: `(id - 1) % 10`.

## Default config

When setting up a new project, seed these defaults via `--config-add`:

**Statuses:** `pending` (not terminal), `done` (terminal)

**Priorities:** `high`, `medium`, `low`

**Types:** `Implementation`, `Discussion`, `Architectural Decision`, `Learning`, `Security`

**Areas:** project-specific — ask the user for the main areas of their codebase.

## Priority guidance

| Label | When |
|---|---|
| `high` | Blocks other work or has user-facing risk |
| `medium` | Normal backlog |
| `low` | Nice-to-have |

Pass by id or label: `--priority 1` or `--priority high`

## Operations

**Never edit `issues.js` directly.** Always use `gjuice.py` — it handles JSON formatting and ID assignment.

```bash
# Add
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --add \
    --title "Implementing login" --type 1 --area auth --priority medium

# Mark done
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --done 42 --solution "Implemented via JWT."

# Reopen
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --reopen 42

# Update
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --update 42 --priority high
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --update 42 --description --augment "Additional context."
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --update 42 --solution --augment "Follow-up fix applied."

# Search and filter
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --search jwt
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --area auth
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --type Discussion
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --priority high
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --status done --area persistence
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --all --sort id-desc --limit 5
```

### Description and solution flags

| Flag | Effect |
|---|---|
| `--description "text"` | Replace description |
| `--description --augment "text"` | Append to existing description |
| `--solution "text"` | Replace solution |
| `--solution --augment "text"` | Append to existing solution |

## Viewing in browser

Open as a `file://` URL in any browser — no server needed. Provide the full URL when telling the user, e.g. `file:///path/to/project/.grid/programs/ram/skills/gjuice/index.html`.

- Multi-select filters — Status, Priority, Type, Area
- Full-text search — `/` focuses, `Esc` clears; supports regex toggle
- Sort by any column; default newest first
- Expand row to reveal description and solution
- URL anchor — `index.html#42` scrolls to and expands issue 42
- Green dot marks issues completed within the last 7 days

## Conventions

- **Always search before starting work:** `--search <keyword>`. Report what was found.
- **Marking done requires user confirmation** — present the issue and ask: *"Mark #n as done?"*
- **Reopening requires user confirmation** — ask: *"Issue #n is already done — reopen it?"*
- **No match found** — say so explicitly and ask: *"No matching issue found — should I create one?"*
- **One issue per concern** — don't bundle unrelated work
- **Mark done in the same commit** as the code change — include `--solution` to document the outcome
- **Architectural decisions** — add or update an `Architectural Decision` issue to document the outcome
- **Title form:** gerund, sentence case — "Implementing X", not "Implement X" or "IMPLEMENT X"

## Issues vs session tasks vs TODOs

These are three distinct layers with different lifecycles:

| Layer | Where | Lifecycle |
|---|---|---|
| **Issues** | gjuice `issues.js` | Long-term project backlog — persists across sessions |
| **Session tasks** | Able `tasks.json` | Tactical this-session work — reset on each `init --fresh` |
| **TODOs** | inline in `SKILL.md` files | Unfinished design in skills — cleared when resolved |

Issues are **not** pre-loaded into session tasks at startup. They are queried on demand:

- When the user asks for pending work
- In Tron's pre-commit checklist, to cross-reference the commit against open issues
- When closing an issue (Tron requires explicit confirmation)

To query issues on demand:

```bash
python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --status pending
```

## user.md

Project-specific area vocabulary, additional types, priority definitions, or query conventions belong in `user.md` alongside this file.

## Install

Copy the `gjuice` skill directory into the target project's Ram sub-skills folder:

```bash
cp -r .grid/programs/ram/skills/gjuice /path/to/project/.grid/programs/ram/skills/
```

Initialize an empty issue store and default config:

```bash
cd /path/to/project/.grid/programs/ram/skills/gjuice
echo 'window.TASKS = [];' > issues.js  # matches gjuice.py format
python3 scripts/gjuice.py --config-list  # verifies the install
```

Then register in the active session:

```bash
python3 .grid/programs/recognizer/scripts/scan-skills.py | \
    python3 .grid/programs/able/scripts/grid-state.py skills --register-batch
```

After installation, inform the user: gjuice includes a browser UI — provide the path as a clickable `file://` URL, e.g. `file:///home/user/myproject/.grid/programs/ram/skills/gjuice/index.html` (resolve from the project root). Opens directly in any browser, no server needed. Tell them this once, clearly, so they know it exists before they start creating issues.

## Uninstall

Before removing, verify no active issues remain:

```bash
python3 scripts/gjuice.py --status pending
```

Remove from disk:

```bash
rm -rf /path/to/project/.grid/programs/ram/skills/gjuice
```

The skill registry is updated automatically next session. If uninstalling mid-session, ask Anon to handle de-registration.
