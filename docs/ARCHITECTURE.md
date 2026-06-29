# Architecture — dnd_mud

## Общая архитектура

```
┌────────────────────────────────────┐
│           UI Layer (ui/)           │
│   Меню, ввод/вывод, отображение    │
├────────────────────────────────────┤
│          Core Layer (core/)        │
│   Игровое ядро, модели, логика     │
├────────────────────────────────────┤
│        Data Layer (database/)      │
│   YAML-файлы, моды, локализация    │
└────────────────────────────────────┘
```

## Слои

### 1. UI Layer (`ui/`)

| Модуль | Назначение |
|--------|-----------|
| `ui/menus/` | Пакет экранов меню (flows по файлам) |
| `ui/menus/main_menu.py` | Приветствие, главное меню, заглушка «Загрузить игру» |
| `ui/menus/new_game.py` | Flow «Новая игра» |
| `ui/menus/character_flow.py` | Точка входа flow «Создать персонажа» |
| `ui/menus/_creation_steps.py` | State machine создания персонажа |
| `ui/menus/_selectors.py` | Общие селекторы расы, класса, подкласса |
| `ui/menus/scenario_flow.py` | Интерактивный runner YAML-сценариев |
| `ui/menus/subclass_trainer.py` | NPC-наставник: поздний выбор подкласса |
| `ui/menus/languages.py` | Выбор языков расы/подрасы |
| `ui/menus/backgrounds.py` | Выбор предыстории |
| `ui/menus/skills.py` | Выбор навыков класса |
| `ui/menus/stats/` | Пакет генерации характеристик |
| `ui/menus/stats/stats_flow.py` | Оркестратор flow stats |
| `ui/menus/stats/stats_shared.py` | Пул, confirm, общие шаги |
| `ui/menus/stats/stats_methods.py` | Standard array, point-buy, random |
| `ui/menus/stats/stats_choice_bonuses.py` | Выборные расовые бонусы |
| `ui/menus/settings.py` | Настройки, языки, выбор сложности |
| `ui/menus/_common.py`, `_display/`, `_deps.py` | Общие хелперы, отображение (пакет), seam для тестов |
| `ui/input_handler.py` | Валидация ввода, UTF-8 для stdin/stdout |

UI не читает файлы данных напрямую — только через `core/`.

### 2. Core Layer (`core/`)

| Модуль | Назначение |
|--------|-----------|
| `core/models.py` | `Character`, `Adventure` (dataclass) |
| `core/character.py` | Фасад: персонажи, stats, adventure, backgrounds, dice, languages; источник для `_deps` |
| `core/character_storage.py` | CRUD персонажей (JSON в `saves/`) |
| `core/types.py` | `StatMap`, `GameDifficulty`, `RuntimeSettings` |
| `core/abilities.py` | Каталог характеристик и навыков из YAML |
| `core/races.py` | Справочник рас, `collect_race_features`, расовые бонусы |
| `core/classes.py` | Справочник классов, hit dice, подклассы |
| `core/subclasses.py` | Уровень выбора подкласса, gating по режиму сложности |
| `core/class_features.py` | Отложенные особенности класса/подкласса |
| `core/backgrounds.py` | Каталог предысторий PHB |
| `core/skills.py` | Навыки при создании персонажа |
| `core/languages.py` | Каталог языков PHB, пулы выбора |
| `core/proficiencies.py` | Владения оружием, доспехами, инструментами |
| `core/equipment.py` | Оружие, доспехи, инструменты из YAML |
| `core/feats.py` | Публичный фасад черт (требования, описания) |
| `core/feats_loader.py` | Загрузка `feats.yaml` |
| `core/feats_grants.py` | Гранты черт, применение к stats/персонажу |
| `core/asi.py` | ASI при левелапе |
| `core/expertise.py` | Компетентность (rogue, bard, …) |
| `core/hp_bonuses.py` | Источники бонусов HP из features |
| `core/progression.py` | XP, уровни, HP, `grant_experience` |
| `core/levels.py` | `MAX_CHARACTER_LEVEL` |
| `core/combat.py` | Атака, КД, штрафы за доспех |
| `core/checks.py` | Проверки навыков и спасбросков |
| `core/constants.py` | PB, DC из YAML |
| `core/grants.py` | Нормализация `grants[]` из YAML |
| `core/stats.py` | Генерация/валидация характеристик |
| `core/dice.py` | `roll()`, `roll_ability_score()`, `ability_modifier()` |
| `core/slug.py` | `make_save_slug()` |
| `core/io.py` | `load_yaml()` / `load_json()` |
| `core/adventure.py` | `load_adventures()` |
| `core/scenario_actions.py` | Чистая логика action-узлов сценария (без UI) |
| `core/difficulty.py` | `adventure_allows_difficulty()` |
| `core/localization.py` | `load_strings()`, `get_string()` |
| `core/settings.py` | Настройки в `database/core/settings.json` |
| `core/mod_loader.py` | Deep-merge overlay модов в каталоги YAML |

### 3. Data Layer (`database/`, `saves/`)

Канон формата YAML: [`DATA_SCHEMA.md`](DATA_SCHEMA.md) (grants, subraces, mod overlay, Phase 2+ backlog).

| Путь | Назначение | Формат | Модуль |
|------|-----------|--------|--------|
| `database/races/races.yaml` | Расы | YAML | `races.py` |
| `database/classes/classes.yaml` | Классы | YAML | `classes.py` |
| `database/core/languages.yaml` | Языки PHB | YAML | `languages.py` |
| `database/backgrounds/backgrounds.yaml` | Предыстории PHB | YAML | `backgrounds.py` |
| `database/content/adventures.yaml` | Каталог приключений | YAML | `adventure.py` |
| `database/core/settings.json` | Настройки | JSON | `settings.py` |
| `saves/characters/*.json` | Персонажи (по одному файлу) | JSON | `character_storage.py` |
| `database/strings/*.yaml` | Локализация | YAML | `localization.py` |
| `database/core/mods_state.json` | Включённые моды | JSON | `mod_loader.py` |

### 4. Resources (`adventures/`, `mods/`)

| Путь | Назначение |
|------|-----------|
| `adventures/*.yaml` | Сценарии приключений (`tutorial`, `lost_mine`) — runner в `scenario_flow.py` |
| `mods/dragonborn_pack/` | Пример mod overlay (deep-merge) | YAML | `mod_loader.py` |
| `mods/_examples/` | Устаревший пример manifest | YAML | — |
| `database/_future/` | Справочники Phase 2 (не загружаются) | YAML | — |

## Поток данных

```
main.py → ui/menus/ → core/character.py (фасад) → character_storage, races, classes, stats
                    → core/races.py, core/backgrounds.py
                         → core/mod_loader.py → database/*/*.yaml + mods/*/overlay.yaml
                         → core/grants.py (нормализация grants[])
                    → core/settings.py → database/core/settings.json
                    → core/adventure.py → database/content/adventures.yaml
                    → core/localization.py → database/strings/*.yaml
```

**Сценарий «Новая игра»:** персонаж → приключение (фильтр по режиму) → `run_scenario()` в `ui/menus/scenario_flow.py` (grant XP, subclass training, меню узлов).

**Сценарий «Создать персонажа»:** сложность → имя → раса → подраса → характеристики → предыстория → языки → класс → подкласс → черты (если нужны) → владения → навыки → (компетентность?) → сохранение в `saves/characters/{save_slug}.json`.

- Оркестрация: `ui/menus/_creation_steps.py`, `ui/menus/character_flow.py`, `ui/menus/stats/stats_flow.py`
- Генераторы: `core/stats.py`, `core/races.py` (через фасад `core/character.py`)
- Броски 4d6: `core/dice.py` (`roll_ability_score`)

Подробная спецификация UX генерации характеристик: [MUD_PRD.md §3.4.6](MUD_PRD.md#346-генерация-характеристик-реализовано).

## Режим сложности игры

`Character.difficulty` задаётся в flow «Создать персонажа» и используется в «Новая игра»:

```
select_difficulty() → show_stats_generation_flow() → adventure_allows_difficulty() → [будущее] правила game_engine
```

| Режим | Реализовано сегодня | Запланировано |
|-------|---------------------|---------------|
| `normal` | 3 метода характеристик, переквалификация | Базовая механика engine |
| `hardcore` | Авто-4d6×6, без переквалификации; фильтр приключений в UI | Gating модов, полная механика D&D 5e |
| `easy` | — | Упрощённая механика / обучение |

Фильтрация приключений: `core/difficulty.py` (`adventure_unavailable_reason`) + `_select_adventure()` в `ui/menus/new_game.py`. Каталог `adventures.yaml` задаёт `min_level`, `allowed_game_difficulties`, `hardcore_only`; недоступные приключения — серым списком с причиной.  
Спецификация: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

**Настройки:** только `language` в `settings.json`; режим сложности — в `Character.difficulty`. Имена рас и классов в YAML — bilingual `{ ru, en }`, резолв через `resolve_localized_text()` и параметр `language` в loaders.

## Связанные документы

- [API Reference](API.md)
- [Development Guide](DEVELOPMENT.md)
- [MUD_PRD.md](MUD_PRD.md)
