# Development Guide — dnd_mud

## Быстрый старт

### Предварительные требования

- Python 3.12+ (синтаксис и tooling — [`.cursor/rules/dnd-mud-python.mdc`](../.cursor/rules/dnd-mud-python.mdc))
- Git

### Установка

```bash
git clone git@github.com:discipleartem/dnd_mud.git
cd dnd_mud
make install   # venv + pip install -e ".[dev]"
```

Или вручную:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Запуск

```bash
source .venv/bin/activate
python main.py
```

Или через установленный скрипт:

```bash
source .venv/bin/activate
dnd_mud
```

### Тестирование

```bash
make test          # полный pytest + coverage (core, ui)
make verify-scope  # инкрементально на конец task-ветки (vs origin/dev)
VERIFY_BASE=origin/main make verify-scope  # на ветке dev — diff vs main
pytest -v
```

## Структура проекта

```
dnd_mud/
├── main.py                  # Точка входа
├── pyproject.toml           # Конфигурация проекта
├── README.md
├── core/                    # Игровое ядро
│   ├── models.py            # Dataclass: Character, Adventure
│   ├── character.py         # Узкий фасад для flow-оркестраторов (_deps)
│   ├── character_builder.py # resolve_creation_grants, merge языков/компетентности
│   ├── catalog_loader.py    # load_catalog — единая загрузка YAML-каталогов + mod overlay
│   ├── hp_bonuses.py        # Бонусы HP из grants (раса, черта)
│   ├── feats_loader.py      # Загрузка feats.yaml
│   ├── grant_mechanics.py   # Парсинг proficiency-токенов из grants
│   ├── feats.py             # Публичный фасад черт (гранты + apply)
│   ├── character_storage.py # CRUD персонажей (JSON в saves/)
│   ├── slug.py              # make_save_slug — транслитерация имён
│   ├── stats.py             # Генерация и валидация характеристик
│   ├── races.py             # Справочник рас
│   ├── classes.py           # Справочник классов
│   ├── io.py                # load_yaml / load_json
│   ├── adventure.py         # Загрузка приключений из YAML
│   ├── difficulty.py        # Фильтр приключений по режиму сложности
│   ├── dice.py              # Броски кубиков
│   ├── localization.py      # Локализация UI и resolve_localized_text
│   ├── grants.py            # Нормализация grants[] из YAML
│   ├── mod_loader.py        # Deep-merge overlay модов
│   └── settings.py          # Настройки пользователя (JSON)
├── ui/                      # Пользовательский интерфейс
│   ├── input_handler.py     # Валидация ввода (числа, строки, выбор)
│   └── menus/               # Пакет экранов меню
│       ├── main_menu.py
│       ├── new_game.py
│       ├── _creation_steps.py  # Тонкий loop создания персонажа
│       ├── _creation_handlers.py, _creation_navigation.py, _creation_finalize.py, _creation_state.py
│       ├── characters_menu.py
│       ├── _corrupt_saves.py
│       ├── feats/           # Выбор черт (creation + level-up)
│       ├── settings.py
│       ├── stats/           # Генерация характеристик (подпакет)
│       ├── _common.py       # SEPARATOR, _run_numbered_menu, …
│       ├── _display/        # Пакет отображения (класс, раса, stats, персонаж)
│       ├── _selectors.py
│       └── _deps.py         # Re-export core.character + input_handler (flows only)
├── database/                # YAML-справочники D&D 5e
│   ├── races/
│   │   └── races.yaml       # Расы и подрасы
│   ├── classes/
│   │   └── classes.yaml     # Классы персонажей
│   ├── backgrounds/
│   │   └── backgrounds.yaml # Предыстории PHB (grants[])
│   ├── content/adventures.yaml
│   ├── core/
│   │   ├── settings.json.example
│   │   ├── mods_state.json  # Включённые моды
│   │   └── languages.yaml
│   ├── strings/
│       ├── ru.yaml
│       └── en.yaml
├── saves/                   # Пользовательские данные (gitignored)
│   └── characters/          # Сохранённые персонажи (по одному JSON на персонажа)
├── adventures/      # Сценарии приключений (tutorial, lost_mine)
│   ├── tutorial.yaml
│   └── lost_mine.yaml
├── mods/
│   └── dragonborn_pack/     # Пример mod overlay (manifest + overlay.yaml)
├── tests/                   # pytest
│   ├── conftest.py
│   ├── test_adventure.py
│   ├── test_character.py
│   ├── test_difficulty.py
│   ├── test_dice.py
│   ├── test_input_handler.py
│   ├── test_io.py
│   ├── test_localization.py
│   ├── test_main.py
│   ├── test_menus_character.py
│   ├── test_menus_main.py
│   ├── test_menus_stats.py
│   ├── test_models.py
│   ├── test_races.py
│   ├── test_verify_targets.py
│   ├── test_settings.py
│   ├── test_stats.py
│   ├── test_grants.py
│   └── test_mod_loader.py
└── docs/                    # Документация
    ├── DATA_SCHEMA.md       # Схема YAML (grants, subraces, mods)
    ├── DND_RULES.md         # Правила D&D 5e (справочник по PHB)
    ├── rules/               # Главы справочника
    ├── MUD_PRD.md
    ├── ARCHITECTURE.md
    ├── API.md
    ├── DEVELOPMENT.md
    └── CHANGELOG.md
```

### UI → core imports

| Слой | Импорт |
|------|--------|
| Flows (`_creation_steps`, `new_game`, `characters_menu`, …) | `ui/menus/_deps` |
| Экраны (`feats/`, `level_up`, `_display/`) | Прямые `from core.*` |

`core/character.py` синхронизирован с `_deps` — не дублировать leaf-API в фасаде.

## Линтинг и форматирование

```bash
make check            # полный: ruff + black --check + mypy
make verify-changed   # только staged .py (подзадача)
make verify-scope     # diff origin/dev...HEAD (конец task-ветки)
VERIFY_BASE=origin/main make verify-scope  # на ветке dev
make verify           # check + test (CI / ручной full)
```

Маппинг changed → pytest/lint: [`scripts/verify_targets.py`](../scripts/verify_targets.py).

Инкрементальный `mypy` в `verify-changed` / `verify-scope` проверяет только изменённые `.py`; полный typecheck — `make check` или CI.

### Pre-commit (локально)

Перед коммитом с изменениями кода или данных хук запускает `make verify-changed` (не полный CI).

```bash
make install-hooks   # или make install — подключает .githooks/pre-commit
```

Коммиты только в `docs/`, `.cursor/`, `.githooks/`, `AGENTS.md`, `.github/`, `.vscode/` — без прогона. Обход: `git commit --no-verify` (только если осознанно).

### CI (GitHub Actions)

Полный `make check` + `make test` — на PR в `dev` и `main`: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Тестирование

Проект использует `pytest`. Тесты находятся в `tests/`.

### Философия

> **Тесты — максимально простые и только необходимые:** один сценарий на изменение,
> без лишних абстракций и без погони за покрытием.

- Тесты — инструмент регрессии, не цель сама по себе
- При фиче или фиксе — минимальный diff в `tests/`: столько assert, сколько нужно для изменённого поведения
- Эталоны стиля: `tests/test_difficulty.py` (короткий unit), `tests/test_menus_character.py` (интеграция UI без тяжёлых моков)
- Не обязательно закрывать все пробелы из backlog Pre-Alpha — тест добавляется, когда есть реальное поведение, баг или риск регрессии

Подробные правила для агентов: `.cursor/rules/dnd-mud-tests.mdc`.

```python
# tests/test_menus_character.py
"""Тесты UI: выбор персонажа, подрасы, new game, приключения."""
```

Покрытие (актуальный список — `pytest --collect-only -q`; ключевые файлы):
- `test_display.py` — формат stats, карточка персонажа, grants на экране расы
- `test_grants.py` — нормализация grants, legacy features
- `test_mod_loader.py` — deep-merge overlay модов
- `test_adventure.py` — загрузка приключений, поля `hardcore_only`
- `test_character.py` — save/load, генерация stats, variant human, slug
- `test_difficulty.py` — `adventure_allows_difficulty()`
- `test_dice.py` — `roll`, `roll_ability_score`, `ability_modifier`
- `test_input_handler.py` — валидация int/str
- `test_io.py` — `load_yaml` / `load_json`
- `test_localization.py` — ключи en/ru, `resolve_localized_text`, `get_string` default
- `test_main.py` — импорт `main`, VERSION
- `test_menus_character.py` — подрасы, new game, фильтр приключений
- `test_menus_main.py` — главное меню, select_difficulty
- `test_menus_stats.py` — генерация характеристик (standard array, point-buy, 4d6, HardCore)
- `test_models.py` — сериализация Character/Adventure
- `test_verify_targets.py` — маппинг incremental verify
- `test_settings.py` — save/load JSON, `schema_version`
- `test_stats.py` — validate_point_buy_finish, point_buy_points_remaining

Запуск конкретного тестового файла:

```bash
pytest tests/test_menus_character.py -v
```

## Git Workflow

Канон agent: [`.cursor/rules/dnd-mud-workflow.mdc`](../.cursor/rules/dnd-mud-workflow.mdc) · оркестрация [`AGENTS.md`](../AGENTS.md) · global [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc). Sync FAQ: [`~/.cursor/docs/git-dev-main-sync.md`](~/.cursor/docs/git-dev-main-sync.md).

IDE: расширения **GitHub Pull Requests** и **GitHub Actions** — настройки [`.vscode/settings.json`](../.vscode/settings.json) (squash merge, фильтры PR).

### Цикл задачи

```
git-старт → task-ветка → подзадачи (commits) → docs → verify → review (light|full) → push → PR task→dev
→ (накопление в dev) → PR dev→main → Action sync dev←main
```

### Git-старт (перед работой)

См. [`dnd-mud-workflow.mdc`](../.cursor/rules/dnd-mud-workflow.mdc) §Git и [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle шаг 1.

```bash
git fetch origin
git checkout main && git pull origin main
git checkout dev && git pull origin dev
git log dev..origin/main --oneline   # must be empty
git merge origin/main && make verify-scope && git push origin dev   # если main впереди
git checkout -b feat/my-task
```

### Завершение task-ветки

См. [`dnd-mud-workflow.mdc`](../.cursor/rules/dnd-mud-workflow.mdc) §Git (delta).

```bash
git fetch origin && git rebase origin/dev
make verify-scope
# skill dnd-mud-review — light или full, один раз, до push/PR
git push -u origin HEAD        # после rebase на remote: --force-with-lease
gh pr create --base dev --title "feat: …"   # squash merge
```

### Code review (локальный, не GitHub Bugbot)

Канон: skill [`.cursor/skills/dnd-mud-review`](../.cursor/skills/dnd-mud-review/SKILL.md).

| Канал | Использование |
|-------|----------------|
| **Light review** (оркестратор, diff vs `dev`) | Узкий diff без `core/`/`database/`/`mods/`/`ui/`/`main.py` — критерии и метрики: skill [`dnd-mud-review`](../.cursor/skills/dnd-mud-review/SKILL.md) (`git diff --shortstat`, `--name-only`) |
| **Full review** (subagent `bugbot`) | Рискованные изменения; явный запрос «полный review» |
| GitHub PR Bugbot (авто на push, `.cursor/BUGBOT.md`) | **Нет** |

Повтор после fix Blocker — **light re-check** (не full bugbot по умолчанию). Release `dev` → `main` — без обязательного bugbot; см. skill [`dnd-mud-release`](../.cursor/skills/dnd-mud-release/SKILL.md).

Quality gate на PR `task → dev`: локальный `make verify-scope` + review (light или full). Полный pytest/lint — CI [`ci.yml`](../.github/workflows/ci.yml) на PR в `dev`/`main`; sync-check release — [`pr-dev-to-main-check.yml`](../.github/workflows/pr-dev-to-main-check.yml).

#### Рекомендуемые настройки Cursor IDE

Cursor Settings → **Agent Review**:

| Настройка | Значение |
|-----------|----------|
| Start Agent Review on Commit | **OFF** |
| Include Submodules in Agent Review | **OFF** |
| Include Untracked Files in Agent Review | **OFF** |
| Default Approach | **Quick** |

Auto-review на каждый commit дублирует skill `dnd-mud-review` и сильно увеличивает расход `agent_review` в [dashboard usage](https://cursor.com/dashboard/usage).

### Экономия токенов Agent

| Практика | Зачем |
|----------|-------|
| Короткие task-ветки (1 фича, 1–3 дня) | Меньше контекста и diff |
| Один чат ≈ одна ветка | Не тащить историю прошлых задач |
| Review один раз в конце (light или full) | Не дублировать проверку в чате и bugbot |
| `rebase origin/dev` перед full review | Минимальный diff для bugbot |
| Plan mode для крупных задач | Меньше итераций fix в Agent |
| Узкий scope в промпте | Меньше лишних файлов в контексте |
| Grep/Read вместо Task/explore для 1–2 файлов | Дешевле subagent |
| `make test` вместо повторных «проверь ещё раз» в чате | Runtime без LLM |

Мониторинг: раз в неделю [cursor.com/dashboard/usage](https://cursor.com/dashboard/usage) — рост `agent_review` vs `auto`.

### Release (`dev` → `main`)

**Только через PR** — без PR в `main` не релизим (локальный merge/push в `main` запрещён).

```bash
git fetch origin && git checkout dev && git pull origin dev
git log dev..origin/main --oneline   # must be empty
git merge origin/main --no-commit --no-ff && git merge --abort   # пробная проверка, не релиз
make test
gh pr create --base main --head dev --title "release: …"
# CI dev-sync-and-mergeable → gh pr merge <number> --squash
```

CI: [`.github/workflows/pr-dev-to-main-check.yml`](../.github/workflows/pr-dev-to-main-check.yml) (только PR `dev` → `main`, события open/sync). После merge в `main` — [`.github/workflows/sync-dev-with-main.yml`](../.github/workflows/sync-dev-with-main.yml).

**GitHub (Rules → `main_rules`):** required status check — **`dev-sync-and-mergeable`** (имя job, не имя workflow/файла); merge method — squash.

## Создание мода

Канон overlay и `grants`: [`DATA_SCHEMA.md`](DATA_SCHEMA.md) § Mod overlay.

Моды — каталог `mods/<id>/` с `manifest.yaml` и фрагментами YAML. Включение: `database/core/mods_state.json` (`enabled: ["mod_id"]`).

Пример:

```yaml
# mods/dragonborn_pack/manifest.yaml
id: dragonborn_pack
overlays:
  - target: database/races/races.yaml
    path: overlay.yaml
```

Overlay-фрагмент (`overlay.yaml`) — partial YAML с ключом каталога (`races:`, …). Runtime: `core/catalog_loader.load_catalog` → deep-merge через `core/mod_loader.py`.

## Добавление локализации

1. Открыть `database/strings/ru.yaml` или `database/strings/en.yaml`
2. Добавить ключ в нужное место:

```yaml
menu:
  new_game: "Новая игра"
  my_new_item: "Мой новый пункт"  # <-- новый ключ
```

3. Использовать в коде:

```python
get_string(strings, 'menu.my_new_item')
```

Для форматирования с параметрами:

```yaml
welcome:
  version: "Версия: {version}"
```

```python
get_string(strings, 'welcome.version', version='0.1.0')
```

## Добавление новой расы/класса

1. Открыть `database/races/races.yaml` или `database/classes/classes.yaml`
2. Добавить запись по образцу существующих (схема: [`DATA_SCHEMA.md`](DATA_SCHEMA.md))
3. Перезапустить игру

```yaml
# races.yaml — механика в subraces + grants[]
races:
  new_race:
    name: { ru: "Новая раса", en: "New Race" }
    size: medium
    speed: 30
    subraces:
      new_race:
        ability_bonuses: { strength: 2, dexterity: 1 }
        grants:
          - type: language
            languages: [common]
```

## Текущее состояние разработки

### Реализовано (core)
- ✅ `core/models.py` — типизированные dataclass: Character, Adventure
- ✅ `core/character.py` — фасад API персонажей, adventure, backgrounds, dice, languages
- ✅ `core/dice.py` — `roll`, `roll_ability_score`, `ability_modifier`
- ✅ `core/localization.py` — YAML-словари с fallback на английский
- ✅ `core/settings.py` — настройки пользователя (язык)
- ✅ `core/adventure.py` — загрузка приключений из YAML
- ✅ `core/difficulty.py` — `adventure_allows_difficulty()`; UI-фильтр в `_select_adventure()`

### Реализовано (ui)
- ✅ `ui/input_handler.py` — валидация ввода (int, str)
- ✅ `ui/menus/` — главное меню, настройки, languages, flows
- ✅ `ui/menus/stats/` — генерация характеристик (standard / point-buy / random)
- ✅ Flow «Новая игра» (персонаж → приключение → `scenario_flow.run_scenario`)
- ✅ Flow «Создать персонажа» — `ui/menus/_creation_steps.py` (`show_create_character_flow`)
- ✅ Flow «Загрузить игру» — заглушка (`errors.load_not_implemented`)

### Тестирование
- ✅ pytest suite (`make test`; число кейсов: `pytest --collect-only -q`)
- ⏳ Backlog (добавляются по необходимости, см. [философию](#философия) выше):
  - E2E smoke через `python main.py` (ручная проверка меню)

### Настройки: difficulty

Спецификация режимов: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

| ID | UI (ru) | Статус |
|----|---------|--------|
| `normal` | Нормальная | Реализовано в UI |
| `hardcore` | HardCore | Реализовано в UI |
| `easy` | Лёгкая | Реализовано (старт 3 ур., обязательный подкласс) |

- `difficulty` выбирается в flow «Создать персонажа» (`select_difficulty`); сохраняется в `Character.difficulty` и используется в «Новая игра»
- Поле `difficulty` в `adventures.yaml` — **уровень контента**, не режим игрока (не путать с `Character.difficulty`)

### Генерация характеристик

Спецификация UX (методы, HardCore, расовые бонусы, переквалификация): [MUD_PRD.md §3.4.5](MUD_PRD.md#345-генерация-характеристик-реализовано).  
API: `core/character.py`, UI: `show_stats_generation_flow` в `ui/menus/stats/stats_flow.py`.

### База данных
- ✅ Справочники: `races/races.yaml`, `classes/classes.yaml`, `content/adventures.yaml`
- ✅ JSON: `database/core/settings.json`, `saves/characters/*.json` (с `schema_version: 1`)
- ✅ Локализация: `strings/ru.yaml`, `strings/en.yaml`

### Не реализовано
- ❌ Gating модов по режиму (`requires_game_difficulty` в manifest)
- ❌ Параметризация game_engine по режиму сложности
- ❌ Полноценный game engine (сценарии — минимальный runner в `scenario_flow.py`)
- ❌ Боевая система
- ❌ Сохранение/загрузка состояния игры (flow «Загрузить игру»)
- ❌ Сценарии приключений — базовый runner (`tutorial`, `lost_mine`); без боевой системы
- ❌ Отдельные пункты меню «Модификации» / «Приключения» (приключения — внутри «Новая игра»)
- ❌ Обработка модов во время выполнения