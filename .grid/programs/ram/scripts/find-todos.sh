#!/bin/bash
# find-todos.sh — scan skill files for open TODO: markers
# Usage: ./find-todos.sh [file-extension]
# Default: scans all .md files under .grid/ and any module-level .grid/ dirs
# Example: ./find-todos.sh        → scans all .md skill files
#          ./find-todos.sh md     → same
#          ./find-todos.sh .md    → same, dot is optional

fileEnding="${1:-md}"
# normalize — strip leading dot if provided, then re-add
fileEnding="*.${fileEnding#.}"

found=0
while IFS= read -r -d '' dir; do
  results=$(grep -rn "TODO:" "$dir" --include="$fileEnding" 2>/dev/null \
    | grep -v '`TODO:`' \
    | sed 's|^\./||' \
    | sed 's/\(:[0-9]*:\).*TODO:[[:space:]]*/\1/')
  if [ -n "$results" ]; then
    echo "$results"
    found=1
  fi
done < <(find . -type d -name ".grid" -not -path "*/.git/*" -print0 2>/dev/null)

if [ "$found" -eq 0 ]; then
  echo "No open TODO: markers found."
fi
