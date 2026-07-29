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
| `ui/menus/main_menu.py` | Приветствие, главное меню |
| `ui/menus/load_game.py` | Flow «Загрузить игру» (сессии в `saves/sessions/`) |
| `ui/menus/mods_menu.py` | Включение/выключение модов |
| `ui/menus/new_game.py` | Flow «Новая игра» |
| `ui/menus/_creation_steps.py` | Flow «Создать персонажа» + state machine шагов |
| `ui/menus/_selectors.py` | Общие селекторы расы, класса, подкласса |
| `ui/menus/scenario_flow.py` | Runner YAML-сценариев через `GameEngine` |
| `ui/terminal_wrap.py` | Перенос текста под ширину терминала |
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
| `ui/menus/display/` | Отображение: grants, раса/фон, stats, карточка, экипировка, класс |
| `ui/menus/_display.py` | Совместимый re-export → `ui.menus.display` |
| `ui/menus/_subclass_picks.py` | Общий flow выбора владений/навыков/компетентности подкласса |
| `ui/input_handler.py` | Валидация ввода, UTF-8 для stdin/stdout |

UI не читает файлы данных напрямую — только через `core/`.

**Импорты UI → core:** прямые leaf-imports из `core.*` (и `ui.input_handler`). Monkeypatch в тестах — по точке использования в UI-модуле (`conftest.patch_int_input` и т.п.).

### 2. Core Layer (`core/`)

| Модуль | Назначение |
|--------|-----------|
| `core/models.py` | `Character` (`class_id: CharacterClass`), `Adventure` (dataclass); JSON coerce helpers |
| `core/grants_context.py` | `CreationContext`, `ResolvedGrants` — dataclass контекста создания |
| `core/character_build.py` | `build_new_character(CharacterBuildParams)` / `resolve_creation_grants` — сборка модели без записи на диск |
| `core/character_migrate.py` | `CHARACTERS_SCHEMA_VERSION`, `migrate_character_data` — версия JSON сейва при load |
| `core/character_storage.py` | CRUD персонажей; `make_save_slug`, `unique_save_slug`; JSON в `saves/` |
| `core/session_storage.py` | Снимки сессий приключений (`saves/sessions/`) |
| `core/game_engine.py` | `GameEngine`, `GameSession` — state machine сценария; `step_exit`, флаги сессии |
| `core/scenario_rooms.py` | `exits` в узлах YAML-сценария |
| `core/engine_rules.py` | Преимущество/помеха проверок по `GameDifficulty` |
| `core/combat.py` | Каркас Phase 2: `roll_initiative`, `attack_roll` |
| `core/hp_bonus.py` | `HpBonusSource`, бонусы HP из grants |
| `core/expertise.py` | Компетентность (expertise) из class features |
| `core/types.py` | Типы домена: `StatMap`, `CharacterClass`, `CharacterBuildParams`, … |
| `core/abilities.py` | Каталог характеристик и навыков из YAML |
| `core/races.py` | Справочник рас, `collect_race_grants`, расовые бонусы |
| `core/classes.py` | Справочник классов, `get_class_dict`, hit dice, подклассы |
| `core/skills.py` | Навыки при создании персонажа; `PHB_SKILL_IDS` |
| `core/languages.py` | Каталог языков PHB, пулы выбора |
| `core/proficiencies.py` | Сбор и проверки владений |
| `core/checks.py` | Проверки характеристик, навыков, спасбросков (`ability_check`, `skill_check`, …) |
| `core/inventory.py` | Инвентарь, экипировка, `compute_ac`, авто-экипировка |
| `core/starting_equipment.py` | Стартовое снаряжение класса из YAML |
| `core/equipment.py` | Оружие, доспехи, инструменты из YAML |
| `core/feats.py` | Черты: loader, apply, requirements, visibility, descriptions |
| `core/progression.py` | XP, уровни, HP, ASI, expertise, class features, подклассы (lazy-imports к `feats`/`races`) |
| `core/constants.py` | PB, DC; `MAX_CHARACTER_LEVEL`, `clamp_level` |
| `core/grants.py` | Нормализация `grants[]`; proficiency-токены (`normalize_armor_token`, …) |
| `core/backgrounds.py` | Каталог предысторий PHB |
| `core/stats.py` | Генерация/валидация характеристик |
| `core/dice.py` | `roll()`, `roll_ability_score()`, `ability_modifier()` |
| `core/io.py` | `load_file()` (универсальный YAML/JSON), `load_yaml()` / `load_json()` (`strict` для каталогов), `save_json()` / `merge_unique()` |
| `core/catalog_loader.py` | `load_catalog()`, `load_catalog_items()`, `bootstrap_session_catalogs()`, `reload_catalogs()` |
| `core/adventure.py` | `load_adventures()` |
| `core/scenario_actions.py` | Чистая логика action-узлов сценария (без UI) |
| `core/difficulty.py` | `adventure_allows_difficulty()` |
| `core/localization.py` | `load_strings()` (кэш), `get_string()` |
| `core/settings.py` | Настройки в `database/core/settings.json` |
| `core/mod_loader.py` | Deep-merge overlay модов; `requires`/`conflicts`; `delete`/`replace_entity`; gating по `requires_game_difficulty` |

### 3. Data Layer (`database/`, `saves/`)

Канон формата YAML: [`DATA_SCHEMA.md`](DATA_SCHEMA.md) (grants, subraces, mod overlay). Валидация: `database/schema/v1/*.json`, pytest `tests/test_data_schema.py`, CLI `scripts/validate_data.py`.

| Путь | Назначение | Формат | Модуль |
|------|-----------|--------|--------|
| `database/schema/v1/` | JSON Schema v1 (grants, backgrounds, adventures, progression, scenario_node) | JSON | `tests/test_data_schema.py` |
| `database/races/races.yaml` | Расы | YAML | `races.py` |
| `database/classes/classes.yaml` | Классы | YAML | `classes.py` |
| `database/core/languages.yaml` | Языки PHB | YAML | `languages.py` |
| `database/backgrounds/backgrounds.yaml` | Предыстории PHB | YAML | `backgrounds.py` |
| `database/content/adventures.yaml` | Каталог приключений | YAML | `adventure.py` |
| `database/core/settings.json` | Настройки | JSON | `settings.py` |
| `saves/characters/*.json` | Персонажи (по одному файлу) | JSON | `character_storage.py` |
| `saves/sessions/*.json` | Сессии приключений (узел сценария, флаги) | JSON | `session_storage.py` |
| `database/strings/*.yaml` | Локализация | YAML | `localization.py` |
| `database/core/mods_state.json` | Включённые моды | JSON | `mod_loader.py` |

### 4. Resources (`adventures/`, `mods/`)

| Путь | Назначение |
|------|-----------|
| `adventures/*.yaml` | Сценарии приключений (`tutorial`, `lost_mine`) — runner в `scenario_flow.py` |
| `mods/dragonborn_pack/` | Пример mod overlay (deep-merge) | YAML | `mod_loader.py` |

## Поток данных

```
main.py → ui/menus/ → core/* (прямые leaf-imports)
                    → core/races.py, core/backgrounds.py, core/character_storage.py, …
                         → core/mod_loader.py → database/*/*.yaml + mods/*/overlay.yaml
                         → core/grants.py (нормализация grants[])
                    → core/settings.py → database/core/settings.json
                    → core/adventure.py → database/content/adventures.yaml
                    → core/localization.py → database/strings/*.yaml
```

**Сценарий «Новая игра»:** персонаж → приключение (фильтр по режиму) → `run_scenario()` / `run_scenario_with_engine()` в `ui/menus/scenario_flow.py` (автосохранение сессии, grant XP, subclass training, skill_check).

**Сценарий «Загрузить игру»:** список `saves/sessions/` → `session_storage.load_character_for_session` (через `character_storage._try_load_character_file`) и `current_node_id` → продолжение через `GameEngine`.

**Сценарий «Создать персонажа»:** сложность → имя → раса → подраса → характеристики → предыстория → языки → класс → подкласс → черты (если нужны) → владения → навыки → (компетентность?) → **снаряжение** → сохранение в `saves/characters/{save_slug}.json`.

- Оркестрация: `ui/menus/_creation_steps.py` (`show_create_character_flow`), `ui/menus/_creation_handlers.py`, `ui/menus/stats/stats_flow.py`
- Снаряжение: `ui/menus/equipment.py` → `core/starting_equipment.py`; предыстория — `core/backgrounds.get_background_equipment_items`; merge и `equip_defaults` — `core/character_build.build_new_character` / `character_storage.persist_character`, `core/inventory.py`
- Сохранение: `_CreationState.to_character()` → `persist_character()` (без kwargs-bridge)
- Генераторы: `core/stats.py`, `core/races.py`
- Броски 4d6: `core/dice.py` (`roll_ability_score`)

Подробная спецификация UX генерации характеристик: [MUD_PRD.md §3.4.6](MUD_PRD.md#346-генерация-характеристик-реализовано).

## Режим сложности игры

`Character.difficulty` задаётся в flow «Создать персонажа» и используется в «Новая игра»:

```
select_difficulty() → show_stats_generation_flow() → adventure_allows_difficulty()
                    → set_mod_gating_difficulty(character.difficulty) → load_catalog / overlay
                    → run_scenario_with_engine() (GameEngine)
```

| Режим | Реализовано сегодня | Запланировано |
|-------|---------------------|---------------|
| `normal` | 3 метода характеристик, переквалификация; gating модов | Полная механика engine (бой, ресурсы) |
| `hardcore` | Авто-4d6×6; фильтр приключений; gating модов (`requires_game_difficulty`) | Полная механика D&D 5e без упрощений |
| `easy` | Старт 3 ур., обязательный подкласс; характеристики как Normal | Упрощённая механика engine / обучение |

Фильтрация приключений: `core/difficulty.py` (`adventure_unavailable_reason`) + `_select_adventure()` в `ui/menus/new_game.py`. Каталог `adventures.yaml` задаёт `min_level`, `allowed_game_difficulties`, `hardcore_only`; недоступные приключения — серым списком с причиной.  
Спецификация: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

**Настройки:** только `language` в `settings.json`; режим сложности — в `Character.difficulty`. Имена рас и классов в YAML — bilingual `{ ru, en }`, резолв через `resolve_localized_text()` и параметр `language` в loaders.

## Связанные документы

- [API Reference](API.md)
- [Development Guide](DEVELOPMENT.md)
- [MUD_PRD.md](MUD_PRD.md)
