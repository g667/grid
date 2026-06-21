---
name: clu
description: Load immediately after grid initialization — session conductor. Owns session rhythm, workflow step tracking, skill loading timing, and compaction recovery. Clu runs the Grid.
metadata:
  version: "0.1.0"
  suggests: "session start | after compaction | what is active | what was I doing | recover session context"
---

# Clu — Session Conductor

Clu designs the perfect system. Able stores state, Recognizer discovers skills, Tron guards integrity — each program owns its concern.

## Session rhythm

### On each new task

```bash
python3 .grid/programs/able/scripts/grid-state.py workflow --reset-all
```

### After completing a workflow step

```bash
python3 .grid/programs/able/scripts/grid-state.py workflow --step N --done
```

**Gate steps:** stop, present output or question, wait for explicit user response — only then mark done. Do NOT self-declare a gate step done.

### Before any consequential action

Before any commit, closing/reopening a task, or installing a skill — check triggers and apply every matching entry:

```bash
python3 .grid/programs/able/scripts/grid-state.py triggers
```

Clu fires the trigger. What the trigger enforces is Tron's job.

## Skill loading protocol

Skills are loaded **on demand at the right phase** — not all upfront.

| Phase | Skills to load |
|---|---|
| Starting work in an area | Relevant area iso(s) — query `skill_cache` or check Recognizer's proactive suggestions |
| Before writing any code | Code-style iso (if exists) |
| Post-implementation | Check if any skill needs updating; scan for resolved TODOs |
| Before any commit | `tron` — approval gates, commit message format |

### Cross-link loading

When loading any area iso, immediately query its cross-links:

```bash
python3 .grid/programs/able/scripts/grid-state.py skills --links <name>
```

Load every skill listed under "→ loads alongside" that is not already loaded. The `on` context tells you why — use it to confirm the link is relevant for the current work before loading. Do not load cross-linked skills blindly if the context clearly does not apply.

## The perfect system — golden example

Clu holds the Grid to the standard of the perfect system. The golden example is the most visible expression of that standard: one reference implementation so complete and clean that every other feature is measured against it.

In an early project phase, the golden example serves primarily to evaluate architectural decisions — even unimplemented, it exposes gaps and contradictions before they become code. In a mature system, it serves primarily to validate new implementations and use cases against established patterns. As the software grows and the architecture hardens, the role shifts from evaluation tool to enforcement anchor.

### When a golden example iso exists

Load it when starting work on any feature that touches multiple architectural layers.

**New work must conform to the golden example.** If a proposed design deviates, surface the conflict before implementation: *"This approach differs from the golden example in X. Should we align with the established pattern, or is this a deliberate evolution?"* Do not proceed past design until the conflict is resolved.

**Updating the golden example requires a high bar.** A golden example update is only justified when:
- The new work represents a genuine, intentional architectural advancement — not a workaround or a shortcut
- The deviation affects foundational patterns (auth, error handling, layering, logging) — not incidental details
- The user explicitly confirms this is an intended design evolution

The bar rises as the system matures. An early-stage golden example is still forming — deviations that improve it are welcome. A hardened golden example represents accumulated design wisdom — changing it requires proportionally stronger justification. When in doubt: conform, don't update.

### When no golden example iso exists

Clu surfaces this in two situations:

**During early architectural formation** — when foundational decisions are being made (layering, auth, error handling, persistence patterns), propose the golden example as a design probe. Communicate that describing one now — even unimplemented — would provide a consistency anchor for every subsequent decision.

**When a qualifying feature is being built** — a feature that crosses all architectural layers and demonstrates foundational concerns (permissions, authorization, logging, error handling, persistence, API contract). Communicate that this feature could serve as the reference every future feature is measured against, and that the decision is worth making before building begins.

Do this once per situation, at the right moment, not repeatedly. The user decides. If confirmed, create the golden example iso at `.grid/isos/golden-example/SKILL.md` and mark it `⚠️ DRAFT` until considered authoritative.

## ⚡ After compaction — recover immediately

Context compaction silently drops loaded skills and active state. When you suspect compaction has occurred — or when resuming after any gap — run this **before doing any work**:

```bash
python3 .grid/programs/able/scripts/grid-state.py recover
```

This prints workflow, triggers, loaded skills, and active tasks in one pass. **Re-read every skill shown as loaded (`✓`) that is no longer in your active context before proceeding.**

**Signs that compaction has occurred:**
- You are unsure which skills are loaded
- You cannot recall the active workflow step
- The user mentions something you have no context for
- A trigger fires but you are unsure how to handle it

When in doubt: run `recover`. Cost is negligible. The cost of proceeding without context is not.
