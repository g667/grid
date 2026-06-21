---
name: git-grid-style
description: Use when writing commit messages in the Grid house style. Compact type codes, bare task id, expressive vocabulary designed for product and platform projects.
metadata:
  version: "0.1.0"
---

# Grid — Commit Message Style

A compact, expressive commit convention designed for product and platform work. Not tooling-driven — optimised for readable git logs and clear intent at a glance.

## Grammar

```ebnf
commit-line  = id " " type ": " description ;
              (* id may be omitted when no traceable task exists *)

type         = "fet" | "fix" | "sec" | "ref" | "sty" | "doc"
             | "tst" | "ski" | "iss" | "alm" | "rev" ;

description  = sentence ;
              (* sentence case, no trailing full stop *)
```

## Types

| Type | When |
|---|---|
| `fet` | New feature or user-visible behaviour |
| `fix` | Bug fix |
| `sec` | Security fix or hardening — deserves its own type for audit trails |
| `ref` | Refactor — code change, no behaviour change |
| `sty` | Style or formatting — no logic change |
| `doc` | Documentation and comments only |
| `tst` | Tests only |
| `ski` | Skill file changes only |
| `iss` | Issue tracker changes — create, update, close, or migrate issues |
| `alm` | Application lifecycle management — version bumps, build tooling, dependency updates, release changes |
| `rev` | Revert a previous commit — clearly distinct from a fix or refactor |

## Examples

```
43 fet: Add CSRF protection to session cookie path
```

```
17 fix: Correct null handling in user mapper

Mapper returned empty string instead of null for missing display name.
```

```
55 ski: Update architecture iso with CDI Logger pattern
```

```
12 iss: Migrate mystiq-games issues to gjuice format
```

```
alm: Bump Payara to 6.2025.1
```

## user.md

Project-specific type additions or description conventions belong in `user.md` alongside this file.
