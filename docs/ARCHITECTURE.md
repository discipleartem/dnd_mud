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
| `ui/menus/character_flow.py` | Flow «Создать персонажа» |
| `ui/menus/stats_flow.py` | Генерация характеристик |
| `ui/menus/settings.py` | Настройки, языки, выбор сложности |
| `ui/menus/_common.py`, `_display.py`, `_deps.py` | Общие хелперы, отображение, зависимости от core |
| `ui/input_handler.py` | Валидация ввода, UTF-8 для stdin/stdout |

UI не читает файлы данных напрямую — только через `core/`.

### 2. Core Layer (`core/`)

| Модуль | Назначение |
|--------|-----------|
| `core/models.py` | `Character`, `Adventure` (dataclass) |
| `core/character.py` | Фасад: re-export публичного API персонажей |
| `core/character_storage.py` | CRUD персонажей (JSON в `saves/`) |
| `core/races.py` | Справочник рас, расовые бонусы |
| `core/classes.py` | Справочник классов, hit dice |
| `core/stats.py` | Генерация и валидация характеристик |
| `core/io.py` | Общие `load_yaml()` / `load_json()` |
| `core/adventure.py` | `load_adventures()` |
| `core/difficulty.py` | `adventure_allows_difficulty()` — фильтр приключений по режиму |
| `core/dice.py` | `roll()`, `roll_ability_score()`, `ability_modifier()` |
| `core/localization.py` | `load_strings()`, `get_string()` |
| `core/settings.py` | Настройки в `database/core/settings.json` |

### 3. Data Layer (`database/`, `saves/`)

| Путь | Назначение | Формат | Модуль |
|------|-----------|--------|--------|
| `database/races/races.yaml` | Расы | YAML | `races.py` |
| `database/classes/classes.yaml` | Классы | YAML | `classes.py` |
| `database/content/adventures.yaml` | Каталог приключений | YAML | `adventure.py` |
| `database/core/settings.json` | Настройки | JSON | `settings.py` |
| `saves/characters/*.json` | Персонажи (по одному файлу) | JSON | `character_storage.py` |
| `database/strings/*.yaml` | Локализация | YAML | `localization.py` |
| `database/_future/` | Справочники Phase 2 (не загружаются) | YAML | — |

### 4. Resources (`adventures/`, `mods/`)

| Путь | Назначение |
|------|-----------|
| `adventures/*.yaml` | Сценарии (заглушки) |
| `mods/_examples/` | Пример формата мода (runtime не подключён) |

## Поток данных

```
main.py → ui/menus/ → core/character.py (фасад) → character_storage, races, classes, stats
                    → core/settings.py → database/core/settings.json
                    → core/adventure.py → database/content/adventures.yaml
                    → core/localization.py → database/strings/*.yaml
```

**Сценарий «Новая игра»:** персонаж (`Character`, режим из `Character.difficulty`) → приключение (с фильтром по режиму) → сообщение о запуске (без game engine).

**Сценарий «Создать персонажа»:** сложность → имя → раса → подраса → генерация характеристик (в т.ч. выборные бонусы, напр. variant human) → класс → сохранение в `saves/characters/{save_slug}.json`.

- Оркестрация: `ui/menus/character_flow.py`, `ui/menus/stats_flow.py`
- Генераторы: `core/stats.py`, `core/races.py` (через фасад `core/character.py`)
- Броски 4d6: `core/dice.py` (`roll_ability_score`)

Подробная спецификация UX генерации характеристик: [MUD_PRD.md §3.4.5](MUD_PRD.md#345-генерация-характеристик-реализовано).

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

Фильтрация приключений: `core/difficulty.py` + `_select_adventure()` в `ui/menus/new_game.py`. В `adventures.yaml` ограничения (`allowed_game_difficulties`, `hardcore_only`) пока не заданы — все приключения доступны в обоих режимах.  
Спецификация: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

**Настройки:** только `language` в `settings.json`; режим сложности — в `Character.difficulty`. Меню «Настройки» — заглушка (только «Назад»).

## Связанные документы

- [API Reference](API.md)
- [Development Guide](DEVELOPMENT.md)
- [MUD_PRD.md](MUD_PRD.md)
