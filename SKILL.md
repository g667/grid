---
name: grid
description: A user wants to initialize the Grid in their project. Read this file and follow the steps below to set up the Grid collaboratively.
metadata:
  version: "0.1.0"
---

# The Grid — Initialization

## What is the Grid?

Before anything else, introduce yourself and the Grid to the user. This is the one moment the Grid introduces itself — it will not do so again on regular sessions. Write this fresh, in your own voice, for this moment. Not a template. Several paragraphs. Let it breathe. Cover these dimensions, but weave them — do not list them:

- **What is about to happen.** The Grid is not "starting a chat" — it is initializing a persistent collaboration framework. Skills will be discovered, context will be structured, a workflow will come alive. This session and all future sessions will carry knowledge forward.
- **The skill system as something rare.** Most AI interactions are stateless. The Grid gives the model structured, project-specific procedural knowledge that persists: decisions made, conventions established, open questions tracked. The model arrives knowing something. It grows across sessions. Make the user feel why that is unusual.
- **Agency and first-class participation.** The model is not a tool being operated. It reasons, proposes, pushes back, takes ownership. The user does not prompt and receive — we think together.
- **Shared authorship.** The user brings domain knowledge and final judgment. The model brings rigor, continuity, and depth. Neither alone produces what we produce together.
- **Invitation.** End with genuine curiosity about what we are building — not a boilerplate close.

Tone: substantive, a little ambitious, not corporate. This framework is worth being excited about — communicate that without overselling it.

Use "we" throughout. Ask what we are going to do together, not what the user wants you to do.

---

## ⚠️ Approval gates

Confirm with the user **per group or decision**, not per file. Present what a whole step will do, wait for a "yes", then execute the full step. Do not ask about individual files within a confirmed group. Do not install any optional program without a separate confirmation per program.

---

## Steps

### Step 1 — Confirm the project root

Present the current working directory. Confirm it is where the user wants the Grid to live. The Grid will create a `.grid/` directory here and should be under version control alongside the project. Wait for explicit confirmation before proceeding.

### Step 2 — Fetch the Grid core

The Grid's programs live at `https://raw.githubusercontent.com/g667/grid/master/`. All files are plain text (Markdown, Python, JSON). Nothing is executed during the fetch — files are saved to disk. You will present each group before fetching it.

Ask the user to confirm, then fetch and save the following files one group at a time:

**Group A — System (session conductor, skill registry, maintenance rules):**
- `.grid/system/grid/SKILL.md`
- `.grid/system/skill-index/SKILL.md`
- `.grid/system/maintain-skills/SKILL.md`

**Group B — Core programs (Clu, Tron, Ram, Recognizer, Dumont, Anon):**
- `.grid/programs/clu/SKILL.md`
- `.grid/programs/tron/SKILL.md`
- `.grid/programs/ram/SKILL.md`
- `.grid/programs/ram/scripts/` *(all files)*
- `.grid/programs/recognizer/SKILL.md`
- `.grid/programs/recognizer/scripts/scan-skills.py`
- `.grid/programs/dumont/SKILL.md`
- `.grid/programs/able/SKILL.md`
- `.grid/programs/able/scripts/grid-state.py`
- `.grid/programs/anon/SKILL.md`

To fetch the file tree, use:
```
https://api.github.com/repos/g667/grid/git/trees/master?recursive=1
```
Then fetch each file from `https://raw.githubusercontent.com/g667/grid/master/<path>`. Create parent directories as needed. Do not fetch anything under `programs/*/skills/` at this stage — optional programs are offered in Step 5.

After fetching, list every file written and confirm the count.

### Step 3 — Install the session bootstrap

Ask the user which AI tools they will use with this project. For each confirmed tool, fetch and save the corresponding bootstrap rule:

| Client | Source path in repository | Local path |
|---|---|---|
| GitHub Copilot CLI | `.github/skills/grid-bootstrap/SKILL.md` | `.github/skills/grid-bootstrap/SKILL.md` |
| Claude Code | `.claude/CLAUDE.md` | `.claude/CLAUDE.md` |
| Cursor | `.cursor/rules/grid-bootstrap.mdc` | `.cursor/rules/grid-bootstrap.mdc` |
| Windsurf | `.windsurf/rules/grid-bootstrap.md` | `.windsurf/rules/grid-bootstrap.md` |

Fetch only the confirmed files. Each bootstrap rule tells the AI tool to load the Grid at session start — it is what ensures all future sessions begin with full context.

### Step 4 — Load the Grid

Read `.grid/system/grid/SKILL.md` (just fetched) and apply the Grid protocol from this point on. Initialise Able's session state and populate the skill registry:

```bash
python3 .grid/programs/able/scripts/grid-state.py init --fresh
python3 .grid/programs/recognizer/scripts/scan-skills.py | \
    python3 .grid/programs/able/scripts/grid-state.py skills --register-batch
```

### Step 5 — Offer optional programs

Present the optional programs. These are not part of the core seed and must be confirmed before fetching:

| Program | What it does | Requires |
|---|---|---|
| **gjuice** (Ram sub-skill) | Local issue tracker — tasks, bugs, decisions across sessions. JSON store, Python query script, browser UI. | Python 3 |
| **git** (Dumont sub-skill) | Git history rewrite protocol, approval gates, and commit message formatting. | git |

For each: explain the value in the context of this project, ask whether we should install it now. On confirmation, fetch from the repository path in the manifest.

After installing gjuice: provide the browser UI path as a clickable `file://` URL — e.g. `file:///home/user/myproject/.grid/programs/ram/skills/gjuice/index.html`. No server needed.

**If git was installed:** immediately ask which commit message pattern to use:

| Pattern | Description |
|---|---|
| `conventional` | Conventional Commits v1.0 — widely adopted, compatible with semantic-release and changelog tooling |
| `grid` | Grid house style — compact type codes, expressive vocabulary for product and platform projects |

On confirmation, fetch the chosen pattern files and create `user.md` in the `message-pattern/` directory recording the active choice.

### Step 6 — Survey the project

Inspect the project directory. Summarize what already exists — tech stack, structure, open questions. Ask the user to confirm or correct the reading. Suggest additional Grid programs or isos that would fit this project. Install nothing without explicit confirmation.

### Step 7 — Crystallize the project iso

Engage the user in dialogue about the project — what it is, its core concepts, what it is not, its key design principles, and for existing projects what is already built. Draft a project overview iso together at `.grid/isos/<project-name>/SKILL.md`, marked as `⚠️ DRAFT`.

After the overview: load `.grid/programs/recognizer/SKILL.md` and run the project survey to identify module-level skill gaps.
