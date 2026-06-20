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
| `00-project.mdc` | always | Stack, commands, data paths, verify priority |
| `dnd-mud-python-simple.mdc` | `core/**`, `ui/**`, `main.py`, `tests/**` | Simple Python without premature abstractions |
| `dnd-mud-core.mdc` | `core/**`, `ui/**`, `main.py` | Layers, localization, mechanics |
| `dnd-mud-data.mdc` | `database/**`, `mods/**`, `saves/**`, `**/*.json` | YAML (справочники), JSON (сейвы/конфиги) |
| `dnd-mud-tests.mdc` | `tests/**` | pytest — простые, необходимые тесты |
| `dnd-mud-git.mdc` | always | Git workflow агента: task-ветка, атомарные коммиты |
| `dnd-mud-verify.mdc` | always | `make test`, console smoke (no browser) |

## Principle

- **2** global `alwaysApply` + **3** project `alwaysApply` (`00-project`, `dnd-mud-git`, `dnd-mud-verify`)
- Remaining rules activate by `globs` when matching files are open
- Simple first → patterns only when they simplify (`dnd-mud-python-simple.mdc`)
- `dnd-mud-verify.mdc` overrides global browser rules for this console app

## Project docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/API.md](docs/API.md)
- [docs/CHANGELOG.md](docs/CHANGELOG.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/MUD_PRD.md](docs/MUD_PRD.md)

## Data storage

- **Python 3.12** — основной язык проекта
- **YAML** — справочники и игровой контент в `database/` (расы, классы, строки, приключения)
- **JSON** — mutable state: `database/core/settings.json`, `saves/characters/*.json`

Структура `database/`:

```
database/
├── classes/classes.yaml
├── content/adventures.yaml
├── core/settings.json.example
├── _future/                    # Phase 2: core/, equipment/, progression/, content/
├── races/races.yaml
└── strings/{en,ru}.yaml
```

Доступ к файлам только через `core/`, не из `ui/`.

## Quick commands

```bash
make install
make test
make check
python main.py
```
