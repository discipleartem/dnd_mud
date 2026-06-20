# Agent rules — dnd_mud

All agent rules live in [`.cursor/rules/`](.cursor/rules/).  
Global rules: `~/.cursor/rules/` (see [`00-global.mdc`](~/.cursor/rules/00-global.mdc)).

## Rule priority

1. Project `alwaysApply`: `00-project`, `dnd-mud-git`, `dnd-mud-verify`
2. Project globs: `dnd-mud-*` (simple Python overrides global architecture for this MUD)
3. Global rules: `~/.cursor/rules/`
4. User Rules: commit/PR **protocol** only — workflow in `01-operations.mdc`

Console MUD: `dnd-mud-verify.mdc` forbids browser tools (overrides global `browser-automation.mdc`).

## Rule map

### Global (`~/.cursor/rules/`)

| File | Scope | Content |
|------|-------|---------|
| `00-global.mdc` | always | META, KISS/DRY/YAGNI, language, Python mode, index |
| `01-operations.mdc` | always | `.venv`, git workflow (dev/main, автокоммит, push/PR по запросу), secrets |
| `python-standards.mdc` | `**/*.py` | Python 3.12+, types, PEP 8, tooling |
| `python-architecture.mdc` | `**/*.py` | SOLID, design patterns |
| `browser-automation.mdc` | web globs | Browser DevTools MCP (not used in dnd_mud) |

Reference: `~/.cursor/docs/python-versions.md`

### Project (`.cursor/rules/`)

| File | Scope | Content |
|------|-------|---------|
| `00-project.mdc` | always | Stack, commands, local index |
| `dnd-mud-python-simple.mdc` | `core/**`, `ui/**`, `main.py`, `tests/**` | Simple Python without premature abstractions |
| `dnd-mud-core.mdc` | `core/**`, `ui/**`, `main.py` | Layers, localization, mechanics |
| `dnd-mud-data.mdc` | `database/**`, `mods/**`, `saves/**`, `**/*.json` | YAML/JSON paths and formats (single source) |
| `dnd-mud-tests.mdc` | `tests/**` | pytest — простые, необходимые тесты |
| `dnd-mud-git.mdc` | always | scope и dnd_mud-артефакты (extends global git) |
| `dnd-mud-verify.mdc` | always | `make test`, console smoke (no browser) |

## Principle

- **2** global `alwaysApply` + **3** project `alwaysApply`
- Remaining rules activate by `globs` when matching files are open
- Simple first → patterns only when they simplify (`dnd-mud-python-simple.mdc`)
- Data paths and formats: **`dnd-mud-data.mdc` only**
- Commands: **`00-project.mdc`**

## Project docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/API.md](docs/API.md)
- [docs/CHANGELOG.md](docs/CHANGELOG.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/MUD_PRD.md](docs/MUD_PRD.md)
