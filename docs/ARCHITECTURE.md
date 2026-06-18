# Architecture — dnd_mud

## Общая архитектура

Проект построен по слоёной архитектуре (layered architecture):

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

Отвечает за взаимодействие с пользователем.

| Модуль | Назначение |
|--------|-----------|
| `ui/menus.py` | Отрисовка всех экранов меню (главное меню, настройки и т.д.) |
| `ui/input_handler.py` | Валидация пользовательского ввода (числа, строки, выбор из списка) |

**Принцип:** UI не содержит бизнес-логики. Все вызовы идут к core через функции.

### 2. Core Layer (`core/`)

Ядро игры. Не зависит от UI и БД.

| Модуль | Назначение |
|--------|-----------|
| `core/character.py` | Модель `Character` (dataclass), создание, сохранение/загрузка, расы, классы, характеристики |
| `core/adventure.py` | Загрузка приключений из YAML, отображаемые имена, сложность |
| `core/dice.py` | Броски кубиков (d20, ndm), преимущество/помеха, модификаторы |
| `core/game_engine.py` | Игровой движок, обработка команд, проверки характеристик (базовая структура) |
| `core/localization.py` | Загрузка YAML-словарей, переключение языка, fallback на английский |
| `core/mod_loader.py` | Сканирование папки `mods/`, включение/выключение модов |
| `core/settings.py` | Класс `Settings` — загрузка/сохранение настроек пользователя |

### 3. Data Layer (`database/`)

Хранилище данных в формате YAML.

| Файл | Назначение | Статус использования |
|------|-----------|---------------------|
| `database/races.yaml` | Расы, бонусы, подрасы | Используется `character.py` |
| `database/classes.yaml` | Классы, хиты, особенности, подклассы | Используется `character.py` |
| `database/characters.yaml` | Сохранённые персонажи | Используется `character.py` |
| `database/adventures.yaml` | Список приключений | Используется `adventure.py` |
| `database/settings.yaml` | Настройки пользователя (язык, hardcore) | Используется `settings.py` |
| `database/mods_state.yaml` | Состояние модов (вкл/выкл) | Используется `mod_loader.py` |
| `database/strings/ru.yaml` | Русская локализация | Используется `localization.py` |
| `database/strings/en.yaml` | Английская локализация (fallback) | Используется `localization.py` |
| `database/abilities.yaml` | Характеристики и привязанные навыки | Заготовка на будущее |
| `database/armor.yaml` | Доспехи и щиты | Заготовка на будущее |
| `database/backgrounds.yaml` | Предыстории персонажей | Заготовка на будущее |
| `database/constants.yaml` | Константы (модификаторы, DC, hit dice) | Заготовка на будущее |
| `database/equipment.yaml` | Снаряжение | Заготовка на будущее |
| `database/feats.yaml` | Фиты | Заготовка на будущее |
| `database/features.yaml` | Все особенности (фиты, классовые, расовые) | Заготовка на будущее |
| `database/languages.yaml` | Языки | Заготовка на будущее |
| `database/sizes.yaml` | Размеры существ | Заготовка на будущее |
| `database/skills.yaml` | Навыки | Заготовка на будущее |
| `database/tools.yaml` | Инструменты | Заготовка на будущее |
| `database/weapon.yaml` | Оружие | Заготовка на будущее |

### 4. Resources Layer (`adventures_scripts/`, `mods/`)

| Файл | Назначение |
|------|-----------|
| `adventures_scripts/tutorial.yaml` | Сценарий обучения (заглушка) |
| `adventures_scripts/lost_mine.yaml` | Сценарий «Затеряные рудники Фанделвера» (заглушка) |
| `mods/example_mod.yaml` | Пример мода (добавление расы Драконорожденный) |

## Поток данных (Data Flow)

```
Пользователь
    │
    ▼
main.py ──вызов──► ui/menus.py ──вызов──► core/character.py
    │                                              │
    │                                              ▼
    │                                         database/races.yaml
    │                                         database/classes.yaml
    │                                         database/characters.yaml
    │
    │──► core/settings.py ──► database/settings.yaml
    │
    │──► core/mod_loader.py ──► mods/*.yaml
    │                          database/mods_state.yaml
    │
    │──► core/adventure.py ──► database/adventures.yaml
    │                          adventures_scripts/*.yaml
    │
    ▼                       ▼
core/localization.py ◄──── database/strings/*.yaml
```

**Типичный сценарий «Новая игра» (планируемый):**

1. `main.py` → `show_main_menu()` → пользователь выбирает пункт
2. При выборе настроек → `show_settings()` → изменение `Settings` → сохранение в `database/settings.yaml`
3. При выходе → завершение программы

**Текущее состояние главного меню:**
- Пункт 1: Настройки (язык, hardcore)
- Пункт 2: Выход

Остальные экраны (создание персонажа, приключения, моды) будут добавлены в следующих итерациях.

## Ключевые решения

- **YAML вместо БД** — лёгкость модификации конечными пользователями
- **Словари локализации** — YAML-словари, не `gettext` (проще для модов)
- **`Character` dataclass** — вместо dict для type-safety и методов
- **`Settings` class** — инкапсуляция настроек, а не функции в `main.py`
- **No GIL/no async** — одиночная текстовая игра, синхронный код достаточен
- **Большая часть YAML-базы данных** (abilities, armor, backgrounds, etc.) — заготовки на будущее; в коде пока используются только основные файлы

## Связанные документы

- [API Reference](API.md) — детальная документация всех публичных функций и классов
- [Development Guide](DEVELOPMENT.md) — руководство по установке, запуску и разработке
- [MUD_PRD.md](MUD_PRD.md) — Product Requirements Document