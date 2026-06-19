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
| `ui/menus.py` | Отрисовка всех экранов меню |
| `ui/input_handler.py` | Валидация ввода, UTF-8 для stdin/stdout |

UI не читает файлы данных напрямую — только через `core/`.

### 2. Core Layer (`core/`)

| Модуль | Назначение |
|--------|-----------|
| `core/models.py` | `Character`, `Adventure` (dataclass) |
| `core/character.py` | CRUD персонажей, генерация характеристик, справочники рас/классов |
| `core/adventure.py` | `load_adventures()` |
| `core/dice.py` | `roll()`, `roll_ability_score()`, `ability_modifier()` |
| `core/localization.py` | `load_strings()`, `get_string()` |
| `core/settings.py` | Настройки в `database/core/settings.json` |

### 3. Data Layer (`database/`, `saves/`)

| Путь | Назначение | Формат | Модуль |
|------|-----------|--------|--------|
| `database/races/races.yaml` | Расы | YAML | `character.py` |
| `database/classes/classes.yaml` | Классы | YAML | `character.py` |
| `database/content/adventures.yaml` | Каталог приключений | YAML | `adventure.py` |
| `database/core/settings.json` | Настройки | JSON | `settings.py` |
| `saves/characters.json` | Персонажи | JSON | `character.py` |
| `database/strings/*.yaml` | Локализация | YAML | `localization.py` |
| `database/_future/` | Справочники Phase 2 (не загружаются) | YAML | — |

### 4. Resources (`adventures_scripts/`, `mods/`)

| Путь | Назначение |
|------|-----------|
| `adventures_scripts/*.yaml` | Сценарии (заглушки) |
| `mods/_examples/` | Пример формата мода (runtime не подключён) |

## Поток данных

```
main.py → ui/menus.py → core/character.py → saves/characters.json
                      → core/settings.py → database/core/settings.json
                      → core/adventure.py → database/content/adventures.yaml
                      → core/localization.py → database/strings/*.yaml
```

**Сценарий «Новая игра»:** сложность → персонаж (`Character`) → приключение → сообщение о запуске (без game engine).

**Сценарий «Создать персонажа»:** сложность → имя → раса → подраса → генерация характеристик → класс → сохранение в `saves/characters.json`.

- Оркестрация: `ui/menus.py` (`show_create_character_flow`, `show_stats_generation_flow`)
- Генераторы: `core/character.py` (`generate_stats_*`, `get_race_bonuses`)
- Броски 4d6: `core/dice.py` (`roll_ability_score`)

Подробная спецификация UX генерации характеристик: [MUD_PRD.md §3.4.5](MUD_PRD.md#345-генерация-характеристик-реализовано).

## Режим сложности игры

`Character.difficulty` проходит через flows «Новая игра» и «Создать персонажа»:

```
select_difficulty() → show_stats_generation_flow() → [будущее] фильтр приключений → [будущее] правила game_engine
```

| Режим | Реализовано сегодня | Запланировано |
|-------|---------------------|---------------|
| `normal` | 3 метода характеристик, переквалификация | Базовая механика engine |
| `hardcore` | Авто-4d6×6, без переквалификации | Gating приключений/модов, полная механика D&D 5e |
| `easy` | — | Упрощённая механика / обучение |

HardCore — точка расширения для `core/adventure.py`, `core/mod_loader.py`, `core/game_engine.py`.  
Спецификация: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

**Настройки:** `language`, `difficulty` в `settings.json`; сложность персонажа — в `Character.difficulty`. Меню «Настройки» только отображает `difficulty` по умолчанию.

## Связанные документы

- [API Reference](API.md)
- [Development Guide](DEVELOPMENT.md)
- [MUD_PRD.md](MUD_PRD.md)
