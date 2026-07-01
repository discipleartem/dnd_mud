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
make test-fast     # pytest без coverage (быстрый локальный цикл)
make test          # pytest + coverage (CI)
make test-cov      # coverage + term-missing (детальный отчёт)
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
├── tests/                   # pytest (число: pytest --collect-only -q)
│   ├── conftest.py
│   ├── creation_helpers.py  # общие константы golden-path
│   ├── test_*.py            # ~20 файлов: core / menus / data / meta
│   └── …                    # см. группы в §Тестирование ниже
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

Маппинг changed → pytest/lint: [`scripts/verify_targets.py`](../scripts/verify_targets.py). Если хотя бы один изменённый `.py` не смапился — full suite (не только когда mapped-тестов нет совсем).

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
- На сценарий — **один** тест на слой: core **или** 0–1 UI smoke (monkeypatch-навигация), не дублировать unit + integration одного пути
- Похожие кейсы — `@pytest.mark.parametrize`, не копии функций; мелкие домены — в существующий `test_*.py`, не новый файл на 1–2 теста
- При фиче или фиксе — минимальный diff в `tests/`: столько assert, сколько нужно для изменённого поведения
- Эталоны стиля: `tests/test_stats.py` (короткий unit), `tests/test_menus_creation.py` (UI smoke)
- Бюджет и антипаттерны: `.cursor/rules/dnd-mud-tests.mdc` §Бюджет на PR

Покрытие — актуальный список: `pytest --collect-only -q`. Группы файлов:

| Группа | Файлы (примеры) |
|--------|-----------------|
| **core** | `test_stats`, `test_grants`, `test_character`, `test_character_builder`, `test_proficiencies`, `test_progression`, `test_feats`, `test_subclasses`, `test_asi`, `test_expertise`, `test_languages`, `test_class_features`, `test_equipment` |
| **menus** | `test_menus_main`, `test_menus_creation`, `test_menus_new_game`, `test_menus_characters_hub`, `test_menus_stats` |
| **data** | `test_catalog_loader`, `test_data_schema`, `test_io`, `test_models` (adventures/backgrounds) |
| **meta** | `test_verify_targets`, `test_localization` |

Подробные правила для агентов: `.cursor/rules/dnd-mud-tests.mdc`. Не обязательно закрывать все пробелы из backlog Pre-Alpha — тест добавляется при реальном поведении, баге или риске регрессии.

Запуск конкретного тестового файла:

```bash
pytest tests/test_menus_creation.py -v
pytest tests/test_data_schema.py -v
```

## Git Workflow

Канон для агентов — **не дублировать команды здесь**:

| Тема | Канон |
|------|-------|
| Agent-loop, steps, skills | [`AGENTS.md`](../AGENTS.md) |
| Git-старт, rebase, multi-branch, PR, `merged/*` (локально) | [`.cursor/rules/dnd-mud-workflow.mdc`](../.cursor/rules/dnd-mud-workflow.mdc) |
| Task cycle (global) | [`01-operations.mdc`](~/.cursor/rules/01-operations.mdc) §Task cycle |
| Verify | skill [`.cursor/skills/dnd-mud-verify`](../.cursor/skills/dnd-mud-verify/SKILL.md) |
| Review | skill [`.cursor/skills/dnd-mud-review`](../.cursor/skills/dnd-mud-review/SKILL.md) |
| Release `dev` → `main` | skill [`.cursor/skills/dnd-mud-release`](../.cursor/skills/dnd-mud-release/SKILL.md) |
| Sync `dev`←`main` | [`git-dev-main-sync.md`](~/.cursor/docs/git-dev-main-sync.md) |

IDE: расширения **GitHub Pull Requests** и **GitHub Actions** — [`.vscode/settings.json`](../.vscode/settings.json).

### Code review

Канон: skill [`.cursor/skills/dnd-mud-review`](../.cursor/skills/dnd-mud-review/SKILL.md). GitHub PR Bugbot — **нет**.

Quality gate PR `task → dev`: `make verify-scope` + review (light/full). Full pytest/lint — CI [`ci.yml`](../.github/workflows/ci.yml).

### Cursor IDE (Agent Review)

Канон: [`.cursor/rules/dnd-mud-workflow.mdc`](../.cursor/rules/dnd-mud-workflow.mdc) §Verify / review — Agent Review on Commit **OFF**, Default Approach **Quick**.

### Экономия токенов Agent

| Практика | Зачем |
|----------|-------|
| Короткие task-ветки (1 фича, 1–3 дня) | Меньше контекста и diff |
| Один чат ≈ одна интеграционная ветка к PR | Вспомогательные ветки по плану — ок, но перед PR слить в одну |
| Review один раз в конце (light или full) | Не дублировать проверку в чате и bugbot |
| `rebase origin/dev` перед full review | Минимальный diff для bugbot |
| Plan mode для крупных задач | Меньше итераций fix в Agent |
| Узкий scope в промпте | Меньше лишних файлов в контексте |
| Grep/Read вместо Task/explore для 1–2 файлов | Дешевле subagent |
| `make test-fast` / `make test` вместо повторных «проверь ещё раз» в чате | Быстрый feedback без coverage; полный прогон — перед PR |

Мониторинг: раз в неделю [cursor.com/dashboard/usage](https://cursor.com/dashboard/usage) — рост `agent_review` vs `auto`.

### Merge policy (GitHub Rulesets)

Один squash-коммит на PR — канон для обеих интеграционных веток.

| Куда | Push напрямую | Через PR | Merge method на PR |
|------|---------------|----------|-------------------|
| `dev` | **да** — `git push origin dev` | task-ветки → `dev` | squash (практика + default UI) |
| `main` | **нет** — только PR | `dev` → `main` | squash (`main_rules`) |

| PR | Enforcement | Required checks | Linear history |
|----|-------------|-----------------|----------------|
| `feat/…` → `dev` | squash по процессу; CI на PR | `quality` ([`ci.yml`](../.github/workflows/ci.yml)) | нет — sync `main`→`dev` добавляет merge-коммит |
| `dev` → `main` | ruleset **`main_rules`** | `dev-sync-and-mergeable` ([`pr-dev-to-main-check.yml`](../.github/workflows/pr-dev-to-main-check.yml)) | да |

**Прямой push в `dev` разрешён** — docs, мелкие fix, ручной sync; также [`sync-dev-with-main.yml`](../.github/workflows/sync-dev-with-main.yml) после релиза. На `dev` **нет** branch ruleset: ruleset с `pull_request` запретил бы и это.

**Почему нет `dev_rules`:** нельзя одновременно требовать «все изменения только через PR» и разрешать прямой push. Squash task→`dev` — дисциплина процесса + default **Squash** в GitHub UI, не ruleset.

Практика:

- feature-код → task-ветка → PR → **Squash and merge** в `dev` → rename в `merged/…` (локально) — [`.cursor/rules/dnd-mud-workflow.mdc`](../.cursor/rules/dnd-mud-workflow.mdc).
- `dev` → `main`: **только PR**, **Squash and merge** / `gh pr merge --squash` — skill [`.cursor/skills/dnd-mud-release`](../.cursor/skills/dnd-mud-release/SKILL.md).
- Вкладка **Commits** release PR может показывать много коммитов (расходящаяся ancestry после squash); ориентир — **Files changed** или `git diff origin/main...origin/dev`.

Rulesets: **Settings → Rules**. Только **`main_rules`** на `refs/heads/main`.

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

Merge policy и rulesets — § [Merge policy (GitHub Rulesets)](#merge-policy-github-rulesets) выше.

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

**Кросс-локальная подпись переключателя языка:** ключ `menu.languages` намеренно на «чужом» языке — при ru UI пункт **Languages**, при en UI — **Языки**, чтобы пользователь мог найти переключатель без знания текущей локали.

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

Открытые задачи Pre-Alpha и Phase 2 — [BACKLOG.md](BACKLOG.md).