# Development Guide — dnd_mud

## Быстрый старт

### Предварительные требования

- Python 3.12+
- Git

### Установка

```bash
# Клонировать репозиторий
git clone git@github.com:discipleartem/dnd_mud.git
cd dnd_mud

# Создать виртуальное окружение
python3.12 -m venv .venv
source .venv/bin/activate

# Установить зависимости
pip install -e .
pip install -e ".[dev]"  # + dev-зависимости (pytest, ruff, black, mypy)
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
source .venv/bin/activate
pytest                  # Все тесты
pytest -v               # Подробный вывод
pytest --cov=.          # С coverage
```

## Структура проекта

```
dnd_mud/
├── main.py                  # Точка входа
├── pyproject.toml           # Конфигурация проекта
├── README.md
├── core/                    # Игровое ядро
│   ├── __init__.py
│   ├── character.py         # Модель персонажа (dataclass)
│   ├── adventure.py         # Загрузка приключений из YAML
│   ├── dice.py              # Броски кубиков (d20, ndm)
│   ├── game_engine.py       # Игровой движок (базовая структура)
│   ├── localization.py      # Локализация (YAML-словари)
│   ├── mod_loader.py        # Моды (сканирование, включение/выключение)
│   └── settings.py          # Настройки пользователя
├── ui/                      # Пользовательский интерфейс
│   ├── __init__.py
│   ├── menus.py             # Меню (главное, настройки)
│   └── input_handler.py     # Валидация ввода (числа, строки, выбор)
├── database/                # YAML-данные D&D 5e
│   ├── races.yaml           # Расы и подрасы
│   ├── classes.yaml         # Классы персонажей
│   ├── characters.yaml      # Сохранённые персонажи
│   ├── adventures.yaml      # Список приключений
│   ├── settings.yaml        # Настройки пользователя
│   ├── mods_state.yaml      # Состояние модов
│   ├── abilities.yaml       # Характеристики и навыки (заготовка)
│   ├── armor.yaml           # Доспехи (заготовка)
│   ├── backgrounds.yaml     # Предыстории (заготовка)
│   ├── constants.yaml       # Константы (заготовка)
│   ├── equipment.yaml       # Снаряжение (заготовка)
│   ├── feats.yaml           # Фиты (заготовка)
│   ├── features.yaml        # Особенности (заготовка)
│   ├── languages.yaml       # Языки (заготовка)
│   ├── sizes.yaml           # Размеры (заготовка)
│   ├── skills.yaml          # Навыки (заготовка)
│   ├── tools.yaml           # Инструменты (заготовка)
│   ├── weapon.yaml          # Оружие (заготовка)
│   └── strings/             # Локализация
│       ├── ru.yaml
│       └── en.yaml
├── adventures_scripts/      # Сценарии приключений (заглушки)
│   ├── tutorial.yaml
│   └── lost_mine.yaml
├── mods/                    # Пользовательские моды
│   └── example_mod.yaml
├── tests/                   # Тесты
│   └── test_integration_menus.py  # 3 интеграционных теста
└── docs/                    # Документация
    ├── MUD_PRD.md
    ├── ARCHITECTURE.md
    ├── API.md
    ├── DEVELOPMENT.md
    └── CHANGELOG.md
```

## Линтинг и форматирование

```bash
source .venv/bin/activate

# Линтер
ruff check .

# Автофикс
ruff check --fix .

# Форматирование
black .

# Проверка типов
mypy .
```

## Тестирование

Проект использует `pytest`. Тесты находятся в `tests/`.

```python
# tests/test_integration_menus.py
"""Интеграционные тесты (3 теста): локализация, настройки, импорт main."""
```

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
  - target: "database/races.yaml"
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
loc('menu.my_new_item')
```

Для форматирования с параметрами:

```yaml
welcome:
  version: "Версия: {version}"
```

```python
loc('welcome.version', version='0.1.0')
```

## Добавление новой расы/класса

1. Открыть `database/races.yaml` или `database/classes.yaml`
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
- ✅ `core/character.py` — полная модель персонажа с dataclass
- ✅ `core/dice.py` — все броски кубиков (d20, ndm, криты, adv/disadv)
- ✅ `core/localization.py` — YAML-словари с fallback на английский
- ✅ `core/settings.py` — настройки пользователя (язык, hardcore)
- ✅ `core/mod_loader.py` — сканирование и переключение модов
- ✅ `core/adventure.py` — загрузка приключений из YAML
- ✅ `core/game_engine.py` — базовая структура игрового движка

### Реализовано (ui)
- ✅ `ui/input_handler.py` — валидация ввода (int, str, выбор из списка)
- ✅ `ui/menus.py` — главное меню (2 пункта) и экран настроек

### Тестирование
- ❌ Нет тестов для character.py, dice.py, localization.py, mod_loader.py, settings.py, adventure.py

### База данных
- ✅ Основные файлы: races.yaml, classes.yaml, characters.yaml, adventures.yaml
- ✅ Локализация: ru.yaml, en.yaml
- ⏳ Заготовки: abilities.yaml, armor.yaml, backgrounds.yaml, constants.yaml, equipment.yaml, feats.yaml, features.yaml, languages.yaml, sizes.yaml, skills.yaml, tools.yaml, weapon.yaml — заполнены данными, но не используются в коде

### Не реализовано
- ❌ Полноценный цикл приключений в game_engine.py
- ❌ Боевая система
- ❌ Сохранение/загрузка состояния игры
- ❌ Сценарии приключений (только заглушки)
- ❌ Меню создания персонажа в ui/menus.py
- ❌ Меню Languages в ui/menus.py
- ❌ Меню Модификаций в ui/menus.py
- ❌ Меню Приключений в ui/menus.py
- ❌ Обработка модов во время выполнения