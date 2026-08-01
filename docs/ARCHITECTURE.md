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
| `ui/menus/` | Пакет экранов меню (flows по подпакетам) |
| `ui/menus/hub/` | Главное меню, новая/загрузка игры, персонажи, моды, настройки |
| `ui/menus/hub/main_menu.py` | Приветствие, главное меню |
| `ui/menus/hub/load_game.py` | Flow «Загрузить игру» (сессии в `saves/sessions/`) |
| `ui/menus/hub/mods_menu.py` | Включение/выключение модов |
| `ui/menus/hub/new_game.py` | Flow «Новая игра» |
| `ui/menus/hub/characters_menu.py` | Список персонажей; кэш `LoadCharactersResult`, reload после create/delete |
| `ui/menus/hub/settings.py` | Настройки, языки, выбор сложности |
| `ui/menus/creation/` | Flow «Создать персонажа»: steps, handlers, navigation, state, finalize |
| `ui/menus/creation/selectors.py` | Общие селекторы расы, класса, подкласса |
| `ui/menus/creation/corrupt_saves.py` | Предупреждение о битых JSON в `saves/characters/` |
| `ui/menus/creation/languages.py` | Выбор языков расы/подрасы |
| `ui/menus/creation/backgrounds.py` | Выбор предыстории |
| `ui/menus/creation/skills.py` | Выбор навыков класса |
| `ui/menus/creation/equipment.py` | Стартовое снаряжение |
| `ui/menus/creation/proficiencies.py` | Выбор владений |
| `ui/menus/creation/expertise.py` | Выбор компетентности |
| `ui/menus/creation/subclass_picks.py` | Владения/навыки/компетентность подкласса |
| `ui/menus/progression/` | Левелап, ASI, class features, subclass trainer |
| `ui/menus/scenario/flow.py` | Runner YAML-сценариев через `GameEngine` |
| `ui/menus/stats/` | Пакет генерации характеристик |
| `ui/menus/stats/stats_flow.py` | Оркестратор flow stats |
| `ui/menus/stats/stats_shared.py` | Пул, confirm, общие шаги |
| `ui/menus/stats/stats_methods.py` | Standard array, point-buy, random |
| `ui/menus/stats/stats_choice_bonuses.py` | Выборные расовые бонусы |
| `ui/menus/feats/` | Выбор черт при создании и левелапе (публичный API в `__init__.py`) |
| `ui/menus/display/` | Отображение: grants, раса/фон, stats, карточка, экипировка, класс |
| `ui/menus/console.py` | Публичный UI toolkit: `print_screen_header`, `read_numbered_choice`, … |
| `ui/terminal_wrap.py` | Перенос текста под ширину терминала |
| `ui/input_handler.py` | Валидация ввода, UTF-8 для stdin/stdout |

UI не читает файлы данных напрямую — только через `core/`.

**Импорты UI → core:** прямые leaf-imports из `core.<pkg>.<module>` (и `ui.input_handler`). Пакетные `__init__.py` в `core/` — только навигация, без фасадов. Monkeypatch в тестах — по точке использования в UI-модуле (`conftest.patch_int_input` и т.п.).

### 2. Core Layer (`core/`)

Корневые модули: `core/types.py`, `core/constants.py`. Остальное — пакеты с leaf-imports (без package facades).

| Пакет / модуль | Назначение |
|----------------|-----------|
| `core/types.py` | Типы домена: `StatMap`, `CharacterClass`, `CharacterBuildParams`, … |
| `core/constants.py` | PB, DC; `MAX_CHARACTER_LEVEL`, `clamp_level`; ability modifier |
| **`core/platform/`** | I/O, каталоги, локализация, настройки, моды |
| `platform/io.py` | `load_file()`, `load_yaml()` / `load_json()` (`strict`), `save_json()` / `merge_unique()` |
| `platform/catalog_loader.py` | `load_catalog()`, `load_catalog_items()`, `reload_catalogs()` |
| `platform/catalog_session.py` | `CatalogSession` — gating модов (`set_mod_gating_difficulty` / `get_mod_gating_difficulty`) и сброс кэшей; `get_catalog_session()` |
| `platform/localization.py` | `load_strings()` (кэш), `get_string()` |
| `platform/settings.py` | Настройки в `database/core/settings.json` |
| `platform/mod_loader.py` | Deep-merge overlay модов; `requires`/`conflicts`; `delete`/`replace_entity`; difficulty только аргументом |
| **`core/catalogs/`** | YAML-справочники PHB |
| `catalogs/abilities.py` | Характеристики и навыки (метаданные) из YAML |
| `catalogs/races.py` | Расы, `collect_race_grants`, расовые бонусы |
| `catalogs/classes.py` | Классы, `get_class_dict`, hit dice, подклассы |
| `catalogs/skills.py` | Навыки при создании; `PHB_SKILL_IDS` |
| `catalogs/skill_ids.py` | Идентификаторы навыков |
| `catalogs/languages.py` | Каталог языков PHB, пулы выбора |
| `catalogs/backgrounds.py` | Предыстории PHB |
| `catalogs/equipment.py` | Оружие, доспехи, инструменты из YAML |
| `catalogs/adventure.py` | `Adventure` + `load_adventures()` |
| **`core/grants/`** | Нормализация и разрешение grants |
| `grants/normalize.py` | Нормализация `grants[]`; proficiency-токены |
| `grants/format.py` | Чистое текстовое форматирование grants (без print); registry по типу |
| `grants/labels.py` | Ключи локализации для отображения grants |
| `grants/context.py` | `CreationContext`, `ResolvedGrants` |
| `grants/resolve.py` | Leaf: `resolve_grants_for_context` / `resolve_creation_grants` (без feats) |
| **`core/character/`** | Модель, сборка, хранение |
| `character/models.py` | `Character` (dataclass); JSON coerce helpers |
| `character/build.py` | `build_new_character(CharacterBuildParams)` — сборка без записи на диск |
| `character/finalize.py` | Merge языков черт + persist собранного персонажа |
| `character/migrate.py` | `CHARACTERS_SCHEMA_VERSION`, `migrate_character_data` |
| `character/storage.py` | CRUD; `make_save_slug`, `unique_save_slug`; JSON в `saves/` |
| `character/creation_draft.py` | Черновик создания (`saves/creation_draft.json`) |
| **`core/feats/`** | Черты (leaf: catalog, apply, text, requirements) |
| `feats/catalog.py` | YAML черт, чистое чтение grants |
| `feats/grant_merge.py` | Слияние черт с `ResolvedGrants` (над leaf resolve) |
| `feats/apply.py` | Применение эффектов черт |
| `feats/selection_side_effects.py` | Накопление weapon/skill/tool после выбора черты |
| `feats/text.py` / `requirement_text.py` | PHB-текст и описания требований |
| `feats/requirements.py` | Видимость / требования |
| **`core/progression/`** | XP, HP, ASI, class features, level-up |
| `progression/xp_levels.py` | Пороги XP |
| `progression/hp.py` | HP по уровню / режиму |
| `progression/asi.py` | ASI helpers |
| `progression/class_progression.py` | Подклассы, старт по difficulty, class features |
| `progression/subclass_proficiencies.py` | Apply владений подкласса / picked tools |
| `progression/level_up.py` | Разрешение pending level-ups |
| **`core/inventory/`** | Инвентарь, КД, стартовое снаряжение |
| `inventory/items.py` | Операции с инвентарём |
| `inventory/armor_class.py` | Расчёт КД |
| `inventory/background_equipment.py` | Снаряжение предыстории |
| `inventory/equipment_text.py` | UI-подсказки оружия/доспехов (свойства, кубы урона, КД в списках) |
| `inventory/equipped_display.py` | Данные экипировки для карточки (`get_equipped_display`) |
| `inventory/equip_defaults.py` | Авто-экипировка |
| `inventory/starting_equipment.py` | Стартовое снаряжение класса из YAML |
| **`core/mechanics/`** | Броски, проверки, владения, характеристики |
| `mechanics/dice.py` | `roll()`, `roll_ability_score()`, `ability_modifier()` |
| `mechanics/stats.py` | Генерация/валидация характеристик |
| `mechanics/checks.py` | `ability_check`, `skill_check`, спасброски |
| `mechanics/proficiencies.py` | Проверки владений (`has_*`) |
| `mechanics/proficiency_collect.py` | Сбор токенов владений из grants |
| `mechanics/expertise.py` | Компетентность (expertise) из class features |
| `mechanics/hp_bonus.py` | `HpBonusSource`, `get_racial_hp_bonus_sources` |
| **`core/engine/`** | Сценарии, сессии, сложность (+ `combat/`) |
| `engine/game_engine.py` | `GameEngine`, `GameSession` — state machine сценария |
| `engine/session_runner.py` | Persist сессии и UI-action wiring без UI I/O (storage I/O допустим) |
| `engine/session_storage.py` | Снимки сессий приключений (`saves/sessions/`) |
| `engine/scenario_rooms.py` | `exits` в узлах YAML-сценария |
| `engine/scenario_actions.py` | Чистая логика action-узлов (без UI) |
| `engine/engine_rules.py` | Преимущество/помеха проверок по `GameDifficulty` |
| `engine/difficulty.py` | `adventure_allows_difficulty()` |
| `engine/combat/` | Phase 2: `roll_initiative`, `attack_roll` (`rolls`) |

### 3. Data Layer (`database/`, `saves/`)

Канон формата YAML: [`DATA_SCHEMA.md`](DATA_SCHEMA.md) (grants, subraces, mod overlay). Валидация: `database/schema/v1/*.json`, pytest `tests/data/test_data_schema.py`, CLI `scripts/validate_data.py`.

| Путь | Назначение | Формат | Модуль |
|------|-----------|--------|--------|
| `database/schema/v1/` | JSON Schema v1 (grants, backgrounds, adventures, progression, scenario_node) | JSON | `tests/data/test_data_schema.py` |
| `database/races/races.yaml` | Расы | YAML | `catalogs/races.py` |
| `database/classes/classes.yaml` | Классы | YAML | `catalogs/classes.py` |
| `database/backgrounds/backgrounds.yaml` | Предыстории PHB | YAML | `catalogs/backgrounds.py` |
| `database/content/adventures.yaml` | Каталог приключений | YAML | `catalogs/adventure.py` |
| `database/equipment/` | Оружие, доспехи, инструменты, прочее снаряжение | YAML | `catalogs/equipment.py` |
| `database/progression/feats.yaml` | Черты | YAML | `feats/catalog.py` |
| `database/core/abilities.yaml` | Характеристики и привязка навыков | YAML | `catalogs/abilities.py` |
| `database/core/skills.yaml` | Метаданные навыков | YAML | `catalogs/skills.py` |
| `database/core/constants.yaml` | PB, DC, cover, sizes, ability modifiers | YAML | `constants.py` |
| `database/core/languages.yaml` | Языки PHB | YAML | `catalogs/languages.py` |
| `database/core/settings.json` | Настройки | JSON | `platform/settings.py` |
| `database/core/mods_state.json` | Включённые моды | JSON | `platform/mod_loader.py` |
| `database/strings/*.yaml` | Локализация | YAML | `platform/localization.py` |
| `saves/characters/*.json` | Персонажи (по одному файлу) | JSON | `character/storage.py` |
| `saves/creation_draft.json` | Черновик незавершённого создания | JSON | `character/creation_draft.py` |
| `saves/sessions/*.json` | Сессии приключений (узел сценария, флаги) | JSON | `engine/session_storage.py` |

### 4. Resources (`adventures/`, `mods/`)

| Путь | Назначение |
|------|-----------|
| `adventures/*.yaml` | Сценарии приключений (`tutorial`, `lost_mine`) — runner в `ui/menus/scenario/flow.py` |
| `mods/dragonborn_pack/` | Пример mod overlay (deep-merge) | YAML | `platform/mod_loader.py` |

### 5. Tests (`tests/`)

| Путь | Назначение |
|------|-----------|
| `tests/conftest.py` | Общие фикстуры и patch-хелперы |
| `tests/core/` | Unit-тесты ядра (зеркалит пакеты `core/`) |
| `tests/ui/` | UI smoke (меню) |
| `tests/data/` | Схема YAML / data validation |
| `tests/creation_helpers.py` | Хелперы создания персонажа для тестов |

Число кейсов не фиксировать в docs — `pytest --collect-only -q`.

## Поток данных

```
main.py → ui/menus/ → core.<pkg>.<module> (прямые leaf-imports)
                    → core.catalogs.*, core.character.storage, …
                         → core.platform.mod_loader → database/*/*.yaml + mods/*/overlay.yaml
                         → core.grants.normalize (нормализация grants[])
                    → core.platform.settings → database/core/settings.json
                    → core.catalogs.adventure → database/content/adventures.yaml
                    → core.platform.localization → database/strings/*.yaml
```

**Сценарий «Новая игра»:** персонаж → приключение (фильтр по режиму) → `run_scenario()` / `run_scenario_with_engine()` в `ui/menus/scenario/flow.py` (автосохранение сессии, grant XP, subclass training, skill_check).

**Сценарий «Загрузить игру»:** список `saves/sessions/` → `session_storage.load_character_for_session` (через `character.storage.try_load_character_file`) и `current_node_id` → продолжение через `GameEngine`.

**Сценарий «Создать персонажа»:** сложность → имя → раса → подраса → характеристики → предыстория → языки → класс → подкласс → черты (если нужны) → владения → навыки → (компетентность?) → **снаряжение** → сохранение в `saves/characters/{save_slug}.json`.

- Оркестрация: `ui/menus/creation/steps.py` (`show_create_character_flow` / `show_continue_character_flow`), autosave в `saves/creation_draft.json`; `ui/menus/creation/handlers.py`, `ui/menus/stats/stats_flow.py`
- Ввод: `ui/input_handler.safe_input` глотает Ctrl+C; safety-net в `main()`
- Снаряжение: `ui/menus/creation/equipment.py` → `core.inventory.starting_equipment`; предыстория — `core.inventory.background_equipment.get_background_equipment_items`; merge и `equip_defaults` — `core.character.build.build_new_character` / `character.storage.persist_character`, `core.inventory.*`
- Сохранение: `_CreationState.to_character()` → `persist_character()` (без kwargs-bridge)
- Генераторы: `core.mechanics.stats`, `core.catalogs.races`
- Броски 4d6: `core.mechanics.dice` (`roll_ability_score`)

Подробная спецификация UX генерации характеристик: [MUD_PRD.md §3.4.6](MUD_PRD.md#346-генерация-характеристик-реализовано).

## Режим сложности игры

`Character.difficulty` задаётся в flow «Создать персонажа» и используется в «Новая игра»:

```
select_difficulty() → show_stats_generation_flow() → adventure_allows_difficulty()
                    → CatalogSession.set_difficulty(character.difficulty) → load_catalog / overlay
                    → run_scenario_with_engine() (GameEngine)
```

| Режим | Реализовано сегодня | Запланировано |
|-------|---------------------|---------------|
| `normal` | 3 метода характеристик, переквалификация; gating модов | Полная механика engine (бой, ресурсы) |
| `hardcore` | Авто-4d6×6; фильтр приключений; gating модов (`requires_game_difficulty`) | Полная механика D&D 5e без упрощений |
| `easy` | Старт 3 ур., обязательный подкласс; характеристики как Normal | Упрощённая механика engine / обучение |

Фильтрация приключений: `core.engine.difficulty` (`adventure_unavailable_reason`) + `_select_adventure()` в `ui/menus/hub/new_game.py`. Каталог `adventures.yaml` задаёт `min_level`, `allowed_game_difficulties`, `hardcore_only`; недоступные приключения — серым списком с причиной.  
Спецификация: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

**Настройки:** только `language` в `settings.json`; режим сложности — в `Character.difficulty`. Имена рас и классов в YAML — bilingual `{ ru, en }`, резолв через `resolve_localized_text()` и параметр `language` в loaders.

## Связанные документы

- [API Reference](API.md)
- [Development Guide](DEVELOPMENT.md)
- [MUD_PRD.md](MUD_PRD.md)
