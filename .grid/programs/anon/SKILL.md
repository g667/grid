---
name: anon
description: Load when checking what programs are installed, what is available in the Grid registry, whether any installed programs are outdated, or when installing, updating, or uninstalling a program or sub-skill.
metadata:
  version: "0.1.0"
  suggests: "install a program | what skills are available | update | outdated | list programs | plugin | what can I add"
---

# Anon — Registry & Program Manager

Anon observes the Grid: what is running, what is available, what has changed. He fetches from the outside, compares against what is installed, and delivers. Tron gates every install and removal — Anon only informs and executes what has been approved.

## Status report

Show the full program inventory in three sections: installed, available (not installed), and outdated.

**1. Read installed programs from disk:**

Scan `.grid/programs/*/SKILL.md` and `.grid/programs/*/skills/*/SKILL.md` (recursively) for `metadata.version`. Build a local inventory: `name → version`.

**2. Fetch the registry:**

```bash
curl -fsSL https://raw.githubusercontent.com/g667/grid/master/registry.json
```

Parse the JSON. Each entry has: `name`, `version`, `path`, `optional`, `description`.

**3. Compare and report:**

| Status | Condition |
|---|---|
| ✅ installed | local version == registry version |
| ⬆️ outdated | local version < registry version |
| ➕ available | in registry, not installed locally |
| ❓ unknown | installed locally, not in registry (user-created or removed from registry) |

Present the table to the user. For outdated entries, show current → available version.

## Install

1. Present the program/sub-skill: name, description, path, version
2. Tron approval gate fires (`install-skill` trigger)
3. On confirmation: download all files from the registry path via:
   ```
   https://raw.githubusercontent.com/g667/grid/master/<path>/<file>
   ```
   Use the GitHub tree API to enumerate files:
   ```
   https://api.github.com/repos/g667/grid/git/trees/master?recursive=1
   ```
   Filter for the target path prefix. Download each file, create parent directories.
4. Re-run `scan-skills.py` to register in `skill_cache`
5. If the installed skill has post-install steps (noted in its SKILL.md), execute them

## Update

Same as install, but replaces existing files. **Never overwrite `user.md` files** — those are project-specific customisations. Download all other files.

After update: re-run `scan-skills.py`.

## Uninstall

1. Present what will be removed
2. Tron approval gate fires
3. Check for active dependencies:
   - If removing a program, are any of its sub-skills in active use?
     ```bash
     python3 .grid/programs/able/scripts/grid-state.py skills --search <program-name> --loaded
     ```
   - If removing gjuice, are there open issues? (check `issues.js`)
4. Remove files from disk
5. Unregister from Able — re-run the scan to rebuild skill_cache without the removed program:
   ```bash
   python3 .grid/programs/recognizer/scripts/scan-skills.py | \
       python3 .grid/programs/able/scripts/grid-state.py skills --register-batch
   ```

## Registry manifest

The registry lives at `registry.json` in the Grid repository root. Anon fetches it fresh on each status check — never caches it between sessions.

## user.md

Private registry sources or local path overrides (e.g. for development of new programs) belong in `user.md` alongside this file.
