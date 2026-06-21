---
name: skill-index
description: Use at session start to load the full skill registry. Query skill_cache via Able to find and load relevant skills during a session.
metadata:
  version: "0.1.0"
---

# Skill Index

`skill_cache` is the active registry for all skills discovered in the project. It is populated at session start by Recognizer's `scan-skills.py` piped through Able — no manual maintenance required.

## Schema

Each entry in `skill_cache.json` (managed by Able):

| Field | Type | Description |
|---|---|---|
| `path` | string | Skill directory path (relative to project root) |
| `description` | string | What the skill does and when to use it |
| `suggests` | string\|null | Pipe-separated trigger phrases for proactive suggestions |
| `loaded` | 0\|1 | Whether the full SKILL.md has been read this session |

Data is sourced from each skill's frontmatter. The frontmatter IS the registration — no separate index file to maintain.

## Querying

```bash
# Find skills by keyword
python3 .grid/programs/able/scripts/grid-state.py skills --search <keyword>

# Mark a skill as loaded
python3 .grid/programs/able/scripts/grid-state.py skills --mark-loaded <path>

# All loaded skills this session
python3 .grid/programs/able/scripts/grid-state.py skills --loaded
```

## Installing a new skill

1. Create the skill directory and `SKILL.md` with valid frontmatter (`description` required, `metadata.suggests` optional)
2. The skill is automatically discovered next session — no other file to update
3. To register immediately in the current session without restarting:

```bash
python3 .grid/programs/recognizer/scripts/scan-skills.py | \
    python3 .grid/programs/able/scripts/grid-state.py skills --register-batch
```

