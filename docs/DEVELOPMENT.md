# Development Guide — dnd_mud

## Быстрый старт

### Предварительные требования

- Python 3.12+
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
make test
pytest -v
pytest --cov=.
```

## Структура проекта

```
dnd_mud/
├── main.py                  # Точка входа
├── pyproject.toml           # Конфигурация проекта
├── README.md
├── core/                    # Игровое ядро
│   ├── models.py            # Dataclass: Character, Adventure
│   ├── character.py         # CRUD персонажей, генерация характеристик
│   ├── adventure.py         # Загрузка приключений из YAML
│   ├── difficulty.py        # Фильтр приключений по режиму сложности
│   ├── dice.py              # Броски кубиков
│   ├── localization.py      # Локализация (YAML-словари)
│   └── settings.py          # Настройки пользователя (JSON)
├── ui/                      # Пользовательский интерфейс
│   ├── __init__.py
│   ├── menus.py             # Меню (главное, настройки)
│   └── input_handler.py     # Валидация ввода (числа, строки, выбор)
├── database/                # YAML-справочники D&D 5e
│   ├── races/
│   │   └── races.yaml       # Расы и подрасы
│   ├── classes/
│   │   └── classes.yaml     # Классы персонажей
│   ├── content/adventures.yaml
│   ├── core/settings.json.example
│   ├── _future/               # Справочники Phase 2
│   └── strings/
│       ├── ru.yaml
│       └── en.yaml
├── saves/                   # Пользовательские данные (gitignored)
│   └── characters/          # Сохранённые персонажи (по одному JSON на персонажа)
├── adventures/      # Сценарии приключений (заглушки)
│   ├── tutorial.yaml
│   └── lost_mine.yaml
├── mods/_examples/example_mod.yaml
├── tests/
│   ├── test_adventure.py
│   ├── test_character.py
│   ├── test_difficulty.py
│   ├── test_dice.py
│   ├── test_input_handler.py
│   ├── test_localization.py
│   ├── test_main.py
│   ├── test_menus_character.py
│   ├── test_menus_stats.py
│   ├── test_models.py
│   └── test_settings.py     # 54 теста всего
└── docs/                    # Документация
    ├── MUD_PRD.md
    ├── ARCHITECTURE.md
    ├── API.md
    ├── DEVELOPMENT.md
    └── CHANGELOG.md
```

## Линтинг и форматирование

```bash
make check   # lint + black --check + mypy
```

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

Покрытие (54 теста в 11 файлах):
- `test_adventure.py` — загрузка приключений, поля `hardcore_only`
- `test_character.py` — save/load, генерация stats, variant human, slug
- `test_difficulty.py` — `adventure_allows_difficulty()`
- `test_dice.py` — `roll`, `roll_ability_score`, `ability_modifier`
- `test_input_handler.py` — валидация int/str
- `test_localization.py` — ключи en/ru, имена характеристик
- `test_main.py` — импорт `main`, VERSION
- `test_menus_character.py` — подрасы, new game, фильтр приключений
- `test_menus_stats.py` — генерация характеристик (standard array, point-buy, 4d6, HardCore)
- `test_models.py` — сериализация Character/Adventure
- `test_settings.py` — save/load JSON, `schema_version`

Запуск конкретного тестового файла:

```bash
pytest tests/test_menus_character.py -v
```

## Git Workflow

Git workflow (dev/main, squash, автокоммит, push/PR по запросу): [`~/.cursor/rules/01-operations.mdc`](~/.cursor/rules/01-operations.mdc). Для агентов dnd_mud: [`.cursor/rules/dnd-mud-git.mdc`](../.cursor/rules/dnd-mud-git.mdc), [`.cursor/rules/dnd-mud-verify.mdc`](../.cursor/rules/dnd-mud-verify.mdc).

Полный индекс правил агентов: [`AGENTS.md`](../AGENTS.md).

### Пример

```bash
git fetch origin && git checkout dev && git pull origin dev
git checkout -b feat/add-combat-system

# ... работа, коммиты по подзадачам ...
git commit -m "feat: add dice roll helper"

# push/PR — когда попросят:
git push -u origin HEAD && gh pr create --base dev --title "feat: add basic combat system"
```

## Создание мода

Моды — это YAML-файлы в папке `mods/`. Пример:

```yaml
# mods/my_mod.yaml
name: "Новая раса - Драконорожденный"
version: "1.0"
type: "addon"   # addon — добавляет новые данные, mod — изменяет
description: "Добавляет расу Dragonborn"
files:
  - target: "database/races/races.yaml"
    action: "append"   # append, replace, delete
    data:
      - id: dragonborn
        name:
          ru: "Драконорожденный"
          en: "Dragonborn"
        ability_bonuses:
          str: 2
          cha: 1
```

**Типы модов:**
- `addon` — добавляет новые расы, классы, приключения
- `mod` — изменяет существующую логику

**Действия (action):**
- `append` — добавляет данные к существующим
- `replace` — заменяет существующие данные
- `delete` — удаляет данные

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
2. Добавить запись по образцу существующих
3. Перезапустить игру

```yaml
# races.yaml
races:
  new_race:
    name: "Новая раса"
    description: "..."
    ability_bonuses:
      str: 2
      dex: 1
```

## Текущее состояние разработки

### Реализовано (core)
- ✅ `core/models.py` — типизированные dataclass: Character, Adventure
- ✅ `core/character.py` — создание, сохранение/загрузка персонажей
- ✅ `core/dice.py` — `roll`, `roll_ability_score`, `ability_modifier`
- ✅ `core/localization.py` — YAML-словари с fallback на английский
- ✅ `core/settings.py` — настройки пользователя (язык)
- ✅ `core/adventure.py` — загрузка приключений из YAML
- ✅ `core/difficulty.py` — `adventure_allows_difficulty()`; UI-фильтр в `_select_adventure()`

### Реализовано (ui)
- ✅ `ui/input_handler.py` — валидация ввода (int, str)
- ✅ `ui/menus.py` — главное меню (5 пунктов + Выход), настройки, languages
- ✅ Flow «Новая игра» (персонаж → приключение с фильтром по режиму)
- ✅ Flow «Создать персонажа» (сложность → имя → раса → подраса → генерация характеристик → класс)
- ✅ Flow «Загрузить игру» — заглушка (`errors.load_not_implemented`)

### Тестирование
- ✅ 54 теста в 11 файлах (см. выше)
- ⏳ Backlog (добавляются по необходимости, см. [философию](#философия) выше):
  - E2E smoke через `python main.py` (ручная проверка меню)

### Настройки: difficulty

Спецификация режимов: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

| ID | UI (ru) | Статус |
|----|---------|--------|
| `normal` | Нормальная | Реализовано в UI |
| `hardcore` | HardCore | Реализовано в UI |
| `easy` | Лёгкая | Зарезервировано, не в UI |

- `difficulty` выбирается в flow «Создать персонажа» (`select_difficulty`); сохраняется в `Character.difficulty` и используется в «Новая игра»
- Поле `difficulty` в `adventures.yaml` — **уровень контента**, не режим игрока (не путать с `Character.difficulty`)

### Генерация характеристик

Спецификация UX (методы, HardCore, расовые бонусы, переквалификация): [MUD_PRD.md §3.4.5](MUD_PRD.md#345-генерация-характеристик-реализовано).  
API: `core/character.py`, UI: `show_stats_generation_flow` в `ui/menus.py`.

### База данных
- ✅ Справочники: `races/races.yaml`, `classes/classes.yaml`, `content/adventures.yaml`
- ✅ JSON: `database/core/settings.json`, `saves/characters/*.json` (с `schema_version: 1`)
- ✅ Локализация: `strings/ru.yaml`, `strings/en.yaml`
- ⏳ Справочники Phase 2 в `database/_future/` — не загружаются runtime

### Не реализовано
- ❌ Режим сложности «Лёгкая» (`easy`) в UI
- ❌ Ограничения приключений в `adventures.yaml` (`allowed_game_difficulties`, `hardcore_only`); core/UI готовы
- ❌ Gating модов по режиму (`requires_game_difficulty` в метаданных мода)
- ❌ Параметризация game_engine по режиму сложности
- ❌ Полноценный цикл приключений в game_engine.py
- ❌ Боевая система
- ❌ Сохранение/загрузка состояния игры (flow «Загрузить игру»)
- ❌ Сценарии приключений (только заглушки в `adventures/`)
- ❌ Отдельные пункты меню «Модификации» / «Приключения» (приключения — внутри «Новая игра»)
- ❌ Обработка модов во время выполнения