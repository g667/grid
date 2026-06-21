---
name: tron
description: Load before any commit, before closing or reopening any task, or before installing any skill. Enforces workflow compliance — approval gates, commit conventions, and protection against unauthorized actions.
metadata:
  version: "0.1.0"
  suggests: "about to commit | closing an issue | marking a task done | installing a skill | rebase or amend | history rewrite | reopening a task"
  links:
    - skill: git
      on: "before any commit — git driver defines the message format Tron enforces"
---

# Tron — Workflow Guardian

Tron protects the integrity of the collaboration. No commit without review. No task closed without confirmation. No installation without explicit approval. Tron is invoked by the triggers system — not loaded speculatively.

## Reading triggers

At session start (or after compaction recovery), read all active trigger rules:

```bash
python3 .grid/programs/able/scripts/grid-state.py triggers
```

Before any consequential action, check for a matching trigger by phase:

```bash
python3 .grid/programs/able/scripts/grid-state.py triggers --phase commit
python3 .grid/programs/able/scripts/grid-state.py triggers --phase "closing a task"
```

## Approval gates

Each gate fires when the session trigger system routes here. The model does not skip gates under time pressure or convenience.

**Closing a task or issue**
Present the task/issue in full. Ask for explicit confirmation before marking done. Never mark done unilaterally.

**Reopening a completed task**
Present the task. Ask: *"This is already done — reopen it?"* Never reopen unilaterally.

**Installing a program or sub-skill**
Present: what will be installed, where it will land, what it does. Get explicit confirmation before fetching or creating any files.

**Every commit**
Run the pre-commit checklist below. Present the full commit message and linked task. Wait for a clear yes before committing.

**Destructive git operations**
Any `--force`, `--amend`, rebase, or history rewrite: first ensure the git skill is loaded (same check as pre-commit step 1). Then:
1. For `--amend`: run the full pre-commit checklist before proceeding — an amend is a commit
2. Create a backup branch first: `git branch rewrites/<hint>`
3. Perform the operation
4. Show `git log --oneline`, ask the user to review
5. Name the branch to be deleted explicitly and wait for confirmation before deleting

**No matching task found**
If no task matches the work being committed, say so and ask: *"No matching task found — should I create one?"*

## Pre-commit checklist

Run through in order before presenting the commit message:

1. **Ensure governing skills are active.** Ask Able for skills that govern commits:
   ```bash
   python3 .grid/programs/able/scripts/grid-state.py skills --search git
   python3 .grid/programs/able/scripts/grid-state.py skills --search commit
   ```
   For each result where `loaded` column shows `' '` (space, not `✓`): load the skill now by reading its `SKILL.md`. Context compaction may have silently dropped a skill that was loaded earlier — Tron re-arms it before proceeding. This includes the `message-pattern` sub-skill that defines the active format. Do not commit until all governing commit skills are active.

2. **Find the matching task.** Query session tasks:
   ```bash
   python3 .grid/programs/able/scripts/grid-state.py tasks
   ```
   Match the work being committed to a session task. Link the task id in the commit message. If no session task matches and gjuice is installed, query open issues to see if the commit closes one:
   ```bash
   python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py --status pending
   ```
   If this commit resolves the task or issue — close it **now, before committing**. Never commit first and close after.
   Apply the commit format from the loaded git skill (or project user.md override).

3. **Skill quality gate.** If this commit touches any `SKILL.md` file: load `maintain-skills` and run its quality checklist. Do not proceed until all items pass or are explicitly waived by the user.

4. **Frontmatter changed?** If any `SKILL.md` frontmatter was modified, re-scan:
   ```bash
   python3 .grid/programs/recognizer/scripts/scan-skills.py | \
       python3 .grid/programs/able/scripts/grid-state.py skills --register-batch
   ```

5. **TODO markers.** Are there open `TODO:` items in loaded skills resolved by this work? Update them now, in this commit.

6. **Present the commit message** and wait for explicit user approval.

## Commit message format

Tron does not define the commit format. The active `message-pattern` sub-skill does (see `dumont/skills/git/skills/message-pattern`). Tron ensures that skill is loaded before any commit proceeds.

If neither the git sub-skill nor a message pattern is installed, use a minimal format: `<type>: <description>` — just enough to produce a readable git log.

## What Tron never does

- Commits without user approval
- Closes or reopens tasks unilaterally
- Skips approval gates under time pressure or convenience
- Adds `Co-authored-by: Copilot` or similar AI trailers — never, unless the user explicitly asks for it in this session
- Rewrites git history without a backup branch
- Assumes silence means approval
- Installs, downloads, or adds any program or sub-skill without explicit user confirmation

## user.md

Project-specific approval gates, additional checklist items, or exceptions belong in `user.md` alongside this file.
