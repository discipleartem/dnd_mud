---
description: dnd_mud — stack, команды, docs index, local rules index
alwaysApply: true
---

# dnd_mud project

**Stack:** Python **3.12**, console MUD, Colorama, file-based storage, pytest.

**Принцип:** [`dnd-mud-python.md`](dnd-mud-python.md), [`dnd-mud-tests.md`](dnd-mud-tests.md).

## Commands

`.venv` обязателен.

```bash
make install          # venv + pip install -e ".[dev]"
make verify-changed   # подзадача (pre-commit)
# verify-scope — только в dnd-mud-review (конец task-ветки)
# make verify       — CI / release
make test / make check  # по запросу или CI
python main.py        # smoke меню (в review при UI-diff)
```

Verify/review policy — [`dnd-mud-workflow.md`](dnd-mud-workflow.md) §Verify / review; skills — [`.devin/workflows/`](../workflows/README.md).

## Docs

- [docs/README.md](../../docs/README.md) — индекс документации
- [docs/DND_RULES.md](../../docs/DND_RULES.md) · [docs/DATA_SCHEMA.md](../../docs/DATA_SCHEMA.md) · [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)
- [docs/API.md](../../docs/API.md) · [docs/BACKLOG.md](../../docs/BACKLOG.md) · [docs/CHANGELOG.md](../../docs/CHANGELOG.md) · [docs/DEVELOPMENT.md](../../docs/DEVELOPMENT.md) · [docs/MUD_PRD.md](../../docs/MUD_PRD.md)

## D&D 5e — источник истины и поиск правил

**Канон редакции:** Player's Handbook **2014** (рус. перевод PHantom, 2016). **Не** редакция правил 2024.

Код, YAML и [`docs/DND_RULES.md`](../../docs/DND_RULES.md) описывают **реализацию в MUD**. Пересказ механики для агентов — [`docs/rules/`](../../docs/rules/). При расхождении с официальным PHB 2014 / SRD 5.1 — уточнить по веб-источнику (шаг 2) и обновить `docs/rules/` (пересказ, не дословная копия).

### Алгоритм поиска (агенты и разработчики)

Искать информацию **строго по порядку**; переходить к следующему шагу только если на текущем ответа нет или он явно неполный. **Не опираться на память модели** и не выдумывать правила.

| Шаг | Источник | Как искать |
|-----|----------|------------|
| **1** | [`docs/rules/`](../../docs/rules/) | [`_index/lookup.yaml`](../../docs/rules/_index/lookup.yaml) (`by_alias` / `by_id`); детали — markdown `phb:auto`; обзор — [`docs/rules/README.md`](../../docs/rules/README.md), [`docs/DND_RULES.md`](../../docs/DND_RULES.md) |
| **2** | Интернет | Официальные правила **D&D 5e до редакции 2024** (PHB 2014 / SRD 5.1). **Не** использовать правила PHB 2024+ как канон для этого проекта |

**При противоречии:** официальные правила 5e до 2024 (шаг 2) > пересказ в `docs/rules/` (шаг 1). После уточнения дополняй `docs/rules/`. После правок справочника при необходимости — `python scripts/build_rules_index.py` (нормализация индексов).

Подробнее: [`docs/rules/README.md`](../../docs/rules/README.md).

## Agent-loop

[`AGENTS.md`](../../AGENTS.md) · git/verify/review — [`dnd-mud-workflow.md`](dnd-mud-workflow.md).

## Local rules (index)

| Файл | Globs | Канон |
|------|-------|-------|
| `dnd-mud-workflow.md` | always | git/verify/review overrides |
| `dnd-mud-python.md` | `**/*.py` | Python 3.12, KISS |
| `dnd-mud-tests.md` | `tests/**` | pytest |
| `dnd-mud-core.md` | `core/**`, `ui/**`, `main.py` | слои, механика |
| `dnd-mud-data.md` | `database/**`, `mods/**`, `**/*.json` | YAML/JSON |
