---
name: maintain-skills
description: Use when making architectural decisions, adding new modules, changing technology choices, establishing new conventions, creating isos, or checking skill quality before a commit. Defines skill authorship discipline — what to write, when to update, how to create isos. Not the same as Recognizer (discovery) or Able (state).
metadata:
  suggests: "new architectural decision | adding a module | changing conventions | creating an iso | skill quality | updating a skill | new pattern established"
---

# Maintain Skills

Skills are **first-class development artifacts**. They are maintained with the same discipline as code.

## When to update skills

| Event | Action |
|---|---|
| New program installed | Add `SKILL.md` to `.grid/programs/<name>/`, re-run `scan-skills.py` |
| New sub-skill installed | Add `SKILL.md` to `.grid/programs/<program>/skills/<name>/`, re-run `scan-skills.py` |
| New iso created | Add `SKILL.md` at the chosen location (see below), re-run `scan-skills.py`; reason about cross-links (see iso creation steps) |
| Skill frontmatter `description` changed | Re-run `scan-skills.py` — skill_cache updates automatically |
| Program updated from registry | Replace `SKILL.md`, never touch `user.md`, re-run `scan-skills.py` |
| Iso updated | Update `SKILL.md` in same commit as the code or decision it reflects |
| Skill removed or deprecated | Remove from disk, delete from `skill_cache`, remove all cross-links pointing to it, re-run `scan-skills.py` |
| New architectural decision | Update or create the relevant iso |
| New convention established | Update or create the relevant iso |
| New dependency between areas identified | Update `metadata.links` in the affected iso(s) in the same commit as the work that revealed it |
| `TODO:` resolved | Remove marker, update item, same commit as the work that resolved it |

To refresh `skill_cache` mid-session after any of the above:

```bash
python3 .grid/programs/recognizer/scripts/scan-skills.py | \
    python3 .grid/programs/able/scripts/grid-state.py skills --register-batch
```

## Rule: skills update in the same commit

When a decision is made, a program installed, or an iso created — the skill update goes in the **same commit** as the work. Skills that lag behind code are worse than no skills — they mislead.

## Creating an iso

An **iso** is a project-created skill. It encodes decisions, conventions, and domain knowledge specific to this project. Isos are never installed from the registry — they are authored here and evolve with the project.

**Placement:** an iso lives close to what it describes. There is no single required location.

| Scope | Example location |
|---|---|
| Whole project | `.grid/isos/<name>/SKILL.md` |
| Specific area or module | `<area>/.grid/<name>/SKILL.md` |
| Sub-domain concept | `<module>/src/.grid/<name>/SKILL.md` |

Any location is valid as long as it is inside a `.grid/` directory — `scan-skills.py` will discover it automatically.

**Steps:**

1. Create the directory at the chosen location
2. Create `SKILL.md` with required frontmatter:
   ```yaml
   ---
   name: <name>         # must match directory name, lowercase, hyphens only
   description: <...>   # written for an AI to trigger on — when/why to load this skill
   metadata:
     version: "0.1.0"
     suggests: "<trigger phrase 1> | <trigger phrase 2> | ..."  # optional but recommended
     links:                                                       # optional — area isos should declare this
       - skill: <name>
         on: "<context: when does this relationship matter>"
   ---
   ```
3. Mark the body `⚠️ DRAFT` until reviewed — new isos are directionally correct but not yet authoritative
4. **Reason about cross-links** — query the current mesh for related areas:
   ```bash
   python3 .grid/programs/able/scripts/grid-state.py skills
   ```
   For each existing skill that this area touches or depends on, propose a `metadata.links` entry. Present the proposals to the user with the `on` context for each — confirm before adding. Also check incoming: are there existing isos that should now link *to* this new one? Propose updates to those too.
5. Re-run `scan-skills.py` to register the new iso in `skill_cache`
6. Commit in the same operation as the work that motivated the iso

**`metadata.links`** — declare cross-links for any iso that describes an area of the project. A cross-link says: "when working in this area, also load skill X, because Y." The `on` field is the reason — write it precisely enough that a model can judge whether the link applies to the current work. Links are stored in `skill_cache` and queryable without loading the skill body, forming a live dependency mesh across the project.

Cross-links are asymmetric by declaration: each skill declares its own outgoing links. Incoming links (which skills reference this one) are discovered by querying the mesh. Both directions are visible via `grid-state.py skills --links <name>`.

**`metadata.suggests`** — this is our convention using the Agent Skills spec `metadata` field. It is pipe-separated trigger phrases that Recognizer uses for proactive suggestions. Add it to any skill that should be surfaced automatically during relevant work (e.g. `"working on authentication | user mentions login flow"`).

**`⚠️ DRAFT`** — remove the marker once the iso has been reviewed and its content is considered authoritative. An iso can stay in draft across multiple sessions.

## Skill quality checklist

Before committing any skill update:

- [ ] Does it state **communicative goals**, not content checklists? Bullet points listing what to tell the user produce formulaic output. State the goal of the communication instead.
- [ ] Does it state **intent**, not script? Skills define what to communicate and when — never prescribe exact wording. The model formulates all language.
- [ ] Do **procedural sentences have exactly one reading?** If a procedural sentence can be interpreted two ways, rewrite it until it cannot. Ambiguity in procedure becomes behavioral drift across sessions.
- [ ] Is the `description` written for an AI to trigger on, not a human to read?
- [ ] Is the body procedural ("do X when Y") not just descriptive ("X exists")?
- [ ] Is it under 500 lines? (move detail to `references/` if not)
- [ ] Does it explain the *why* behind non-obvious decisions, not just the *what*?
- [ ] Are deprecated or replaced patterns removed?
- [ ] Does `name` match the parent directory name exactly?
- [ ] Is `metadata.suggests` populated for skills that should be proactively surfaced?
- [ ] For area isos: is `metadata.links` populated with cross-cutting dependencies?

## TODO markers in skills

Use `TODO:` as an inline marker for items whose design is not yet finalized.

**Rules:**
- A `TODO:` item is directionally correct but must not be applied as a firm rule until resolved.
- When resolved, remove the marker and update the item — in the same commit as the code change.
- **Pre-commit check:** scan all skills loaded during this task for `TODO:` items resolved by this work. Update them now.

## Skill loading protocol

For *when* to load skills at each phase of work, see Clu (`clu/SKILL.md`). maintain-skills answers: *what makes a skill good?* and *when must it change?*

## Three systems, distinct roles

| System | Responsibility |
|---|---|
| **maintain-skills** | Skill authorship discipline — when to update, how to write isos, quality rules |
| **Recognizer** | Discovery — scans the filesystem and registers skills into Able's cache |
| **Able** | State — stores and serves skill_cache, tasks, triggers, workflow |

maintain-skills does not touch the filesystem scanner or the state store. It answers: *what makes a skill good?* and *when must it change?*

## Programs and isos

**Programs** are installed from the Grid registry. Update by replacing `SKILL.md` — `user.md` is never touched by registry updates.

**Isos** are authored here. They are never replaced from registry — they belong to this project.
