#!/usr/bin/env python3
"""
grid-state.py — Query and mutate Grid active-state JSON files.

Manages three state stores under .grid/programs/able/assets/state/:
  skill_cache.json   — discovered skills and loaded flags
  triggers.json      — workflow trigger rules
  tasks.json         — session task list
  workflow.json      — session workflow step statuses

Usage:
  python3 .grid/programs/able/scripts/grid-state.py skills
  python3 .grid/programs/able/scripts/grid-state.py skills --loaded
  python3 .grid/programs/able/scripts/grid-state.py skills --search git
  python3 .grid/programs/able/scripts/grid-state.py skills --mark-loaded .grid/programs/tron
  python3 .grid/programs/able/scripts/grid-state.py skills --mark-loaded .grid/programs/tron --unload
  python3 .grid/programs/able/scripts/grid-state.py skills --register-batch          # merge
  python3 .grid/programs/able/scripts/grid-state.py skills --register-batch --replace  # full rebuild

  python3 .grid/programs/able/scripts/grid-state.py triggers
  python3 .grid/programs/able/scripts/grid-state.py triggers --phase commit

  python3 .grid/programs/able/scripts/grid-state.py tasks
  python3 .grid/programs/able/scripts/grid-state.py tasks --status pending
  python3 .grid/programs/able/scripts/grid-state.py tasks --add --title "Doing X" --description "Details"
  python3 .grid/programs/able/scripts/grid-state.py tasks --done <id>
  python3 .grid/programs/able/scripts/grid-state.py tasks --update <id> --status in_progress

  python3 .grid/programs/able/scripts/grid-state.py init --fresh
    Writes default triggers, workflow, and empty tasks. Always use --fresh at session start.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

# State lives at: <project_root>/.grid/programs/able/assets/state/
# Script lives at: <project_root>/.grid/programs/able/scripts/grid-state.py
def _find_state_dir():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    state = os.path.normpath(os.path.join(script_dir, '..', 'assets', 'state'))
    os.makedirs(state, exist_ok=True)
    return state

STATE_DIR      = _find_state_dir()
SKILLS_FILE    = os.path.join(STATE_DIR, 'skill_cache.json')
TRIGGERS_FILE  = os.path.join(STATE_DIR, 'triggers.json')
TASKS_FILE     = os.path.join(STATE_DIR, 'tasks.json')

DEFAULT_TRIGGERS = [
    {"id": "load-area-skill", "phase": "Starting work in an area",          "instruction": "Load the relevant skill before writing any code. Query skill_cache for candidates."},
    {"id": "scan-todos",      "phase": "Post-implementation",               "instruction": "Scan loaded skill files for TODO: markers resolved by this work. Update skills in same commit."},
    {"id": "update-skill",    "phase": "After any code change",             "instruction": "Check whether any skill needs updating. If a new dependency between areas emerged, update metadata.links in the affected iso(s). See maintain-skills."},
    {"id": "pre-commit",      "phase": "Before any commit",                 "instruction": "Load tron. Run the pre-commit checklist. Get user approval for commit message."},
    {"id": "close-task",      "phase": "Before closing any task or issue",  "instruction": "Load tron. Present the task/issue and get explicit user confirmation before marking done."},
    {"id": "reopen-task",     "phase": "Before reopening a completed task", "instruction": "Load tron. Present the task and confirm before reopening."},
    {"id": "install-skill",   "phase": "Before installing any skill",       "instruction": "Load tron. Present what will be installed, where it lands, and what it does. Get explicit confirmation."},
]

WORKFLOW_FILE = os.path.join(STATE_DIR, 'workflow.json')

DEFAULT_WORKFLOW = [
    {"step": 1, "title": "Identify task",                 "status": "pending", "gate": False},
    {"step": 2, "title": "Clarify and propose solutions", "status": "pending", "gate": True},
    {"step": 3, "title": "User chooses approach",         "status": "pending", "gate": True},
    {"step": 4, "title": "Load relevant skills",          "status": "pending", "gate": False},
    {"step": 5, "title": "Implement and update skills",   "status": "pending", "gate": False},
    {"step": 6, "title": "Review and refine with user",   "status": "pending", "gate": True},
    {"step": 7, "title": "User accepts result",           "status": "pending", "gate": True},
    {"step": 8, "title": "Skill quality checklist",       "status": "pending", "gate": True},
    {"step": 9, "title": "Commit",                        "status": "pending", "gate": True},
]


# ── I/O helpers ──────────────────────────────────────────────────────────────

def _load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def _save(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')

def _now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# ── Skills ───────────────────────────────────────────────────────────────────

SKILL_SCHEMA = {'path', 'description'}  # required fields

def _validate_skill(entry):
    missing = SKILL_SCHEMA - set(entry.keys())
    if missing:
        raise ValueError(f"Skill entry missing required fields: {missing} — got {entry}")
    if not entry['path'] or not entry['description']:
        raise ValueError(f"Skill 'path' and 'description' must be non-empty — got {entry}")

def cmd_skills(args):
    skills = _load(SKILLS_FILE, [])
    if not skills:
        print("skill_cache is empty. Run: scan-skills.py | grid-state.py skills --register-batch")
        return

    # --links <name>: show dependency mesh for a skill
    if getattr(args, 'links', None):
        _cmd_skills_links(skills, args.links)
        return

    results = skills
    if args.loaded:
        results = [s for s in results if s.get('loaded')]
    if args.search:
        q = args.search.lower()
        results = [s for s in results if q in s.get('path','').lower()
                   or q in (s.get('name') or '').lower()
                   or q in (s.get('description') or '').lower()
                   or q in (s.get('suggests') or '').lower()]

    if not results:
        print("No skills matched.")
        return

    col_w = max(len(s['path']) for s in results)
    print(f"{'PATH':<{col_w}}  {'L'}  DESCRIPTION")
    print('-' * (col_w + 50))
    for s in results:
        loaded = '✓' if s.get('loaded') else ' '
        desc = (s.get('description') or '')[:60]
        print(f"{s['path']:<{col_w}}  {loaded}  {desc}")
    print(f"\n{len(results)} skill(s)")


def _cmd_skills_links(skills, name):
    """Show the dependency mesh for a skill identified by name."""
    targets = [s for s in skills if s.get('name') == name]
    if not targets:
        print(f"No skill named '{name}' in skill_cache.")
        return
    if len(targets) > 1:
        print(f"⚠️  Name collision: '{name}' matches {len(targets)} skills — resolve before using as reference:")
        for s in targets:
            print(f"   {s['path']}")
        return

    skill = targets[0]
    outgoing = skill.get('links') or []
    incoming = [s for s in skills if any(lk.get('skill') == name for lk in (s.get('links') or []))]

    print(f"Dependency mesh for '{name}'  ({skill['path']})")
    print()

    if outgoing:
        print("  → loads alongside (outgoing):")
        for lk in outgoing:
            on = f"  — {lk['on']}" if lk.get('on') else ''
            print(f"      {lk['skill']}{on}")
    else:
        print("  → loads alongside: (none)")

    print()

    if incoming:
        print("  ← linked from (incoming):")
        for s in incoming:
            my_links = [lk for lk in (s.get('links') or []) if lk.get('skill') == name]
            for lk in my_links:
                on = f"  — {lk['on']}" if lk.get('on') else ''
                sname = s.get('name') or s['path']
                print(f"      {sname}{on}")
    else:
        print("  ← linked from: (none)")


def cmd_skills_register(args):
    """Register a single skill."""
    entry = {"path": args.path, "name": None, "description": args.description,
             "suggests": args.suggests or None, "links": None, "loaded": 0}
    _validate_skill(entry)
    skills = _load(SKILLS_FILE, [])
    for s in skills:
        if s['path'] == entry['path']:
            s.update({"description": entry['description'],
                      "suggests": entry['suggests'], "links": None, "loaded": 0})
            _save(SKILLS_FILE, skills)
            print(f"Updated: {entry['path']}")
            return
    skills.append(entry)
    _save(SKILLS_FILE, skills)
    print(f"Registered: {entry['path']}")


def cmd_skills_register_batch(args):
    """Register skills from a JSON array on stdin."""
    try:
        entries = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON on stdin: {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(entries, list):
        print("Expected a JSON array on stdin.", file=sys.stderr)
        sys.exit(1)

    # --replace: start with empty index (purges removed skills)
    existing = [] if getattr(args, 'replace', False) else _load(SKILLS_FILE, [])
    index = {s['path']: s for s in existing}
    count_new = count_updated = 0
    for entry in entries:
        try:
            _validate_skill(entry)
        except ValueError as e:
            print(f"Skipping invalid entry: {e}", file=sys.stderr)
            continue
        skill = {"path": entry['path'], "name": entry.get('name'),
                 "description": entry['description'], "suggests": entry.get('suggests'),
                 "links": entry.get('links'), "loaded": 0}
        if entry['path'] in index:
            index[entry['path']].update(skill)
            count_updated += 1
        else:
            index[entry['path']] = skill
            count_new += 1

    result = list(index.values())
    _save(SKILLS_FILE, result)

    # Detect name collisions across the full cache
    name_map = {}
    for s in result:
        n = s.get('name')
        if n:
            name_map.setdefault(n, []).append(s['path'])
    collisions = {n: paths for n, paths in name_map.items() if len(paths) > 1}
    if collisions:
        print(f"⚠️  Name collision(s) detected — resolve before using names as cross-link references:",
              file=sys.stderr)
        for n, paths in sorted(collisions.items()):
            print(f"   '{n}': {', '.join(paths)}", file=sys.stderr)

    print(f"{count_new} registered, {count_updated} updated")


def cmd_mark_loaded(args):
    skills = _load(SKILLS_FILE, [])
    path = args.mark_loaded.rstrip('/')
    matched = False
    for s in skills:
        if s['path'] == path:
            s['loaded'] = 0 if args.unload else 1
            matched = True
            break
    if not matched:
        print(f"Path not found in skill_cache: {path}", file=sys.stderr)
        sys.exit(1)
    _save(SKILLS_FILE, skills)
    state = "unloaded" if args.unload else "loaded"
    print(f"Marked {path} as {state}")


# ── Triggers ─────────────────────────────────────────────────────────────────

def cmd_triggers(args):
    triggers = _load(TRIGGERS_FILE, [])
    if not triggers:
        print("triggers.json not found. Run: grid-state.py init")
        return

    results = triggers
    if args.phase:
        q = args.phase.lower()
        results = [t for t in results if q in t.get('phase','').lower()
                   or q in t.get('id','').lower()]

    for t in results:
        print(f"[{t['id']}]")
        print(f"  Phase:       {t['phase']}")
        print(f"  Instruction: {t['instruction']}")
        print()


# ── Tasks ─────────────────────────────────────────────────────────────────────

def _load_tasks():
    return _load(TASKS_FILE, [])

def _save_tasks(tasks):
    _save(TASKS_FILE, tasks)

def _next_id(tasks):
    if not tasks:
        return 1
    return max(t.get('id', 0) for t in tasks) + 1

def cmd_tasks(args):
    tasks = _load_tasks()

    if args.add:
        if not args.title:
            print("--title required with --add", file=sys.stderr)
            sys.exit(1)
        task = {
            'id':          _next_id(tasks),
            'title':       args.title,
            'description': args.description or '',
            'status':      'pending',
            'created_at':  _now(),
            'updated_at':  _now(),
        }
        tasks.append(task)
        _save_tasks(tasks)
        print(f"Task {task['id']} created: {task['title']}")
        return

    if args.done is not None:
        _update_task(tasks, args.done, {'status': 'done'})
        return

    if args.update is not None:
        updates = {}
        if args.status:
            updates['status'] = args.status
        if args.title:
            updates['title'] = args.title
        if args.description:
            updates['description'] = args.description
        _update_task(tasks, args.update, updates)
        return

    # List
    results = tasks
    if args.status:
        results = [t for t in results if t.get('status') == args.status]
    else:
        results = [t for t in results if t.get('status') != 'done']

    if not results:
        print("No tasks.")
        return

    for t in results:
        status_icon = {'pending': '○', 'in_progress': '►', 'done': '✓', 'blocked': '✗'}.get(t.get('status',''), '?')
        print(f"  [{t['id']:>3}] {status_icon} {t['title']}")
        if t.get('description'):
            print(f"         {t['description'][:80]}")
    print(f"\n{len(results)} task(s)")


def _update_task(tasks, task_id, updates):
    for t in tasks:
        if t.get('id') == task_id:
            t.update(updates)
            t['updated_at'] = _now()
            _save_tasks(tasks)
            print(f"Task {task_id} updated: {updates}")
            return
    print(f"Task {task_id} not found.", file=sys.stderr)
    sys.exit(1)


# ── Workflow ──────────────────────────────────────────────────────────────────

def cmd_workflow(args):
    workflow = _load(WORKFLOW_FILE, [])
    if not workflow:
        print("workflow.json not found. Run: grid-state.py init")
        return

    if args.step is not None:
        for w in workflow:
            if w['step'] == args.step:
                if args.done:
                    w['status'] = 'done'
                elif args.reset:
                    w['status'] = 'pending'
                _save(WORKFLOW_FILE, workflow)
                icon = '✓' if w['status'] == 'done' else '○'
                gate = ' [gate]' if w.get('gate') else ''
                print(f"Step {w['step']}: {icon} {w['title']}{gate}")
                return
        print(f"Step {args.step} not found.", file=sys.stderr)
        sys.exit(1)

    if args.reset_all:
        for w in workflow:
            w['status'] = 'pending'
        _save(WORKFLOW_FILE, workflow)
        print("Workflow reset.")
        return

    # List
    for w in workflow:
        icon = '✓' if w['status'] == 'done' else '○'
        gate = ' ⛔' if w.get('gate') else ''
        print(f"  {w['step']}. {icon} {w['title']}{gate}")


# ── Init ─────────────────────────────────────────────────────────────────────

def cmd_init(args):
    fresh = getattr(args, 'fresh', False)
    written = []
    if fresh or not os.path.exists(TRIGGERS_FILE):
        _save(TRIGGERS_FILE, DEFAULT_TRIGGERS)
        written.append(TRIGGERS_FILE)
    if fresh or not os.path.exists(TASKS_FILE):
        _save(TASKS_FILE, [])
        written.append(TASKS_FILE)
    if fresh or not os.path.exists(WORKFLOW_FILE):
        _save(WORKFLOW_FILE, DEFAULT_WORKFLOW)
        written.append(WORKFLOW_FILE)
    if written:
        for p in written:
            print(f"{'Reset' if fresh else 'Created'}: {p}")
    else:
        print("State files already exist. Use --fresh to reset.")


# ── Recover ───────────────────────────────────────────────────────────────────

def cmd_recover(args):
    """Print all active state in one pass — use after compaction to re-arm context."""
    print("═" * 60)
    print("  GRID STATE RECOVERY")
    print("═" * 60)

    # Workflow
    print("\n── Workflow ──────────────────────────────────────────────")
    workflow = _load(WORKFLOW_FILE, [])
    if not workflow:
        print("  workflow.json not found — run: grid-state.py init --fresh")
    else:
        for w in workflow:
            icon = '✓' if w['status'] == 'done' else '○'
            gate = ' ⛔' if w.get('gate') else ''
            print(f"  {w['step']}. {icon} {w['title']}{gate}")

    # Triggers
    print("\n── Triggers ──────────────────────────────────────────────")
    triggers = _load(TRIGGERS_FILE, [])
    if not triggers:
        print("  triggers.json not found")
    else:
        for t in triggers:
            print(f"  [{t['id']}] {t['phase']}")
            print(f"         → {t['instruction']}")

    # Loaded skills
    print("\n── Loaded skills ─────────────────────────────────────────")
    skills = _load(SKILLS_FILE, [])
    loaded = [s for s in skills if s.get('loaded')]
    if not loaded:
        print("  No skills marked as loaded.")
    else:
        for s in loaded:
            print(f"  ✓ {s['path']}")
            print(f"    {(s.get('description') or '')[:80]}")

    # In-progress tasks
    print("\n── In-progress tasks ─────────────────────────────────────")
    tasks = _load(TASKS_FILE, [])
    active = [t for t in tasks if t.get('status') in ('pending', 'in_progress')]
    if not active:
        print("  No active tasks.")
    else:
        for t in active:
            icon = '►' if t.get('status') == 'in_progress' else '○'
            print(f"  [{t['id']:>3}] {icon} {t['title']}")

    print("\n" + "═" * 60)
    print("  Re-read any loaded skill no longer in active context.")
    print("═" * 60)



def main():
    parser = argparse.ArgumentParser(description='Grid active state manager')
    sub = parser.add_subparsers(dest='command')

    # skills
    p_skills = sub.add_parser('skills', help='Query or register skills')
    p_skills.add_argument('--loaded',           action='store_true', help='Only loaded skills')
    p_skills.add_argument('--search',           metavar='QUERY',     help='Filter by path/name/description/suggests')
    p_skills.add_argument('--links',            metavar='NAME',      help='Show dependency mesh for skill by name')
    p_skills.add_argument('--mark-loaded',      metavar='PATH',      help='Mark a skill as loaded')
    p_skills.add_argument('--unload',           action='store_true', help='Use with --mark-loaded to unload')
    p_skills.add_argument('--register',         action='store_true', help='Register a single skill')
    p_skills.add_argument('--register-batch',   action='store_true', help='Register skills from JSON array on stdin')
    p_skills.add_argument('--replace',          action='store_true', help='Use with --register-batch: clears cache before inserting (full rebuild)')
    p_skills.add_argument('--path',             metavar='PATH',      help='Skill path (with --register)')
    p_skills.add_argument('--description',      metavar='TEXT',      help='Skill description (with --register)')
    p_skills.add_argument('--suggests',         metavar='TEXT',      help='Suggests string (with --register)')

    # triggers
    p_trig = sub.add_parser('triggers', help='Query triggers')
    p_trig.add_argument('--phase', metavar='QUERY', help='Filter by phase or id')

    # tasks
    p_tasks = sub.add_parser('tasks', help='Manage session tasks')
    p_tasks.add_argument('--status',      metavar='STATUS',  help='Filter by status (pending/in_progress/done/blocked)')
    p_tasks.add_argument('--add',         action='store_true')
    p_tasks.add_argument('--title',       metavar='TEXT')
    p_tasks.add_argument('--description', metavar='TEXT')
    p_tasks.add_argument('--done',        metavar='ID',      type=int)
    p_tasks.add_argument('--update',      metavar='ID',      type=int)

    # workflow
    p_wf = sub.add_parser('workflow', help='Track session workflow steps')
    p_wf.add_argument('--step',      metavar='N',   type=int, help='Target step number')
    p_wf.add_argument('--done',      action='store_true',     help='Mark step done')
    p_wf.add_argument('--reset',     action='store_true',     help='Mark step pending')
    p_wf.add_argument('--reset-all', action='store_true',     dest='reset_all', help='Reset all steps to pending')

    # init
    p_init = sub.add_parser('init', help='Initialise all state files for a new session')
    p_init.add_argument('--fresh', action='store_true', help='Overwrite existing state files')

    # recover
    sub.add_parser('recover', help='Print all active state — use after compaction to re-arm context')

    args = parser.parse_args()

    if args.command == 'skills':
        if args.register_batch:
            cmd_skills_register_batch(args)
        elif args.register:
            cmd_skills_register(args)
        elif args.mark_loaded:
            cmd_mark_loaded(args)
        else:
            cmd_skills(args)
    elif args.command == 'triggers':
        cmd_triggers(args)
    elif args.command == 'tasks':
        cmd_tasks(args)
    elif args.command == 'workflow':
        cmd_workflow(args)
    elif args.command == 'init':
        cmd_init(args)
    elif args.command == 'recover':
        cmd_recover(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
