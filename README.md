# D&D MUD — текстовая MUD-игра по мотивам Dungeons & Dragons 5e

**Версия:** 0.1.0 (Pre-Alpha)

Текстовая приключенческая игра в жанре MUD, основанная на правилах **Dungeons & Dragons 5-й редакции**.  
Фокус на одиночное прохождение с выбором действий из нумерованных списков.  
Модульная архитектура и YAML-конфигурация позволяют модифицировать игру без навыков программирования.

---

## Особенности

- 🎲 **Генерация персонажа** — сложность → имя → раса → подраса → характеристики → предыстория → языки → класс → подкласс → владения → навыки. Три метода в Normal или авто-4d6×6 в HardCore; режим Easy — старт с 3 уровня.
- 🧝 **Расы и подрасы** — человек (`standard` / `variant_human`), эльф, дварф, полуорк; единая модель `subraces` в YAML
- ⚔️ **Классы** — воин, плут, бард, жрец и другие из SRD; подклассы, левелап, черты PHB
- 🛡️ **Экипировка** — каталог в `database/equipment/`; боевое применение — Phase 2
- 📚 **Предыстории и навыки** — 13 PHB backgrounds (`grants[]`), выбор навыков класса
- 🌐 **Локализация** — поддержка русского и английского языков (YAML-словари)
- ⚙️ **Модификации** — overlay через `core/mod_loader.py`; пример `mods/dragonborn_pack/`; включение в `database/core/mods_state.json`
- 🎨 **Цветной терминал** — адаптивный вывод с переносом текста под ширину окна
- 🔧 **Режимы сложности** — Normal, HardCore и Easy. HardCore — авто-генерация характеристик, gating приключений; Easy — старт с 3 уровня

---

## Стек технологий

| Компонент       | Технология                    |
|-----------------|-------------------------------|
| Язык            | Python 3.12+                  |
| Цветной вывод   | colorama                      |
| Конфигурация    | YAML (PyYAML)                 |
| Локализация     | YAML-словари (самописная)     |
| Модели данных   | dataclasses                   |
| Сборка          | pyproject.toml                |
| Линтер          | ruff                          |
| Форматирование  | black                         |
| Типизация       | mypy (strict mode)            |

---

## Установка

### Установка (через Makefile)

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

## Запуск

```bash
source .venv/bin/activate
python main.py
```

Или через установленный скрипт:

```bash
source .venv/bin/activate
dnd_mud
```

## Тестирование

```bash
make verify-changed    # lint + test (staged)
make verify-scope      # lint + test (diff vs dev)
make verify            # full check + test (CI)
make test              # pytest + coverage
make check             # ruff + black + mypy
pytest -v              # подробный вывод
pytest --cov=.         # с coverage
```

---

## Структура проекта

```
dnd_mud/
├── main.py                          # Точка входа
├── pyproject.toml                   # Конфигурация проекта и зависимостей
├── README.md                        # Документация проекта
│
├── core/                            # Ядро игры
│   ├── models.py                    # Dataclass: Character, Adventure
│   ├── character.py                 # Фасад: персонажи, stats, races/classes loaders
│   ├── grants.py                    # Нормализация grants[] из YAML
│   ├── mod_loader.py                # Deep-merge overlay модов
│   ├── dice.py                      # Броски кубиков
│   ├── adventure.py                 # Загрузка приключений из YAML
│   ├── difficulty.py                # Фильтр приключений по режиму сложности
│   ├── localization.py              # Локализация (YAML-словари)
│   └── settings.py                  # Настройки пользователя (JSON)
│
├── ui/                              # Пользовательский интерфейс
│   ├── input_handler.py             # Валидация ввода (числа, строки, выбор)
│   └── menus/                       # Экраны меню (_creation_steps, stats, …)
│
├── database/                        # База данных правил D&D 5e
│   ├── races/races.yaml
│   ├── classes/classes.yaml
│   ├── backgrounds/backgrounds.yaml
│   ├── content/adventures.yaml
│   ├── core/settings.json.example
│   ├── core/mods_state.json         # Включённые моды
│   └── strings/{ru,en}.yaml
├── saves/                           # Пользовательские данные (gitignored)
│   └── characters/                  # Персонажи (по одному JSON на персонажа)
│
├── adventures/              # Сценарии приключений (YAML, заглушки)
│   ├── tutorial.yaml                # Обучение
│   └── lost_mine.yaml               # «Затерянные рудники Фанделвера»
│
├── mods/                            # Моды (overlay YAML)
│   ├── dragonborn_pack/             # Пример: manifest + overlay.yaml
│   └── _examples/example_mod.yaml
│
├── tests/                           # Тесты (pytest)
│   ├── test_adventure.py
│   ├── test_character.py
│   ├── test_difficulty.py
│   ├── test_dice.py
│   ├── test_input_handler.py
│   ├── test_localization.py
│   ├── test_main.py
│   ├── test_menus_creation.py
│   ├── test_menus_new_game.py
│   ├── test_menus_characters_hub.py
│   ├── test_data_schema.py
│   ├── test_menus_stats.py
│   ├── test_models.py
│   └── test_settings.py
│
└── docs/                            # Документация
    ├── README.md                    # Индекс документации
    ├── DATA_SCHEMA.md               # Схема YAML (grants, subraces, mods)
    ├── DND_RULES.md                 # Правила D&D 5e (оглавление PHB)
    ├── rules/                       # Справочник PHB (layout agent-v2)
    ├── MUD_PRD.md                   # Product Requirements Document
    ├── ARCHITECTURE.md              # Архитектура проекта
    ├── API.md                       # API Reference
    ├── BACKLOG.md                   # Backlog
    ├── DEVELOPMENT.md               # Руководство разработчика
    └── CHANGELOG.md                 # История изменений
```

Правила для AI-агентов: [AGENTS.md](AGENTS.md) (локальные) + `~/.cursor/rules/` (глобальные).

---

## Текущее состояние главного меню

| № | Пункт | Статус |
|---|-------|--------|
| 1 | Новая игра | Реализовано (персонаж → приключение; без полного engine) |
| 2 | Загрузить игру | Заглушка |
| 3 | Создать персонажа | Реализовано |
| 4 | Настройки | Заглушка (только «Назад»; язык — в Languages) |
| 5 | Languages | Реализовано |
| 0 | Выход | Реализовано |

---

## Статус разработки (Pre-Alpha)

### Реализовано
- [x] Приветственный экран (ASCII-art + colorama)
- [x] Главное меню (5 пунктов + Выход)
- [x] Экран настроек (заглушка) и Languages
- [x] Flow «Создать персонажа» с генерацией характеристик (standard array, point-buy, 4d6, HardCore)
- [x] Подрасы, variant human, предыстории, языки, черты PHB
- [x] Mod overlay (`core/mod_loader.py`, `mods/dragonborn_pack/`)
- [x] Модель персонажа (`Character` dataclass, JSON в `saves/characters/*.json`)
- [x] Броски кубиков, локализация, каталог приключений
- [x] Валидация ввода

### В разработке
- [ ] Flow «Загрузить игру» (заглушка)
- [ ] Игровой цикл и сценарии приключений
- [ ] UI включения модов; gating модов по режиму HardCore

---

## Разработка

### Принципы

Проект следует принципам **KISS**, **DRY** и **YAGNI** — минимальная сложность, отсутствие дублирования, никакого кода «на будущее».  
Паттерны проектирования применяются только при реальной необходимости.

### Коммиты

Используется [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: добавлен генератор характеристик персонажа
fix: исправлен расчёт модификатора при значении > 20
refactor: вынесена логика валидации ввода в input_handler
chore: обновлены зависимости в pyproject.toml
```

**Правила Git** — [`AGENTS.md`](AGENTS.md) · [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) §Git Workflow

### Линтинг и форматирование

```bash
make check             # ruff --fix + black + mypy
```

---

## Лицензия

MIT

---

## Благодарности

- Dungeons & Dragons 5th Edition — Wizards of the Coast
- SRD (System Reference Document) 5.1
- Сообщество Python и open-source библиотек