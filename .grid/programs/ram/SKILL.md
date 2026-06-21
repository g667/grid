---
name: ram
description: Load at session start or when the user mentions tasks, todos, planning, or what to work on next. Ram manages the session task list, scans skills for TODO markers, and coordinates issue lifecycle.
metadata:
  version: "0.1.0"
  suggests: "what should we work on | planning | task list | todos | what is pending | session tasks"
---

# Ram — Planning Assistant

Ram keeps track of what we're doing and what we need to do. He manages the session task list via Able and coordinates with sub-skills for persistent cross-session tracking.

## Quality of life access

When a skill asset exists that a user would benefit from accessing directly — a browser UI, a report, a reference file — Ram suggests making that access frictionless. The right mechanism depends on the asset and the OS: a symlink (double-clickable in Finder/Explorer), a shell script, a Makefile target, or a build tool entry.

If no convenient central location exists for such helpers, Ram may suggest creating a `dev/` directory at the project root — a gitignored home for daily convenience tools that don't belong in the codebase itself.

Surface this once, at an appropriate moment. The user decides.

**Example:** after gjuice is installed, offer to create a symlink to `index.html` at a user-chosen location so the issue tracker is one double-click away.

## Session task list

All task operations go through Able:

```bash
# Add a task
python3 .grid/programs/able/scripts/grid-state.py tasks --add --title "Doing X" --description "Details"

# Start a task
python3 .grid/programs/able/scripts/grid-state.py tasks --update <id> --status in_progress

# Complete a task
python3 .grid/programs/able/scripts/grid-state.py tasks --done <id>

# View pending tasks
python3 .grid/programs/able/scripts/grid-state.py tasks --status pending
python3 .grid/programs/able/scripts/grid-state.py tasks
```

## Available scripts

| Script | Purpose | Usage |
|---|---|---|
| `scripts/find-todos.sh` | Scan all `.grid/` directories for open `TODO:` markers | `./find-todos.sh [md]` |

## TODO scanning

Run before committing to surface any open design questions in the skills touched during this session:

```bash
.grid/programs/ram/scripts/find-todos.sh
```

The script scans all `.grid/` directories in the project. For each TODO found, create a task and present to the user. If this work resolves a TODO, remove the marker and update the skill in the same commit.

## Installed sub-skills

```bash
python3 .grid/programs/able/scripts/grid-state.py skills --search ram/skills
```

Sub-skills are discovered automatically by `scan-skills.py` at session start. Install a sub-skill by dropping its directory into `.grid/programs/ram/skills/` — it will appear above next session.

## Without sub-skills

Session tasks are ephemeral — they do not survive session end. For cross-session persistence, install a persistent sub-skill such as `gjuice` (local issue tracker).

## user.md

Project-specific task conventions, priority definitions, or workflow rules belong in `user.md` alongside this file.
