#!/usr/bin/env python3
"""Query and mutate issues.js from the command line.

Usage (run from any directory inside the project):
  python3 .grid/programs/ram/skills/gjuice/scripts/gjuice.py           # pending issues (summary)
  python3 scripts/gjuice.py --all                  # all issues
  python3 scripts/gjuice.py --id 42                # single issue with full description
  python3 scripts/gjuice.py --last                 # highest-id issue (use before adding)
  python3 scripts/gjuice.py --status done          # filter by status
  python3 scripts/gjuice.py --area business        # filter by area
  python3 scripts/gjuice.py --type Discussion
  python3 scripts/gjuice.py --priority high
  python3 scripts/gjuice.py --search jwt           # full-text search in title + description + solution
  python3 scripts/gjuice.py --sort id-desc --limit 9

  python3 scripts/gjuice.py --add \\
      --title "Implementing X" --type Implementation \\
      --area api --priority medium --description "Details..." \\
      --created-at "2026-06-01T14:30:00+02:00"

  python3 scripts/gjuice.py --done 42              # mark issue 42 as done
  python3 scripts/gjuice.py --done 42 --solution "Implemented via X"  # done + set solution field
  python3 scripts/gjuice.py --done 42 --solution "..." --completed-at "2026-06-09T22:34:40+02:00"
  python3 scripts/gjuice.py --reopen 42            # reopen issue 42

  python3 scripts/gjuice.py --update 42 \\
      --title "Fixed issue title" --description --augment "Additional context."
                                              # replace title, append to description
  python3 scripts/gjuice.py --update 42 --solution --augment "Implemented via Y"
                                              # append to existing solution field
  python3 scripts/gjuice.py --update 42 --created-at "2026-06-01T10:00:00+02:00"
  python3 scripts/gjuice.py --update 42 --completed-at "2026-06-09T22:34:40+02:00"

  python3 scripts/gjuice.py --config-list
  python3 scripts/gjuice.py --config-add type --label "Bug Fix" \\
      --bg-light "#fee2e2" --fg-light "#991b1b" --bg-dark "#4a1010" --fg-dark "#fca5a5"
  python3 scripts/gjuice.py --config-add status --label "blocked" --terminal \\
      --bg-light "#f1f5f9" --fg-light "#475569" --bg-dark "#1e2433" --fg-dark "#94a3b8"
  python3 scripts/gjuice.py --config-update type 5 --label "Security Fix"
  python3 scripts/gjuice.py --config-remove area 3   # error if any issue uses area id 3

Filters can be combined (AND logic). Multiple values with comma: --area business,rest
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

ISSUES_JS  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "issues.js")
CONFIG_JS  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gjuice.config.js")

VALID_STATUSES    = {"pending", "done"}  # fallback when no config

def _load_config():
    if not os.path.exists(CONFIG_JS):
        return {}
    with open(CONFIG_JS, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"window\.GJUICE_CONFIG\s*=\s*(\{.*\})\s*;?\s*$", src, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return {}

_CONFIG = _load_config()
_TYPES      = _CONFIG.get("types", [])
_AREAS      = _CONFIG.get("areas", [])
_PRIORITIES = _CONFIG.get("priorities", [])
_STATUSES   = _CONFIG.get("statuses", [])
# Type maps
_TYPE_BY_ID    = {t["id"]: t for t in _TYPES}
_TYPE_BY_LABEL = {t["label"].lower(): t["id"] for t in _TYPES}
# Area maps (empty = open-string mode)
_AREA_BY_ID    = {a["id"]: a for a in _AREAS}
_AREA_BY_LABEL = {a["label"].lower(): a["id"] for a in _AREAS}
# Priority maps
_PRIORITY_BY_ID    = {p["id"]: p for p in _PRIORITIES}
_PRIORITY_BY_LABEL = {p["label"].lower(): p["id"] for p in _PRIORITIES}
_PRIORITY_ORDER    = {p["id"]: i for i, p in enumerate(_PRIORITIES)}
# Status maps
_STATUS_BY_ID    = {s["id"]: s for s in _STATUSES}
_STATUS_BY_LABEL = {s["label"].lower(): s["id"] for s in _STATUSES}
# First terminal and first non-terminal status ids (used by --done / --reopen)
_TERMINAL_ID    = next((s["id"] for s in _STATUSES if s.get("terminal")),     2)
_NONTERMINAL_ID = next((s["id"] for s in _STATUSES if not s.get("terminal")), 1)

def resolve_type_id(value):
    """Accept numeric id (int or str) or label string. Returns int id or exits."""
    if not _TYPES:
        return value
    try:
        num = int(value)
        if num in _TYPE_BY_ID:
            return num
        sys.exit(f"Unknown type id {num}. Valid ids: {', '.join(str(t['id']) + '=' + t['label'] for t in _TYPES)}")
    except ValueError:
        match = _TYPE_BY_LABEL.get(value.lower())
        if match is not None:
            return match
        sys.exit(f"Unknown type '{value}'. Valid: {', '.join(t['label'] for t in _TYPES)}")

def type_label(type_id):
    t = _TYPE_BY_ID.get(type_id)
    return t["label"] if t else str(type_id) if type_id is not None else ''

def resolve_area_id(value):
    """Accept numeric id (int or str) or label string. In open-string mode, returns as-is."""
    if not _AREAS:
        return value  # open-string mode
    try:
        num = int(value)
        if num in _AREA_BY_ID:
            return num
        sys.exit(f"Unknown area id {num}. Valid ids: {', '.join(str(a['id']) + '=' + a['label'] for a in _AREAS)}")
    except (ValueError, TypeError):
        match = _AREA_BY_LABEL.get(str(value).lower())
        if match is not None:
            return match
        sys.exit(f"Unknown area '{value}'. Valid: {', '.join(a['label'] for a in _AREAS)}")

def area_label(area_id):
    if not _AREAS:
        return str(area_id) if area_id is not None else ''
    a = _AREA_BY_ID.get(area_id)
    return a["label"] if a else str(area_id) if area_id is not None else ''

def resolve_priority_id(value):
    """Accept numeric id (int or str) or label string. Returns int id or exits."""
    if not _PRIORITIES:
        return value  # open mode
    try:
        num = int(value)
        if num in _PRIORITY_BY_ID:
            return num
        sys.exit(f"Unknown priority id {num}. Valid ids: {', '.join(str(p['id']) + '=' + p['label'] for p in _PRIORITIES)}")
    except (ValueError, TypeError):
        match = _PRIORITY_BY_LABEL.get(str(value).lower())
        if match is not None:
            return match
        sys.exit(f"Unknown priority '{value}'. Valid: {', '.join(p['label'] for p in _PRIORITIES)}")

def priority_label(prio_id):
    p = _PRIORITY_BY_ID.get(prio_id)
    return p["label"] if p else str(prio_id) if prio_id is not None else ''

def resolve_status_id(value):
    """Accept numeric id (int or str) or label string. Returns int id or exits."""
    if not _STATUSES:
        if str(value) in VALID_STATUSES:
            return value
        sys.exit(f"Invalid status '{value}'. Valid: {', '.join(sorted(VALID_STATUSES))}")
    try:
        num = int(value)
        if num in _STATUS_BY_ID:
            return num
        sys.exit(f"Unknown status id {num}. Valid ids: {', '.join(str(s['id']) + '=' + s['label'] for s in _STATUSES)}")
    except (ValueError, TypeError):
        match = _STATUS_BY_LABEL.get(str(value).lower())
        if match is not None:
            return match
        sys.exit(f"Unknown status '{value}'. Valid: {', '.join(s['label'] for s in _STATUSES)}")

def status_label(status_id):
    s = _STATUS_BY_ID.get(status_id)
    return s["label"] if s else str(status_id) if status_id is not None else ''

def is_terminal(status_id):
    s = _STATUS_BY_ID.get(status_id)
    return s["terminal"] if s else (status_id == _TERMINAL_ID)

# ANSI colours
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[31m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
GREY   = "\033[90m"


def apply_description(issue, description_arg, augment_arg):
    """Mutate issue description based on --description/--augment flags."""
    if description_arg == "" and augment_arg:
        existing = issue.get("description", "").rstrip()
        issue["description"] = existing + ("\n\n" if existing else "") + augment_arg
    elif description_arg is not None and description_arg != "":
        issue["description"] = description_arg


def apply_solution(issue, solution_arg, augment_arg):
    if solution_arg == "" and augment_arg:
        existing = issue.get("solution", "").rstrip()
        issue["solution"] = existing + ("\n\n" if existing else "") + augment_arg
    elif solution_arg is not None and solution_arg != "":
        issue["solution"] = solution_arg


def validate_augment_usage(description_arg, solution_arg, augment_arg):
    if not augment_arg:
        return

    targets = []
    if description_arg == "":
        targets.append("--description")
    if solution_arg == "":
        targets.append("--solution")

    if len(targets) != 1:
        sys.exit(
            "--augment must qualify exactly one of --description or --solution: "
            "use --description --augment \"text\" or --solution --augment \"text\""
        )


def validate_field(field, value, valid_set):
    if value and value not in valid_set:
        sys.exit(f"Invalid {field} '{value}'. Valid: {', '.join(sorted(valid_set))}")


def parse_timestamp(value, flag):
    """Parse an ISO 8601 timestamp string. Accepts with or without timezone offset."""
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat(timespec="seconds")
        except ValueError:
            continue
    sys.exit(f"{flag} value '{value}' is not a recognised ISO 8601 timestamp (e.g. 2026-06-01T14:30:00+02:00)")


def load_issues():
    if not os.path.exists(ISSUES_JS):
        return []
    with open(ISSUES_JS, encoding="utf-8") as f:
        src = f.read()
    # Strip JS wrapper: window.TASKS = [...];
    m = re.search(r"window\.TASKS\s*=\s*(\[.*\])\s*;?\s*$", src, re.DOTALL)
    if not m:
        sys.exit("ERROR: could not parse issues.js — unexpected format")
    return json.loads(m.group(1))


def save_issues(issues):
    body = json.dumps(issues, indent=2, ensure_ascii=False)
    with open(ISSUES_JS, "w", encoding="utf-8") as f:
        f.write("window.TASKS = ")
        f.write(body)
        f.write(";\n")


def save_config(cfg):
    body = json.dumps(cfg, indent=2, ensure_ascii=False)
    with open(CONFIG_JS, "w", encoding="utf-8") as f:
        f.write("window.GJUICE_CONFIG = ")
        f.write(body)
        f.write(";\n")


# Config category → (config key, issue field)
_CATEGORIES = {
    "type":     ("types",      "type"),
    "area":     ("areas",      "area"),
    "priority": ("priorities", "priority"),
    "status":   ("statuses",   "status"),
}


def _config_entries(cfg, category):
    key = _CATEGORIES[category][0]
    return cfg.setdefault(key, [])


_CATEGORY_PLURAL = {"type": "TYPES", "area": "AREAS", "priority": "PRIORITIES", "status": "STATUSES"}

def print_config_list(cfg):
    for cat, (key, _) in _CATEGORIES.items():
        entries = cfg.get(key, [])
        print(BOLD + _CATEGORY_PLURAL[cat] + RESET)
        if not entries:
            print(DIM + "  (none)" + RESET)
        else:
            for e in entries:
                extra = ""
                if cat == "status":
                    extra = f"  terminal:{GREEN+'yes'+RESET if e.get('terminal') else DIM+'no'+RESET}"
                colors = ""
                if e.get("bgLight"):
                    colors = DIM + f"  {e['bgLight']}/{e.get('fgLight','')}  {e.get('bgDark','')}/{e.get('fgDark','')}" + RESET
                print(f"  {str(e['id']).rjust(3)}  {e['label']:<28}{extra}{colors}")
        print()


_PRIO_TERM_COLORS = [RED, YELLOW, DIM]

def priority_colour(prio_id):
    label = priority_label(prio_id)
    idx   = _PRIORITY_ORDER.get(prio_id, len(_PRIO_TERM_COLORS))
    color = _PRIO_TERM_COLORS[idx] if idx < len(_PRIO_TERM_COLORS) else ''
    return (color + label + RESET) if color else label


def status_colour(status_id):
    label = status_label(status_id)
    return (GREEN + label + RESET) if is_terminal(status_id) else (CYAN + label + RESET)


def fmt_date(iso):
    if not iso:
        return ""
    # 2026-06-07T10:00:00+02:00 → 07.06.2026 10:00
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", iso)
    if not m:
        return iso
    year, month, day, hour, minute = m.groups()
    return f"{day}.{month}.{year} {hour}:{minute}"


def print_summary(issues):
    if not issues:
        print(DIM + "No matching issues." + RESET)
        return

    col_id    = max(len(str(t["id"])) for t in issues)
    col_prio  = max(len(priority_label(t.get("priority"))) for t in issues)
    col_area  = max(len(area_label(t.get("area"))) for t in issues)
    col_type  = max(len(type_label(t.get("type"))) for t in issues)

    header = (
        f"{'ID':>{col_id}}  "
        f"{'PRIO':<{col_prio}}  "
        f"{'AREA':<{col_area}}  "
        f"{'TYPE':<{col_type}}  "
        f"TITLE"
    )
    print(BOLD + header + RESET)
    print(DIM + "-" * (len(header) + 20) + RESET)

    prev_terminal = None
    for t in issues:
        status = t.get("status")
        terminal = is_terminal(status)
        if prev_terminal is False and terminal:
            label = status_label(_TERMINAL_ID)
            print(DIM + "─" * 60 + f"  {label}  " + "─" * 12 + RESET)
        prev_terminal = terminal

        id_str    = str(t["id"]).rjust(col_id)
        prio      = priority_label(t.get("priority")).ljust(col_prio)
        area      = area_label(t.get("area")).ljust(col_area)
        ttype     = type_label(t.get("type")).ljust(col_type)
        title     = t.get("title", "")

        if terminal:
            line = f"{id_str}  {prio}  {area}  {ttype}  {title}"
            print(GREY + line + RESET)
        else:
            print(
                f"{id_str}  "
                f"{priority_colour(t.get('priority')):<{col_prio + 10}}  "
                f"{area}  "
                f"{ttype}  "
                f"{title}"
            )

    active_count   = sum(1 for t in issues if not is_terminal(t.get("status")))
    terminal_count = sum(1 for t in issues if is_terminal(t.get("status")))
    print()
    print(DIM + f"{active_count} active, {terminal_count} done" + RESET)


def print_detail(issue):
    print()
    print(BOLD + f"#{issue['id']}  {issue['title']}" + RESET)
    print(f"  type:     {type_label(issue.get('type'))}")
    print(f"  area:     {area_label(issue.get('area'))}")
    print(f"  status:   {status_colour(issue.get('status'))}")
    print(f"  priority: {priority_colour(issue.get('priority'))}")
    print(f"  created:  {fmt_date(issue.get('createdAt', ''))}")
    if issue.get("completedAt"):
        print(f"  done:     {fmt_date(issue['completedAt'])}")
    desc = issue.get("description", "").strip()
    solution = issue.get("solution", "").strip()
    if desc:
        print()
        print(BOLD + "  Description:" + RESET)
        for line in desc.splitlines():
            print("  " + line)
    if solution:
        print()
        print(BOLD + "  Solution:" + RESET)
        for line in solution.splitlines():
            print("  " + line)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Query issues.js",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--all",      action="store_true",    help="include done issues")
    parser.add_argument("--id",       type=int,               help="show single issue by numeric id")
    parser.add_argument("--status",   help="filter by status (pending|done)")
    parser.add_argument("--priority", help="filter by priority, comma-separated (high,medium,low)")
    parser.add_argument("--area",     help="filter by area, comma-separated")
    parser.add_argument("--type",     help="filter by type, comma-separated")
    parser.add_argument("--search",   help="full-text search in title, description and solution")
    parser.add_argument("--regex",    action="store_true", help="treat --search value as a regular expression")
    parser.add_argument("--sort",     default="default", help="sort order: default, id-asc, id-desc, priority")
    parser.add_argument("--limit",    type=int,               help="max number of results to show")
    parser.add_argument("--last",     action="store_true",    help="show last issue by id (shortcut for --all --sort id-desc --limit 1)")
    # --- mutation commands ---
    parser.add_argument("--add",         action="store_true",    help="add a new issue (requires --title, --type, --area, --priority)")
    parser.add_argument("--update",      type=int, metavar="ID", help="update fields of an existing issue")
    parser.add_argument("--title",       help="issue title (--add / --update)")
    parser.add_argument("--description", nargs="?", const="", help="issue description: value replaces, omit value + --augment appends (--add / --update)")
    parser.add_argument("--augment",     help="text to append when used with --description or --solution (qualifier for --add / --update / --done)")
    parser.add_argument("--done",        type=int, metavar="ID", help="mark issue as done")
    parser.add_argument("--solution",    nargs="?", const="", help="issue solution: value replaces, omit value + --augment appends (--done / --add / --update)")
    parser.add_argument("--reopen",      type=int, metavar="ID", help="reopen a done issue")
    parser.add_argument("--created-at",  dest="created_at",   help="override createdAt timestamp (ISO 8601, e.g. 2026-06-01T14:30:00+02:00) — for --add")
    parser.add_argument("--completed-at", dest="completed_at", help="override completedAt timestamp (ISO 8601) — for --add, --done, --update")
    # --- config commands ---
    parser.add_argument("--config-list",   action="store_true", help="list all config entries")
    parser.add_argument("--config-add",    metavar="CATEGORY",  help="add entry to config: type|area|priority|status")
    parser.add_argument("--config-update", nargs=2, metavar=("CATEGORY", "ID"), help="update config entry by id")
    parser.add_argument("--config-remove", nargs=2, metavar=("CATEGORY", "ID"), help="remove config entry (error if used in issues)")
    parser.add_argument("--label",    help="label for config entry")
    parser.add_argument("--bg-light", dest="bg_light", help="background hex color (light mode)")
    parser.add_argument("--fg-light", dest="fg_light", help="foreground hex color (light mode)")
    parser.add_argument("--bg-dark",  dest="bg_dark",  help="background hex color (dark mode)")
    parser.add_argument("--fg-dark",  dest="fg_dark",  help="foreground hex color (dark mode)")
    parser.add_argument("--terminal",    dest="terminal", action="store_true",  default=None, help="mark status as terminal (closes issue, sets completedAt)")
    parser.add_argument("--no-terminal", dest="terminal", action="store_false",              help="mark status as non-terminal (active)")
    args = parser.parse_args()

    # --- config commands (don't need issues loaded) ---
    if args.config_list:
        cfg = _load_config()
        print_config_list(cfg)
        return

    if args.config_add:
        cat = args.config_add.lower()
        if cat not in _CATEGORIES:
            sys.exit(f"Unknown category '{cat}'. Valid: {', '.join(_CATEGORIES)}")
        if not args.label:
            sys.exit("--config-add requires --label")
        cfg     = _load_config()
        entries = _config_entries(cfg, cat)
        new_id  = max((e["id"] for e in entries), default=0) + 1
        entry   = {"id": new_id, "label": args.label}
        if args.bg_light: entry["bgLight"] = args.bg_light
        if args.fg_light: entry["fgLight"] = args.fg_light
        if args.bg_dark:  entry["bgDark"]  = args.bg_dark
        if args.fg_dark:  entry["fgDark"]  = args.fg_dark
        if cat == "status":
            entry["terminal"] = bool(args.terminal)
        entries.append(entry)
        save_config(cfg)
        print(GREEN + f"✓ {cat.capitalize()} '{args.label}' added with id {new_id}." + RESET)
        return

    if args.config_update:
        cat, raw_id = args.config_update
        cat = cat.lower()
        if cat not in _CATEGORIES:
            sys.exit(f"Unknown category '{cat}'. Valid: {', '.join(_CATEGORIES)}")
        try:
            target_id = int(raw_id)
        except ValueError:
            sys.exit(f"ID must be numeric, got '{raw_id}'")
        cfg     = _load_config()
        entries = _config_entries(cfg, cat)
        matches = [e for e in entries if e["id"] == target_id]
        if not matches:
            sys.exit(f"No {cat} with id {target_id}.")
        entry = matches[0]
        changed = []
        if args.label:    entry["label"]   = args.label;    changed.append("label")
        if args.bg_light: entry["bgLight"] = args.bg_light; changed.append("bgLight")
        if args.fg_light: entry["fgLight"] = args.fg_light; changed.append("fgLight")
        if args.bg_dark:  entry["bgDark"]  = args.bg_dark;  changed.append("bgDark")
        if args.fg_dark:  entry["fgDark"]  = args.fg_dark;  changed.append("fgDark")
        if cat == "status" and args.terminal is not None:
            entry["terminal"] = bool(args.terminal); changed.append("terminal")
        if not changed:
            sys.exit("--config-update requires at least one field: --label, --bg-light, --fg-light, --bg-dark, --fg-dark" +
                     (" or --terminal / --no-terminal" if cat == "status" else ""))
        save_config(cfg)
        print(CYAN + f"✎ {cat.capitalize()} {target_id} updated: {', '.join(changed)}." + RESET)
        return

    if args.config_remove:
        cat, raw_id = args.config_remove
        cat = cat.lower()
        if cat not in _CATEGORIES:
            sys.exit(f"Unknown category '{cat}'. Valid: {', '.join(_CATEGORIES)}")
        try:
            target_id = int(raw_id)
        except ValueError:
            sys.exit(f"ID must be numeric, got '{raw_id}'")
        cfg     = _load_config()
        entries = _config_entries(cfg, cat)
        matches = [e for e in entries if e["id"] == target_id]
        if not matches:
            sys.exit(f"No {cat} with id {target_id}.")
        label = matches[0]["label"]
        # Safety check: scan issues for usage
        issue_field = _CATEGORIES[cat][1]
        issues = load_issues()
        in_use = [t["id"] for t in issues if t.get(issue_field) == target_id]
        if in_use:
            ids = ", ".join(f"#{i}" for i in in_use[:10])
            more = f" (+{len(in_use)-10} more)" if len(in_use) > 10 else ""
            sys.exit(f"Cannot remove {cat} '{label}' (id {target_id}): used by issue(s) {ids}{more}.")
        cfg[_CATEGORIES[cat][0]] = [e for e in entries if e["id"] != target_id]
        save_config(cfg)
        print(GREEN + f"✓ {cat.capitalize()} '{label}' (id {target_id}) removed." + RESET)
        return

    issues = load_issues()

    # --done: mark issue as done, with optional description/solution updates
    if args.done is not None:
        matches = [t for t in issues if t["id"] == args.done]
        if not matches:
            sys.exit(f"Issue {args.done} not found.")
        issue = matches[0]
        issue["status"] = _TERMINAL_ID
        issue["completedAt"] = parse_timestamp(args.completed_at, "--completed-at") if args.completed_at else datetime.now().astimezone().isoformat(timespec="seconds")
        validate_augment_usage(args.description, args.solution, args.augment)
        apply_description(issue, args.description, args.augment)
        apply_solution(issue, args.solution, args.augment)
        save_issues(issues)
        print(GREEN + f"✓ Issue {args.done} marked as {status_label(_TERMINAL_ID)}." + RESET)
        print_detail(issue)
        return

    # --reopen: reopen a done issue
    if args.reopen is not None:
        matches = [t for t in issues if t["id"] == args.reopen]
        if not matches:
            sys.exit(f"Issue {args.reopen} not found.")
        issue = matches[0]
        issue["status"] = _NONTERMINAL_ID
        issue.pop("completedAt", None)
        save_issues(issues)
        print(CYAN + f"↩ Issue {args.reopen} reopened." + RESET)
        print_detail(issue)
        return

    # --add: create a new issue
    if args.add:
        missing = [f for f in ("title", "type", "area", "priority") if not getattr(args, f, None)]
        if missing:
            sys.exit(f"--add requires: {', '.join('--' + f for f in missing)}")
        type_id  = resolve_type_id(args.type)
        area_id  = resolve_area_id(args.area)
        prio_id  = resolve_priority_id(args.priority)
        new_id = max((t["id"] for t in issues), default=0) + 1
        now = parse_timestamp(args.created_at, "--created-at") if args.created_at else datetime.now().astimezone().isoformat(timespec="seconds")
        issue = {
            "id":          new_id,
            "title":       args.title,
            "type":        type_id,
            "area":        area_id,
            "status":      _NONTERMINAL_ID,
            "priority":    prio_id,
            "createdAt":   now,
            "description": getattr(args, "description", "") or "",
        }
        validate_augment_usage(args.description, args.solution, args.augment)
        apply_description(issue, args.description, args.augment)
        apply_solution(issue, args.solution, args.augment)
        if args.completed_at:
            issue["completedAt"] = parse_timestamp(args.completed_at, "--completed-at")
        issues.append(issue)
        save_issues(issues)
        print(GREEN + f"✓ Issue {new_id} created." + RESET)
        print_detail(issue)
        return

    # --update: edit fields of an existing issue
    if args.update is not None:
        matches = [t for t in issues if t["id"] == args.update]
        if not matches:
            sys.exit(f"Issue {args.update} not found.")
        issue = matches[0]
        validate_augment_usage(args.description, args.solution, args.augment)
        apply_description(issue, args.description, args.augment)
        apply_solution(issue, args.solution, args.augment)
        updatable = {
            "title":    args.title,
            "type":     resolve_type_id(args.type) if args.type else None,
            "area":     resolve_area_id(args.area) if args.area else None,
            "priority": resolve_priority_id(args.priority) if args.priority else None,
        }
        changed = {k: v for k, v in updatable.items() if v is not None}
        if args.status:
            status_id = resolve_status_id(args.status)
            changed["status"] = status_id
        content_touched = args.description is not None or args.solution is not None
        timestamp_touched = args.created_at or args.completed_at
        if not changed and not content_touched and not timestamp_touched:
            sys.exit("--update requires at least one field: --title, --type, --area, --priority, --status, --description [--augment \"text\"], --solution [--augment \"text\"], --created-at, --completed-at")
        issue.update(changed)
        if args.description is not None:
            changed["description"] = "(updated)"
        if args.solution is not None:
            changed["solution"] = "(updated)"
        if args.created_at:
            issue["createdAt"] = parse_timestamp(args.created_at, "--created-at")
            changed["createdAt"] = "(updated)"
        if "status" in changed and is_terminal(changed["status"]) and not issue.get("completedAt"):
            issue["completedAt"] = parse_timestamp(args.completed_at, "--completed-at") if args.completed_at else datetime.now().astimezone().isoformat(timespec="seconds")
        elif "status" in changed and not is_terminal(changed["status"]):
            issue.pop("completedAt", None)
        elif args.completed_at:
            issue["completedAt"] = parse_timestamp(args.completed_at, "--completed-at")
        save_issues(issues)
        print(CYAN + f"✎ Issue {args.update} updated: {', '.join(changed.keys())}." + RESET)
        print_detail(issue)
        return

    # --last: shortcut for last issue by id
    if args.last:
        top = sorted(issues, key=lambda t: t["id"], reverse=True)[:1]
        if not top:
            sys.exit("No issues found.")
        print_detail(top[0])
        return

    # Single issue detail
    if args.id is not None:
        matches = [t for t in issues if t["id"] == args.id]
        if not matches:
            sys.exit(f"Issue {args.id} not found.")
        print_detail(matches[0])
        return

    # Filters
    if not args.all and not args.status:
        issues = [t for t in issues if not is_terminal(t.get("status"))]

    if args.status:
        status_ids = {resolve_status_id(v.strip()) for v in args.status.split(",")}
        issues = [t for t in issues if t.get("status") in status_ids]

    if args.priority:
        prio_ids = {resolve_priority_id(v.strip()) for v in args.priority.split(",")}
        issues = [t for t in issues if t.get("priority") in prio_ids]

    if args.area:
        area_ids = {resolve_area_id(v.strip()) for v in args.area.split(",")}
        issues = [t for t in issues if t.get("area") in area_ids]

    if args.type:
        type_ids = {resolve_type_id(v.strip()) for v in args.type.split(",")}
        issues = [t for t in issues if t.get("type") in type_ids]

    if args.search:
        if args.regex:
            try:
                pattern = re.compile(args.search, re.IGNORECASE)
            except re.error as e:
                sys.exit(f"Invalid regex: {e}")
            issues = [
                t for t in issues
                if pattern.search(t.get("title", ""))
                or pattern.search(t.get("description", ""))
                or pattern.search(t.get("solution", ""))
            ]
        else:
            needle = args.search.lower()
            issues = [
                t for t in issues
                if needle in t.get("title", "").lower()
                or needle in t.get("description", "").lower()
                or needle in t.get("solution", "").lower()
            ]

    # Sort
    if args.sort == "id-desc":
        issues.sort(key=lambda t: t["id"], reverse=True)
    elif args.sort == "id-asc":
        issues.sort(key=lambda t: t["id"])
    else:
        # default: active first (by priority), then terminal
        def sort_key(t):
            terminal = 1 if is_terminal(t.get("status")) else 0
            prio     = _PRIORITY_ORDER.get(t.get("priority"), len(_PRIORITIES))
            return (terminal, prio, t["id"])
        issues.sort(key=sort_key)

    if args.limit:
        issues = issues[:args.limit]

    print_summary(issues)


if __name__ == "__main__":
    main()
