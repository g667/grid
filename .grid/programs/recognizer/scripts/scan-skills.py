#!/usr/bin/env python3
"""
scan-skills.py — Discover all SKILL.md files under .grid/ directories,
parse their frontmatter, and output as a JSON array to stdout.

Usage:
  python3 scan-skills.py [root_dir]

Output:
  JSON array of skill objects to stdout. Pipe to grid-state.py:
  python3 scan-skills.py | python3 .grid/programs/able/scripts/grid-state.py skills --register-batch
"""
import argparse
import json
import os
import re
import sys

# Directories that will never contain .grid or SKILL.md files.
PRUNE = frozenset({
    '.git', 'node_modules', 'target', 'build', 'dist',
    '__pycache__', '.venv', 'venv', '.tox', '.mypy_cache',
})


def find_grid_dirs(root):
    """Phase 1: yield every .grid directory under root, without recursing into them."""
    for dirpath, dirnames, _ in os.walk(root, topdown=True):
        if '.grid' in dirnames:
            yield os.path.join(dirpath, '.grid')
            dirnames.remove('.grid')          # don't look for .grid inside .grid
        # Prune heavy/irrelevant dirs to keep phase 1 fast
        dirnames[:] = [
            d for d in dirnames
            if d not in PRUNE and not d.startswith('.')
        ]


def find_skill_files(grid_dir):
    """Phase 2: yield every SKILL.md path inside a .grid directory."""
    for dirpath, _, filenames in os.walk(grid_dir):
        if 'SKILL.md' in filenames:
            yield os.path.join(dirpath, 'SKILL.md')


def parse_frontmatter(path):
    """
    Read the frontmatter block and extract name, description, suggests, and links.
    Returns (name, description, suggests, links).
    - name:        str or None  — top-level `name:` field
    - description: str or None  — top-level `description:` field
    - suggests:    str or None  — `metadata.suggests` pipe-separated trigger phrases
    - links:       list of {skill, on} or None — `metadata.links` cross-link entries
    """
    name = description = suggests = None
    links = []

    try:
        with open(path, encoding='utf-8') as f:
            if f.readline().strip() != '---':
                return name, description, suggests, None
            fm_lines = []
            for line in f:
                stripped = line.rstrip('\n')
                if stripped.strip() == '---':
                    break
                fm_lines.append(stripped)
    except OSError:
        return name, description, suggests, None

    # Top-level scalar fields (no leading whitespace)
    for line in fm_lines:
        if not line.startswith(' '):
            if line.startswith('name:'):
                name = line[5:].strip().strip('"\'')
            elif line.startswith('description:'):
                description = line[12:].strip().strip('"\'')

    # metadata block — state machine over indented lines
    STATE_NONE, STATE_META, STATE_LINKS = 0, 1, 2
    state = STATE_NONE
    current_link = None

    for line in fm_lines:
        if state == STATE_NONE:
            if line == 'metadata:':
                state = STATE_META

        elif state == STATE_META:
            if not line.startswith(' '):
                state = STATE_NONE
            elif re.match(r'\s+suggests:', line):
                suggests = line.split('suggests:', 1)[1].strip().strip('"\'')
            elif re.match(r'  links:\s*$', line):
                state = STATE_LINKS

        elif state == STATE_LINKS:
            if not line.startswith(' '):
                if current_link:
                    links.append(current_link)
                    current_link = None
                state = STATE_NONE
            elif re.match(r'  \S', line):          # back to metadata indent level
                if current_link:
                    links.append(current_link)
                    current_link = None
                state = STATE_META
                if re.match(r'\s+suggests:', line):  # re-process if it's suggests
                    suggests = line.split('suggests:', 1)[1].strip().strip('"\'')
            elif re.match(r'    - skill:', line):
                if current_link:
                    links.append(current_link)
                skill_val = line.split('skill:', 1)[1].strip().strip('"\'')
                current_link = {'skill': skill_val, 'on': None}
            elif re.match(r'      on:', line) and current_link:
                current_link['on'] = line.split('on:', 1)[1].strip().strip('"\'')

    if current_link:
        links.append(current_link)

    return name, description, suggests, links if links else None


def skill_path(skill_file, root):
    """Return directory path relative to root, without the /SKILL.md suffix."""
    rel = os.path.relpath(os.path.dirname(skill_file), root)
    return rel.replace('\\', '/')          # normalise on Windows too


def main():
    parser = argparse.ArgumentParser(
        description='Scan .grid/ directories for SKILL.md files and output as JSON.')
    parser.add_argument('root', nargs='?', default='.',
                        help='Project root to scan (default: cwd)')
    args = parser.parse_args()

    root = os.path.abspath(args.root)

    skills = []
    for grid_dir in find_grid_dirs(root):
        for skill_file in find_skill_files(grid_dir):
            name, desc, suggests, links = parse_frontmatter(skill_file)
            if not desc:
                continue
            path = skill_path(skill_file, root)
            skills.append((path, name, desc, suggests, links))

    # Detect name collisions — same name on two distinct skills is a conflict
    name_map = {}
    for path, name, _desc, _suggests, _links in skills:
        if name:
            name_map.setdefault(name, []).append(path)
    for name, paths in sorted(name_map.items()):
        if len(paths) > 1:
            print(f"⚠️  Name collision: '{name}' used by {len(paths)} skills:", file=sys.stderr)
            for p in paths:
                print(f"     {p}", file=sys.stderr)

    entries = [
        {"path": p, "name": n, "description": d, "suggests": s, "links": l}
        for p, n, d, s, l in skills
    ]
    print(json.dumps(entries, indent=2))
    print(f"{len(skills)} skills found", file=sys.stderr)


if __name__ == '__main__':
    main()
