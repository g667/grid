---
name: git
description: Use when making git commits, writing commit messages, performing history rewrites, or working with branches. Defines commit message format, approval gates, and history rewrite protocol.
compatibility: Requires git
metadata:
  version: "0.1.0"
  suggests: "about to commit | writing a commit message | rewriting git history | amending a commit | rebasing"
  links:
    - skill: message-pattern
      on: "before writing any commit message — message-pattern determines the active format"
---

# Git Driver

## Commit message format

Commit message format is defined by the active message pattern sub-skill. Load `skills/message-pattern/SKILL.md` to determine which pattern is active, then apply it.

If no pattern is selected yet, present the options and ask the user to choose one before writing the commit message.

## History rewrites

Any operation that rewrites existing commits (amend, rebase, squash, filter-repo) follows this protocol:

**1. Create a backup branch first:**
```bash
git branch rewrites/<short-hint>
```

**2. Perform the rewrite.**

**3. Show the user `git log --oneline` and ask for review.**

**4. State explicitly which branch will be deleted:**
> *"Ready to delete backup branch `rewrites/<short-hint>`. Confirm?"*

**5. Delete only after explicit acknowledgement:**
```bash
git branch -D rewrites/<short-hint>
```

Never delete the backup branch unilaterally.

## Amending the last commit

```bash
git add -A
git commit --amend --no-edit
```

This is a history rewrite — follow the backup protocol above first.

## user.md

Project-specific commit message conventions (e.g. always list updated modules, ticket prefix format, branch naming rules) belong in `user.md` alongside this file.
