---
name: conventional
description: Use when writing commit messages following the Conventional Commits v1.0 specification. Provides the full format, type vocabulary, breaking change rules, and examples.
metadata:
  version: "0.1.0"
---

# Conventional Commits — Message Style

Specification: [conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0/)

## Format

```
<type>[(<scope>)][!]: <description>

[optional body]

[optional footer(s)]
```

- `type` — required, see table below
- `scope` — optional, noun in parentheses describing the section of codebase
- `!` — optional, appended to signal a breaking change
- `description` — short imperative summary, no capital first letter, no full stop
- `body` — optional, one blank line after description; explains *why*, not *what*
- `footer` — optional, one blank line after body; key: value pairs

## Types

| Type | SemVer | When |
|---|---|---|
| `feat` | MINOR | Introduces a new feature |
| `fix` | PATCH | Patches a bug |
| `docs` | — | Documentation only |
| `style` | — | Formatting, whitespace — no logic change |
| `refactor` | — | Code restructure, no feature or bug |
| `perf` | — | Performance improvement |
| `test` | — | Adding or correcting tests |
| `build` | — | Build system or external dependency changes |
| `ci` | — | CI configuration changes |
| `chore` | — | Other changes that don't modify src or test files |
| `revert` | — | Reverts a previous commit |

`feat` and `fix` are the only types defined by the spec. All others come from the Angular convention and are widely adopted.

## Breaking changes

Two ways to mark a breaking change:

**Inline** — append `!` after type/scope:
```
feat(api)!: remove endpoint /v1/users
```

**Footer** — add `BREAKING CHANGE:` token in footer:
```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other configs
```

Both trigger a MAJOR semver bump. Use both together for maximum clarity.

## Scope

Optional but recommended. A noun describing the part of the codebase:

```
fix(auth): handle null token on logout
feat(ui): add dark mode toggle
```

Scope values are project-specific — define them in `user.md` alongside this file.

## Examples

```
feat(lang): add Polish language support
```

```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss incoming responses other than from latest request.

Reviewed-by: Z
```

```
feat!: send email to customer when product is shipped
```

```
chore: update dependencies
```

```
docs: correct spelling in CHANGELOG
```

## Tooling compatibility

This format is understood by:
- `semantic-release` — auto-generates releases and changelogs
- `conventional-changelog` — generates CHANGELOG.md from history
- `commitlint` — lints commit messages in CI
- Most major git forges display `type(scope): description` cleanly

## user.md

Project-specific scope vocabulary, allowed types, or additional footer conventions belong in `user.md` alongside this file.
