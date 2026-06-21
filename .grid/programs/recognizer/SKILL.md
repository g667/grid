---
name: recognizer
description: Load when scanning the project for skill gaps, when unsure which skills are relevant for the current task, or when a skill needs to find linked skills by keyword. Recognizer surveys project structure, identifies areas without skills, and queries the skill index.
metadata:
  version: "0.1.0"
  suggests: "missing skill | skill gap | what skills exist | scanning skills | is there a skill for | new area without skill"
---

# Recognizer — Skill Scanner

Recognizer has two jobs: find skills that already exist but aren't loaded, and find areas of the project that have no skill yet.

## 1. Project survey — find skill gaps

Use this during initialization or any time the project has grown and skills may be missing.

Get all known skill paths from Able:

```bash
python3 .grid/programs/able/scripts/grid-state.py skills
```

Walk the project directories. For each significant area (module, package, service, domain concept) check whether a skill exists for it. An area is significant if it has its own directory with non-trivial content.

For each gap found:
- Present the area to the user with a one-line description of what it does
- Ask whether we should create an iso for it
- If confirmed, create the iso at the appropriate location (see `maintain-skills` for placement options) in dialogue — never draft unilaterally
- Re-scan and register: `scan-skills.py | grid-state.py skills --register-batch`

Run this survey collaboratively, not as a batch. One area at a time.

## 2. Find skills by keyword

```bash
python3 .grid/programs/able/scripts/grid-state.py skills --search <keyword>
```

## 3. Find unloaded skills for the current area

```bash
python3 .grid/programs/able/scripts/grid-state.py skills --search <area>
# then filter results where loaded = ' ' (not ✓)
```

## 4. List all loaded skills this session

```bash
python3 .grid/programs/able/scripts/grid-state.py skills --loaded
```

## 5. Mark a skill as loaded

After reading a SKILL.md, tell Able:

```bash
python3 .grid/programs/able/scripts/grid-state.py skills --mark-loaded <path>
```

## 6. Scan for unregistered skills

`skill_cache` is populated by `scan-skills.py` at session start — not manually. To re-scan mid-session (e.g. after installing a new skill):

```bash
python3 .grid/programs/recognizer/scripts/scan-skills.py | \
    python3 .grid/programs/able/scripts/grid-state.py skills --register-batch
```

This script:
- Walks the project from root, finding all `.grid/` directories (pruning `.git`, `node_modules`, `build`, `dist`, etc.)
- Inside each `.grid/` dir, locates every `SKILL.md`
- Parses frontmatter for `name`, `description`, `metadata.suggests`, and `metadata.links`
- Outputs a JSON array to stdout; Able validates and stores it

Skills without a `description` frontmatter field are silently skipped.

## Name uniqueness — enforcement

Skill names must be unique across the entire project. `scan-skills.py` detects collisions at scan time and prints a warning to stderr:

```
⚠️  Name collision: 'git' used by 2 skills:
     .grid/programs/dumont/skills/git
     src/payments/.grid/git-utils
```

**Cross-links reference skills by name.** A collision makes the reference ambiguous and the dependency mesh unreliable. Resolve every collision before relying on `--links` queries.

To resolve: rename one skill's `name` field (and its directory if desired) to something more specific. Names should reflect the concern precisely — `payments-service` not `service`, `rest-layer` not `layer`.

## How other skills use Recognizer

> *"I'm about to write a commit. Recognizer, find skills related to git and commits."*

```bash
python3 .grid/programs/able/scripts/grid-state.py skills --search git
python3 .grid/programs/able/scripts/grid-state.py skills --search commit
```

## user.md

Project-specific scan paths, exclusion patterns, or area definitions belong in `user.md` alongside this file.

## Proactive suggestions

After each user message, check whether any unloaded skill is relevant:

```bash
python3 .grid/programs/able/scripts/grid-state.py skills
# read 'suggests' field of unloaded skills; match against current user intent
```

The `suggests` field contains pipe-separated trigger phrases from `metadata.suggests` in the skill's frontmatter. If any trigger phrase matches the user's intent — even loosely — surface it:

> *"Gjuice is available and not yet set up. It tracks issues and decisions across sessions — relevant here. Want to initialize it?"*

Keep the suggestion brief and non-intrusive. One suggestion at a time. Only suggest when the match is clear — do not suggest speculatively.
