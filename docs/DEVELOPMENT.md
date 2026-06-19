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
│   └── characters.json      # Сохранённые персонажи
├── adventures_scripts/      # Сценарии приключений (заглушки)
│   ├── tutorial.yaml
│   └── lost_mine.yaml
├── mods/_examples/example_mod.yaml
├── tests/
│   ├── test_character.py
│   ├── test_settings.py
│   └── test_integration_menus.py  # 12 тестов всего
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

```python
# tests/test_integration_menus.py
"""Интеграционные тесты UI; unit-тесты — test_character.py, test_settings.py."""
```

Покрытие:
- `test_localization` — ключи en/ru, имена характеристик
- `test_settings` — save/load JSON, `schema_version`
- `test_main_imports` — импорт `main`, VERSION
- `test_new_game_back_returns_one_step` — навигация «Назад»
- `test_base_race_without_subraces_has_back_option` — расы без подрас
- `test_human_has_base_and_variant_choices` — human / variant_human
- `test_variant_human_does_not_inherit_base_bonuses` — в `test_character.py`

См. также `tests/test_character.py` (save/load Character, stats) и `tests/test_settings.py`.

Запуск конкретного тестового файла:

```bash
pytest tests/test_integration_menus.py -v
```

## Git Workflow

### Правила

1. **Ветки:** `feature/*`, `fix/*`, `refactor/*`, `chore/*`
2. **Коммиты:** Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`)
3. **Коммиты в `main` запрещены** — всегда через PR
4. **Никакого squash** без явного указания
5. **Каждый коммит должен проходить тесты**

### Пример

```bash
git checkout -b feat/add-combat-system
# ... работа ...
git commit -m "feat: add basic combat system with dice rolls"
git push origin feat/add-combat-system
# PR в main или dev
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
- ✅ `core/dice.py` — все броски кубиков (d20, ndm, криты, adv/disadv)
- ✅ `core/localization.py` — YAML-словари с fallback на английский
- ✅ `core/settings.py` — настройки пользователя (язык, hardcore)
- ✅ `core/mod_loader.py` — сканирование и переключение модов
- ✅ `core/adventure.py` — загрузка приключений из YAML
- ✅ `core/game_engine.py` — игровой цикл, ability checks (типизирован)

### Реализовано (ui)
- ✅ `ui/input_handler.py` — валидация ввода (int, str, выбор из списка)
- ✅ `ui/menus.py` — главное меню (5 пунктов + Выход), настройки, languages
- ✅ Flow «Новая игра» (сложность → персонаж → приключение)
- ✅ Flow «Создать персонажа» (имя → раса → подраса → генерация характеристик → класс)
- ✅ Flow «Загрузить игру» — заглушка (`errors.load_not_implemented`)

### Тестирование
- ✅ 9 интеграционных тестов (см. выше)
- ✅ Unit-тест `generate_stats_random` (регрессия API)
- ❌ Нет UI-тестов экрана генерации характеристик
- ❌ Нет unit-тестов для dice.py, mod_loader.py, adventure.py

### Настройки: difficulty

Спецификация режимов: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

| ID | UI (ru) | Статус |
|----|---------|--------|
| `normal` | Нормальная | Реализовано в UI |
| `hardcore` | HardCore | Реализовано в UI |
| `easy` | Лёгкая | Зарезервировано, не в UI |

- `difficulty` выбирается в flow «Новая игра» / «Создать персонажа» (`select_difficulty`); сохраняется в `Character.difficulty`
- `settings.json` → `difficulty` — предвыбор в меню; меню «Настройки» **отображает**, но не переключает
- Поле `difficulty` в `adventures.yaml` — **уровень контента**, не режим игрока (не путать с `Character.difficulty`)
- Миграция legacy `hardcore: true` → `difficulty: "hardcore"` (`core/settings.py`)

### Генерация характеристик

Спецификация UX (методы, HardCore, расовые бонусы, переквалификация): [MUD_PRD.md §3.4.5](MUD_PRD.md#345-генерация-характеристик-реализовано).  
API: `core/character.py`, UI: `show_stats_generation_flow` в `ui/menus.py`.

### База данных
- ✅ Справочники: `races/races.yaml`, `classes/classes.yaml`, `content/adventures.yaml`
- ✅ JSON: `database/core/settings.json`, `saves/characters.json` (с `schema_version: 1`)
- ✅ Локализация: `strings/ru.yaml`, `strings/en.yaml`
- ⏳ Заготовки в `core/`, `equipment/`, `progression/` — заполнены, но не используются в коде

### Не реализовано
- ❌ Режим сложности «Лёгкая» (`easy`) в UI
- ❌ Фильтрация приключений по режиму HardCore (`allowed_game_difficulties` в YAML)
- ❌ Gating модов по режиму (`requires_game_difficulty` в метаданных мода)
- ❌ Параметризация game_engine по режиму сложности
- ❌ Полноценный цикл приключений в game_engine.py
- ❌ Боевая система
- ❌ Сохранение/загрузка состояния игры (flow «Загрузить игру»)
- ❌ Сценарии приключений (только заглушки в `adventures_scripts/`)
- ❌ Отдельные пункты меню «Модификации» / «Приключения» (приключения — внутри «Новая игра»)
- ❌ Обработка модов во время выполнения