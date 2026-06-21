---
name: able
description: Load when storing or querying session state — discovered skills, workflow triggers, active tasks, or workflow step progress. Able is the Grid's central session state manager. Other programs delegate all persistence to him.
metadata:
  version: "0.1.0"
  suggests: "store state | session tasks | skill registry | triggers | what is loaded | active state | workflow step"
---

# Able — Session State Manager

Able runs the garage. He tracks what is active, what is loaded, what needs doing. Other programs tell him what to remember — he stores it, validates it, and gives it back after compaction.

State lives in `assets/state/` — gitignored, never versioned, never shared between teammates. New session → `grid-state.py init --fresh` → clean slate.

## State domains and owners

| Domain | File | Owner (writes) | Consumers (reads) |
|---|---|---|---|
| `skill_cache` | `skill_cache.json` | Recognizer | all programs |
| `triggers` | `triggers.json` | Grid (seeded at init) | Tron |
| `tasks` | `tasks.json` | Ram | Ram, Clu |
| `workflow` | `workflow.json` | Clu | all programs |

No program writes to `assets/state/` directly. All access goes through `grid-state.py`.

## Session start

```bash
python3 .grid/programs/able/scripts/grid-state.py init --fresh
python3 .grid/programs/recognizer/scripts/scan-skills.py | \
    python3 .grid/programs/able/scripts/grid-state.py skills --register-batch
```

## API — Recognizer

```bash
# Register all discovered skills (JSON array from scan-skills.py on stdin)
# --replace clears the cache first (full rebuild — removes orphaned skills)
grid-state.py skills --register-batch
grid-state.py skills --register-batch --replace

# Register a single skill
grid-state.py skills --register --path <path> --description <text> [--suggests <text>]

# Mark a skill as loaded into context this session
grid-state.py skills --mark-loaded <path>
grid-state.py skills --mark-loaded <path> --unload

# Query
grid-state.py skills
grid-state.py skills --loaded
grid-state.py skills --search <query>

# Show dependency mesh for a skill (outgoing cross-links + which skills link to it)
grid-state.py skills --links <name>
```

## API — Tron

```bash
# Read all workflow gates
grid-state.py triggers

# Filter to relevant phase
grid-state.py triggers --phase <query>
```

Triggers are seeded by the Grid conductor at init. Tron reads but never modifies them.

## API — Ram

```bash
# Add a task
grid-state.py tasks --add --title "Doing X" [--description "Details"]

# Update status
grid-state.py tasks --done <id>
grid-state.py tasks --update <id> --status in_progress

# Query
grid-state.py tasks
grid-state.py tasks --status pending
```

## API — Grid conductor

```bash
# Initialise all state for new session
grid-state.py init [--fresh]

# Print all active state in one pass (workflow + triggers + loaded skills + tasks)
grid-state.py recover

# Workflow step tracking
grid-state.py workflow                    # show all steps
grid-state.py workflow --step 3 --done    # mark step 3 done
grid-state.py workflow --step 3 --reset   # revert step 3
grid-state.py workflow --reset-all        # reset on new task
```

## Schema validation

Able rejects invalid payloads:
- Skills must have `path` (non-empty) and `description` (non-empty)
- Tasks must have `title` (non-empty)
- Invalid entries are rejected with an error message; valid entries in a batch proceed

## skill_cache entry schema

| Field | Type | Source | Description |
|---|---|---|---|
| `path` | string | frontmatter → scan | Skill directory path (relative to project root). Primary key. |
| `name` | string\|null | frontmatter `name:` | Human-readable identifier. Must be unique across the project. |
| `description` | string | frontmatter `description:` | When and why to load this skill. |
| `suggests` | string\|null | frontmatter `metadata.suggests` | Pipe-separated trigger phrases for proactive suggestions. |
| `links` | list\|null | frontmatter `metadata.links` | Cross-link entries: `[{skill: <name>, on: <context>}]` |
| `loaded` | 0\|1 | session | Whether the full SKILL.md has been read this session. |
