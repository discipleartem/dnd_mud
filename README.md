# D&D MUD — текстовая MUD-игра по мотивам Dungeons & Dragons 5e

**Версия:** 0.1.0 (Pre-Alpha)

Текстовая приключенческая игра в жанре MUD, основанная на правилах **Dungeons & Dragons 5-й редакции**.  
Фокус на одиночное прохождение с выбором действий из нумерованных списков.  
Модульная архитектура и YAML-конфигурация позволяют модифицировать игру без навыков программирования.

---

## Особенности

- 🎲 **Генерация персонажа** — сложность → имя → раса → подраса → характеристики → класс. Три метода в Normal (стандартный массив `[15,14,13,12,10,8]`, point-buy 27 очков, 4d6 drop lowest) или авто-4d6×6 в HardCore. Расовые бонусы показываются до распределения; итог — с учётом бонусов. В Normal доступна переквалификация.
- 🧝 **Расы и подрасы** — человек (базовый и вариант), эльф, дварф, полуорк и другие — с расовыми бонусами
- ⚔️ **Классы** — воин, плут, волшебник, жрец и другие из SRD
- 🛡️ **Экипировка** — YAML в `database/_future/equipment/` (Phase 2)
- 📚 **Навыки и особенности** — YAML в `database/_future/` (Phase 2)
- 🌐 **Локализация** — поддержка русского и английского языков (YAML-словари)
- ⚙️ **Модификации** — пример формата в `mods/_examples/` (runtime не подключён)
- 🎨 **Цветной терминал** — адаптивный вывод с переносом текста под ширину окна
- 🔧 **Режимы сложности** — Normal и HardCore (в перспективе Easy). HardCore — ключевой режим: авто-генерация характеристик, в будущем — gating приключений и модов, полная механика D&D 5e

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
make test              # pytest
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
│   ├── character.py                 # CRUD персонажей, генерация характеристик
│   ├── dice.py                      # Броски кубиков
│   ├── adventure.py                 # Загрузка приключений из YAML
│   ├── localization.py              # Локализация (YAML-словари)
│   └── settings.py                  # Настройки пользователя (JSON)
│
├── ui/                              # Пользовательский интерфейс
│   ├── __init__.py
│   ├── menus.py                     # Отрисовка меню
│   └── input_handler.py             # Валидация ввода (числа, строки, выбор)
│
├── database/                        # База данных правил D&D 5e
│   ├── races/races.yaml
│   ├── classes/classes.yaml
│   ├── content/adventures.yaml
│   ├── core/settings.json.example   # Шаблон настроек
│   ├── _future/                     # Справочники Phase 2 (не загружаются)
│   └── strings/{ru,en}.yaml
├── saves/                           # Пользовательские данные (gitignored)
│   └── characters.json
│
├── adventures_scripts/              # Сценарии приключений (YAML, заглушки)
│   ├── tutorial.yaml                # Обучение
│   └── lost_mine.yaml               # «Затерянные рудники Фанделвера»
│
├── mods/                            # Примеры модов
│   └── _examples/example_mod.yaml
│
├── tests/                           # Тесты (12)
│   ├── test_character.py
│   ├── test_settings.py
│   └── test_integration_menus.py
│
└── docs/                            # Документация
    ├── MUD_PRD.md                   # Product Requirements Document
    ├── ARCHITECTURE.md              # Архитектура проекта
    ├── API.md                       # API Reference
    ├── DEVELOPMENT.md               # Руководство разработчика
    └── CHANGELOG.md                 # История изменений
```

---

## Текущее состояние главного меню

| № | Пункт | Статус |
|---|-------|--------|
| 1 | Новая игра | Реализовано (flow без полного engine) |
| 2 | Загрузить игру | Заглушка |
| 3 | Создать персонажа | Реализовано |
| 4 | Настройки | Реализовано |
| 5 | Languages | Реализовано |
| 0 | Выход | Реализовано |

---

## Статус разработки (Pre-Alpha)

### Реализовано
- [x] Приветственный экран (ASCII-art + colorama)
- [x] Главное меню (5 пунктов + Выход)
- [x] Экран настроек и Languages
- [x] Flow «Создать персонажа» с генерацией характеристик (standard array, point-buy, 4d6, HardCore)
- [x] Подрасы и variant human
- [x] Модель персонажа (`Character` dataclass, JSON в `saves/characters.json`)
- [x] Броски кубиков, локализация, каталог приключений
- [x] Валидация ввода

### В разработке
- [ ] Flow «Загрузить игру» (заглушка)
- [ ] Игровой цикл и сценарии приключений
- [ ] Runtime-применение модов

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

**Правила Git:**
- Запрещены прямые коммиты в `main`
- Рабочие ветки: `feature/*`, `fix/*`, `refactor/*`, `chore/*`
- Каждый коммит атомарен и работоспособен
- Перед PR — `git rebase main`

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