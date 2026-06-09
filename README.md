# D&D MUD — текстовая MUD-игра по мотивам Dungeons & Dragons 5e

**Версия:** 0.1.0 (Pre-Alpha)

Текстовая приключенческая игра в жанре MUD, основанная на правилах **Dungeons & Dragons 5-й редакции**.  
Фокус на одиночное прохождение с выбором действий из нумерованных списков.  
Модульная архитектура и YAML-конфигурация позволяют модифицировать игру без навыков программирования.

---

## Особенности

- 🎲 **Генерация персонажа** — выбор расы, класса, распределение характеристик (стандартный массив D&D 5e)
- 🧝 **Расы и подрасы** — человек, эльф (высший, лесной, дроу), дварф (холмовой, горный), полуорк — с полными расовыми бонусами и особенностями
- ⚔️ **Классы** — воин, плут, волшебник, жрец, варвар, паладин, следопыт, бард, друид, монах, колдун, чародей (все классы SRD)
- 🛡️ **Экипировка** — доспехи, оружие, инструменты, снаряжение — полная база предметов D&D 5e
- 📚 **Навыки, языки, особенности** — более 30 навыков, 30+ языков, 200+ особенностей (feats, class features, racial traits)
- 🌐 **Локализация** — поддержка русского и английского языков
- ⚙️ **Модификации** — подключаемые YAML-моды без перепрограммирования
- 🎨 **Цветной терминал** — адаптивный вывод с переносом текста под ширину окна
- 🔧 **Hard Core режим** — для опытных игроков

---

## Стек технологий

| Компонент       | Технология             |
|-----------------|------------------------|
| Язык            | Python 3.12+           |
| Цветной вывод   | colorama               |
| Конфигурация    | YAML (PyYAML)          |
| Локализация     | gettext / babel        |
| Модели данных   | dataclasses, enum      |
| Сборка          | pyproject.toml         |

---

## Установка

```bash
# Клонирование репозитория
git clone git@github.com:discipleartem/dnd_mud.git
cd dnd_mud

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install -e .
```

## Запуск

```bash
source .venv/bin/activate
python main.py
```

## Тестирование

```bash
source .venv/bin/activate
pytest
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
│   ├── game_engine.py               # Главный игровой цикл
│   ├── character.py                 # Класс персонажа
│   ├── dice.py                      # Броски кубиков
│   ├── adventure.py                 # Сценарии приключений
│   ├── mod_loader.py                # Загрузка модификаций
│   └── localization.py              # Локализация (gettext)
│
├── ui/                              # Пользовательский интерфейс
│   ├── window_manager.py            # Адаптивный вывод текста
│   ├── menus.py                     # Отрисовка меню
│   └── input_handler.py             # Обработка и валидация ввода
│
├── database/                        # База данных правил (YAML)
│   ├── abilities.yaml               # Характеристики и навыки
│   ├── armor.yaml                   # Доспехи и щиты
│   ├── backgrounds.yaml             # Предыстории персонажей
│   ├── classes.yaml                 # Классы персонажей
│   ├── constants.yaml               # Константы (модификаторы, DC, hit dice и др.)
│   ├── equipment.yaml               # Снаряжение
│   ├── features.yaml                # Особенности (фиты, классовые, расовые)
│   ├── feats.yaml                   # Фиты
│   ├── languages.yaml               # Языки
│   ├── races.yaml                   # Расы и подрасы
│   ├── sizes.yaml                   # Размеры существ
│   ├── skills.yaml                  # Навыки
│   ├── tools.yaml                   # Инструменты
│   └── weapon.yaml                  # Оружие
│
├── adventures_scripts/              # Сценарии приключений (YAML)
│   ├── tutorial.yaml                # Обучение
│   └── lost_mine.yaml               # «Затерянные рудники Фанделвера»
│
├── mods/                            # Пользовательские модификации
│   └── example_mod.yaml             # Пример мода
│
└── docs/                            # Документация
    └── MUD_PRD.md                   # Product Requirements Document
```

---

## База данных (database/)

Все игровые данные хранятся в YAML-файлах и легко редактируются. Каждый файл организован по единому принципу: корневой ключ — имя сущности, id — строковый snake_case идентификатор.

### Характеристики — `abilities.yaml`
Шесть базовых характеристик D&D 5e с привязанными к ним навыками.
```yaml
abilities:
  strength:
    name: "Сила"
    description: "Измеряет физическую мощь и атлетичность"
    skills:
      athletics: "Атлетика"
  dexterity:
    name: "Ловкость"
    skills:
      acrobatics: "Акробатика"
      stealth: "Скрытность"
      sleight_of_hand: "Ловкость рук"
  # ... и т.д.
```

### Расы — `races.yaml`
Расы с подрасами, расовыми бонусами к характеристикам и особенностями.
```yaml
races:
  human:
    name: "Человек"
    size: "medium"
    speed: 30
    ability_bonuses: { strength: 1, dexterity: 1, constitution: 1, intelligence: 1, wisdom: 1, charisma: 1 }
    features: ["additional_language"]
    subraces:
      variant_human: { ... }
  elf:
    name: "Эльф"
    ability_bonuses: { dexterity: 2 }
    features: ["keen_senses", "darkvision_60", "fey_ancestry", "trance"]
    subraces:
      high_elf: { ... }
      wood_elf: { ... }
      dark_elf_drow: { ... }
```

### Классы — `classes.yaml`
Классы персонажей с хитами, прокачкой навыков, спасбросками и умениями.
```yaml
classes:
  barbarian:
    name: "Варвар"
    hit_die: 12
    primary_ability: "strength"
    saving_throws: ["strength", "constitution"]
    skills_proficiencies: 2
    multiclass_requirements: { strength: 13 }
```

### Доспехи — `armor.yaml`
Доспехи всех категорий (лёгкие, средние, тяжёлые, щиты) с AC, модификаторами и требованиями.
```yaml
armor:
  leather:
    name: "Кожаный доспех"
    category: "light"
    armor_class: 11
    modifier_bonus: "DEX"
    weight: 10
    cost: { value: 10, currency: "gold" }
```

### Оружие — `weapon.yaml`
Простое и воинское оружие с уроном, свойствами, типом урона и весом.
```yaml
weapons:
  longsword:
    name: "Длинный меч"
    category: "martial"
    damage: { dice_count: 1, dice_value: 8, damage_type: "slashing" }
    versatile_damage: { dice_count: 1, dice_value: 10 }
    weight: 3
    properties: ["versatile"]
```

### Особенности — `features.yaml`
Все особенности, фиты, расовые и классовые умения — переиспользуемый справочник.
```yaml
features:
  darkvision_60:
    name: "Тёмное зрение (60 футов)"
    description: "Вы видите в тусклом свете как при ярком, а в темноте как при тусклом"
    type: "racial"
  ...
```

### Языки — `languages.yaml`
Стандартные, экзотические, секретные, элементальные и планарные языки.
```yaml
languages:
  common:
    name: "Общий"
    type: "standard"
    script: "common"
  draconic:
    name: "Драконий"
    type: "exotic"
    script: "draconic"
```

### Навыки — `skills.yaml`
Детальное описание каждого навыка с ключевой характеристикой.
```yaml
skills:
  acrobatics:
    name: "Акробатика"
    ability: "dexterity"
    description: "Позволяет удерживать равновесие, кувыркаться"
```

### Константы — `constants.yaml`
Системные константы: модификаторы характеристик (1–30), hit dice по классам, классы сложности (DC), типы языков, алфавиты, размеры, ситуационные модификаторы.

### Предыстории — `backgrounds.yaml`
Предыстории персонажа с навыками, инструментами, языками и стартовым снаряжением.

### Снаряжение — `equipment.yaml`
Общее снаряжение: рюкзаки, верёвки, факелы, фляги и т.д. с ценами и весом.

### Инструменты — `tools.yaml`
Инструменты ремесленников, музыкальные инструменты, игровые наборы и транспорт.

### Фиты — `feats.yaml`
Отдельный файл с фитами (чертами) для variant human и высокоуровневых персонажей.

### Размеры — `sizes.yaml`
Категории размеров существ (Tiny — Gargantuan) с описанием и механическими эффектами.

---

## Модификации (mods/)

Моды — YAML-файлы в папке `mods/`, которые добавляют или изменяют существующие данные.

```yaml
name: "Новая раса — Драконорождённый"
version: "1.0"
type: "addon"      # addon — расширение, mod — изменение логики
description: "Добавляет расу Dragonborn"
files:
  - target: "database/races.yaml"
    action: "append"   # append / replace / delete
    data:
      - id: dragonborn
        name:
          ru: "Драконорождённый"
          en: "Dragonborn"
        ability_bonuses:
          strength: 2
          charisma: 1
```

---

## Статус разработки (Pre-Alpha)

### Реализовано
- [x] Приветственный экран (ASCII-art + colorama)
- [x] Главное меню (8 пунктов)
- [x] Window Manager (адаптивный перенос текста)
- [x] Создание персонажа (имя, раса, класс, характеристики)
- [x] Сохранение/загрузка персонажа (YAML)
- [x] Настройки (размер шрифта, Hard Core)
- [x] Меню Languages (русский/английский)
- [x] База данных правил D&D 5e (14 YAML-файлов)

### В разработке
- [ ] Меню модификаций (сканирование и активация .yaml модов)
- [ ] Меню приключений (выбор сценария)
- [ ] Полноценный движок приключений (комнаты, проверки навыков, бой)
- [ ] Система сохранения игрового состояния
- [ ] Режим Hard Core (перманентная смерть)

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

---

## Лицензия

MIT

---

## Благодарности

- Dungeons & Dragons 5th Edition — Wizards of the Coast
- SRD (System Reference Document) 5.1
- Сообщество Python и open-source библиотек