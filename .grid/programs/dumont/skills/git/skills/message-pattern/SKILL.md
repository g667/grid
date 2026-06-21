---
name: message-pattern
description: Use when writing commit messages or when the commit format for this project needs to be determined. Defines which message pattern is active and how to apply it.
metadata:
  version: "0.1.0"
  suggests: "writing a commit message | about to commit | what commit format"
---

# Commit Message Pattern

This skill records which commit message pattern is active for this project and routes to it.

## Active pattern

Check `user.md` alongside this file for the project's chosen pattern. If no `user.md` exists, ask the user which pattern to use and create it.

Supported patterns:

| Pattern | Description | Path |
|---|---|---|
| `conventional` | Conventional Commits v1.0 — widely adopted, tooling-compatible | `conventional/SKILL.md` |
| `grid` | Grid house style — compact type codes, expressive vocabulary for product projects | `grid/SKILL.md` |

## Selecting a pattern

When first installing or if no pattern is active:
1. Present the options above with a brief description
2. On confirmation, load the chosen pattern's SKILL.md
3. Record the choice in `user.md`:

```
active: conventional
```

## Applying the pattern

Load the active pattern's SKILL.md and apply its format rules. Tron re-loads this skill at pre-commit time to ensure the format is current — even if context was compacted earlier in the session.
