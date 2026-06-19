# Agent rules — dnd_mud

All agent rules live in [`.cursor/rules/`](.cursor/rules/).  
Global rules: `~/.cursor/rules/` (apply to all projects).

## Rule map

### Global (`~/.cursor/rules/`)

| File | Scope | Content |
|------|-------|---------|
| `00-global.mdc` | always | META, KISS/DRY/YAGNI, language, Python mode, index |
| `01-operations.mdc` | always | `.venv`, git safety, secrets |
| `python-standards.mdc` | `**/*.py` | Python 3.12+, types, PEP 8, tooling |
| `python-architecture.mdc` | `**/*.py` | SOLID, design patterns |
| `browser-automation.mdc` | web globs | Browser DevTools MCP (not used in dnd_mud) |

Reference: `~/.cursor/docs/python-versions.md`

### Project (`.cursor/rules/`)

| File | Scope | Content |
|------|-------|---------|
| `00-project.mdc` | always | Stack, commands, index |
| `dnd-mud-core.mdc` | `core/**`, `ui/**`, `main.py` | Layers, localization, mechanics |
| `dnd-mud-data.mdc` | `database/**`, `mods/**`, `adventures_scripts/**` | YAML, mods |
| `dnd-mud-tests.mdc` | `tests/**` | pytest conventions |
| `dnd-mud-verify.mdc` | always | `make test`, console smoke (no browser) |

## Principle

- **2** global `alwaysApply` + **2** project `alwaysApply` (`00-project`, `dnd-mud-verify`)
- Remaining rules activate by `globs` when matching files are open
- Simple first → patterns only when they simplify

## Project docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/MUD_PRD.md](docs/MUD_PRD.md)

## Quick commands

```bash
make install
make test
make check
python main.py
```
