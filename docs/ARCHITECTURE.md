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
| `ui/menus/_creation_steps.py` | Flow «Создать персонажа» + state machine шагов |
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
| `ui/menus/characters_menu.py` | Список персонажей; кэш `LoadCharactersResult`, reload после create/delete |
| `ui/menus/_corrupt_saves.py` | Предупреждение о битых JSON в `saves/characters/` |
| `ui/menus/feats/` | Выбор черт при создании и левелапе (публичный API в `__init__.py`) |
| `ui/menus/_creation_handlers.py`, `_creation_navigation.py`, `_creation_finalize.py`, `_creation_state.py` | State machine создания персонажа |
| `ui/menus/_common.py`, `_display/`, `_deps.py` | Общие хелперы, отображение (пакет), seam для тестов |
| `ui/input_handler.py` | Валидация ввода, UTF-8 для stdin/stdout |

UI не читает файлы данных напрямую — только через `core/`.

**Импорты UI → core (deps policy):**

1. **Flows и оркестраторы** (`_creation_steps`, `new_game`, `characters_menu`, …) — только `ui/menus/_deps` (monkeypatch в тестах).
2. **Специализированные экраны** (`feats/`, `level_up`, `_display/`) — прямые leaf-imports из `core.*`, без дублирования в `_deps`.

`core/character.py` — узкий фасад для п.1 (stats, save/load, каталоги создания), не «весь core».

### 2. Core Layer (`core/`)

| Модуль | Назначение |
|--------|-----------|
| `core/models.py` | `Character`, `Adventure` (dataclass) |
| `core/character.py` | Узкий фасад для flow-оркестраторов (`_deps`): save/load, stats, каталоги создания |
| `core/character_builder.py` | `ResolvedGrants`, `resolve_creation_grants` — единая сборка владений при создании |
| `core/character_storage.py` | CRUD персонажей (JSON в `saves/`) |
| `core/types.py` | `StatMap`, `GameDifficulty`, `RuntimeSettings` |
| `core/abilities.py` | Каталог характеристик и навыков из YAML |
| `core/races.py` | Справочник рас, `collect_race_grants`, расовые бонусы |
| `core/classes.py` | Справочник классов, `get_class_dict`, hit dice, подклассы |
| `core/subclasses.py` | Уровень выбора подкласса, gating по режиму сложности |
| `core/class_features.py` | Отложенные особенности класса/подкласса |
| `core/backgrounds.py` | Каталог предысторий PHB |
| `core/skills.py` | Навыки при создании персонажа |
| `core/languages.py` | Каталог языков PHB, пулы выбора |
| `core/proficiencies.py` | Владения оружием, доспехами, инструментами |
| `core/equipment.py` | Оружие, доспехи, инструменты из YAML |
| `core/feats.py` | Публичный фасад черт (требования, гранты, применение) |
| `core/feat_visibility.py` | Скрытие черт в меню выбора по расе/классу и владениям |
| `core/feats_loader.py` | Загрузка `feats.yaml` |
| `core/grant_mechanics.py` | Парсинг proficiency-токенов из grant dict |
| `core/asi.py` | ASI при левелапе |
| `core/expertise.py` | Компетентность (rogue, bard, …) |
| `core/hp_bonuses.py` | Источники бонусов HP из features |
| `core/progression.py` | XP, уровни, HP, `process_pending_level_ups`, `grant_experience` |
| `core/levels.py` | `MAX_CHARACTER_LEVEL` |
| `core/constants.py` | PB, DC из YAML |
| `core/grants.py` | Нормализация `grants[]` из YAML |
| `core/stats.py` | Генерация/валидация характеристик |
| `core/dice.py` | `roll()`, `roll_ability_score()`, `ability_modifier()` |
| `core/slug.py` | `make_save_slug()` |
| `core/io.py` | `load_yaml()` / `load_json()` (`strict` для каталогов), `save_json()` / `merge_unique()` |
| `core/catalog_loader.py` | `load_catalog()`, `clear_catalog_cache()`, `clear_all_catalog_caches()` |
| `core/adventure.py` | `load_adventures()` |
| `core/scenario_actions.py` | Чистая логика action-узлов сценария (без UI) |
| `core/difficulty.py` | `adventure_allows_difficulty()` |
| `core/localization.py` | `load_strings()` (кэш), `get_string()` |
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

- Оркестрация: `ui/menus/_creation_steps.py` (`show_create_character_flow`), `ui/menus/stats/stats_flow.py`
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
| `easy` | Старт 3 ур., обязательный подкласс; характеристики как Normal | Упрощённая механика engine / обучение |

Фильтрация приключений: `core/difficulty.py` (`adventure_unavailable_reason`) + `_select_adventure()` в `ui/menus/new_game.py`. Каталог `adventures.yaml` задаёт `min_level`, `allowed_game_difficulties`, `hardcore_only`; недоступные приключения — серым списком с причиной.  
Спецификация: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

**Настройки:** только `language` в `settings.json`; режим сложности — в `Character.difficulty`. Имена рас и классов в YAML — bilingual `{ ru, en }`, резолв через `resolve_localized_text()` и параметр `language` в loaders.

## Связанные документы

- [API Reference](API.md)
- [Development Guide](DEVELOPMENT.md)
- [MUD_PRD.md](MUD_PRD.md)
