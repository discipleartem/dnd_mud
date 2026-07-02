# Правила D&D 5e — справочник dnd_mud

Справочник по механикам **Dungeons & Dragons 5-й редакции** для игроков и разработчиков проекта dnd_mud. Структура следует русской **Книге игрока** (PHB 2014, перевод студии PHantom, 2016).

## Источник и авторские права

| Параметр | Значение |
|----------|----------|
| Канон | Player's Handbook 2014 (рус. перевод PHantom, файл `docs/PHB_ D&D_2023 RUS.pdf`) |
| Локальный файл | `docs/PHB_ D&D_2023 RUS.pdf` (331 стр.) |
| В репозитории | PDF **не коммитится** (см. `.gitignore`) |
| Машиночитаемый индекс | [`rules/toc.yaml`](rules/toc.yaml) — точка входа для агентов |
| Терминология RU↔EN | [`rules/glossaries/ru-en.md`](rules/glossaries/ru-en.md), [`rules/glossaries/en-ru.md`](rules/glossaries/en-ru.md) |

Имя файла PDF «2023» — локальное обозначение копии; это **не** отдельная редакция правил 2024.

### Политика каталога ядра

В `database/races/races.yaml` и `database/classes/classes.yaml` допускаются **только** официальные расы/подрасы и классы/подклассы из этого PHB. Расширения — моды `type: addon`.

Текст в `docs/rules/` — **пересказ** правил, не дословная копия PHB. Материалы D&D © Wizards of the Coast; лицензия MIT репозитория на них не распространяется.

Генерация справочника из PDF: `python scripts/phb_generate_rules.py` (dev-tool). Валидация: `python scripts/phb_validate_rules.py`.

## Аудитория

- **Игроки** — обзорные главы `00`–`11` и карточки в подкаталогах.
- **Разработчики** — блоки «Для разработчиков», `mud_status` в frontmatter, связи с `database/` и `core/`.

Игровые требования к UI и flow — в [MUD_PRD.md](MUD_PRD.md). API модулей — в [API.md](API.md).

## Оглавление

### Часть 1 — Персонаж (стр. 11–170)

| Глава PHB | Обзор | Детали | Статус в MUD |
|-----------|-------|--------|--------------|
| Введение | [00-introduction.md](rules/00-introduction.md) | — | Частично (`core/dice.py`) |
| 1. Создание персонажа | [01-character-creation.md](rules/01-character-creation.md) | — | Реализовано |
| 2. Расы | [02-races.md](rules/02-races.md) | [rules/races/](rules/races/) (9 рас) | Частично (4/9 в YAML) |
| 3. Классы | [03-classes.md](rules/03-classes.md) | [rules/classes/](rules/classes/) (12 классов) | Частично (4/12 в YAML) |
| 3a. Подклассы | [03-subclasses.md](rules/03-subclasses.md) | в `classes/*.md` | Phase 2 |
| 4. Предыстория | [04-backgrounds.md](rules/04-backgrounds.md) | [rules/backgrounds/](rules/backgrounds/) (13) | Частично |
| 5. Снаряжение | [05-equipment.md](rules/05-equipment.md) | [05-equipment-reference.md](rules/05-equipment-reference.md) | Частично |
| 6. Индивидуальные опции | [06-individual-options.md](rules/06-individual-options.md) | [06-multiclass.md](rules/06-multiclass.md), [06-feats.md](rules/06-feats.md) | feats: да; мультикласс: **запрещён** |

### Часть 2 — Игровой процесс (стр. 173–198)

| Глава PHB | Файл | Статус в MUD |
|-----------|------|--------------|
| 7. Использование характеристик | [07-ability-scores.md](rules/07-ability-scores.md) | Частично |
| 8. Приключения | [08-adventures.md](rules/08-adventures.md) | Запланировано |
| 9. Сражение | [09-combat.md](rules/09-combat.md) | Запланировано |

### Часть 3 — Магия (стр. 201–289)

| Глава PHB | Файл | Детали | Статус в MUD |
|-----------|------|--------|--------------|
| 10. Использование заклинаний | [10-spellcasting.md](rules/10-spellcasting.md) | — | Запланировано |
| 11. Заклинания | [11-spells.md](rules/11-spells.md) | [rules/spells/](rules/spells/) (~270 карточек) | Не реализовано |

Индексы заклинаний: [по уровню](rules/spells/_index-by-level.md), [по школе](rules/spells/_index-by-school.md).

### Приложения и словари (стр. 290–326)

| Раздел | Обзор | Детали |
|--------|-------|--------|
| Приложения | [appendices.md](rules/appendices.md) | [rules/appendices/](rules/appendices/) |
| Словари | [glossaries/ru-en.md](rules/glossaries/ru-en.md) | [glossaries/en-ru.md](rules/glossaries/en-ru.md) |

## Глоссарий (краткий)

Полный словарь — [`rules/glossaries/`](rules/glossaries/). Ключи в коде — английские; в UI — через `database/strings/`.

| RU (PHB) | EN | Ключ в коде |
|----------|-----|-------------|
| Сила | Strength | `strength` |
| Ловкость | Dexterity | `dexterity` |
| Телосложение | Constitution | `constitution` |
| Интеллект | Intelligence | `intelligence` |
| Мудрость | Wisdom | `wisdom` |
| Харизма | Charisma | `charisma` |
| Модификатор характеристики | Ability modifier | `ability_modifier()` |
| Проверка характеристики | Ability check | `core/checks.ability_check()` |
| Спасбросок | Saving throw | `core/checks.saving_throw()` |
| Бонус мастерства | Proficiency bonus | `core/constants.proficiency_bonus()` |
| Преимущество / помеха | Advantage / disadvantage | `core/checks.roll_d20()` |
| Кость хитов | Hit die | `hit_dice` в `classes.yaml` |
| Хиты (HP) | Hit points | `current_hp`, `max_hp` в `Character` |
| Сл (Сложность) | DC (Difficulty Class) | — |
| Владение | Proficiency | `Character.*_proficiencies`, `core/proficiencies.py` |
| Действие / бонусное действие / реакция | Action / bonus action / reaction | — |

## Модификатор характеристики

Формула PHB: `(значение − 10) // 2` (целочисленное деление вниз).

| Значение | 1 | 2–3 | 4–5 | 6–7 | 8–9 | 10–11 | 12–13 | 14–15 | 16–17 | 18–19 | 20 |
|----------|---|-----|-----|-----|-----|-------|-------|-------|-------|-------|-----|
| Модификатор | −5 | −4 | −3 | −2 | −1 | +0 | +1 | +2 | +3 | +4 | +5 |

Реализация: `core/dice.py` → `ability_modifier()`.

## Бонус мастерства по уровню (PHB)

| Уровень | 1–4 | 5–8 | 9–12 | 13–16 | 17–20 |
|---------|-----|-----|------|-------|-------|
| Бонус | +2 | +3 | +4 | +5 | +6 |

На 1 уровне персонажа MUD бонус мастерства = **+2** (по PHB). Расчёт: `core/constants.proficiency_bonus(level)` из `database/core/constants.yaml`.

## Режимы сложности MUD

| Режим | ID | Отношение к PHB |
|-------|-----|-----------------|
| Нормальная | `normal` | Упрощённая механика в приключениях; полный контроль над генерацией характеристик |
| HardCore | `hardcore` | Целевой режим **полных** правил D&D 5e в game engine (Phase 2) |
| Лёгкая | `easy` | Зарезервировано |

Подробнее: [ARCHITECTURE.md](ARCHITECTURE.md) §Режимы сложности.
