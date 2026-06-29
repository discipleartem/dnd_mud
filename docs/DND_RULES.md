# Правила D&D 5e — справочник dnd_mud

Краткий справочник по механикам **Dungeons & Dragons 5-й редакции** для игроков и разработчиков проекта dnd_mud. Структура следует русской **Книге игрока** (Player's Handbook 2014, перевод студии PHantom).

## Источник и авторские права

| Параметр | Значение |
|----------|----------|
| Канон | Player's Handbook (рус. перевод PHantom, файл `docs/PHB_ D&D_2023 RUS.pdf`) |
| Локальный файл | `docs/PHB_ D&D_2023 RUS.pdf` (331 стр.) |
| В репозитории | PDF **не коммитится** по умолчанию (см. `.gitignore`) |

### Политика каталога ядра

В `database/races/races.yaml` и `database/classes/classes.yaml` допускаются **только** официальные расы/подрасы и классы/подклассы из этого PHB. Расширения — моды `type: addon`.

Положите PDF в `docs/` локально для сверки с первоисточником. Текст в этом справочнике — **сжатый пересказ**, не копия PHB. Материалы D&D © Wizards of the Coast; лицензия MIT репозитория на них не распространяется.

## Аудитория

- **Игроки** — как работают правила (формулы, порядок действий, термины).
- **Разработчики** — что уже реализовано в MUD, где лежат данные (`database/`, `core/`), что запланировано в Phase 2.

Игровые требования к UI и flow — в [MUD_PRD.md](MUD_PRD.md). API модулей — в [API.md](API.md).

## Оглавление

| Глава PHB | Файл | Статус в MUD |
|-----------|------|--------------|
| Введение | [rules/00-introduction.md](rules/00-introduction.md) | Частично (`core/dice.py`) |
| 1. Создание персонажа | [rules/01-character-creation.md](rules/01-character-creation.md) | Реализовано (языки, предыстория, владения; без стартового снаряжения) |
| 2. Расы | [rules/02-races.md](rules/02-races.md) | Частично (4 из 9 рас PHB) |
| 3. Классы | [rules/03-classes.md](rules/03-classes.md) | Частично (4 из 12 классов PHB) |
| 3a. Подклассы | [rules/03-subclasses.md](rules/03-subclasses.md) | Phase 2; каталог — только `classes.yaml` |
| 4. Личность и предыстория | [rules/04-backgrounds.md](rules/04-backgrounds.md) | Частично (выбор предыстории) |
| 5. Снаряжение | [rules/05-equipment.md](rules/05-equipment.md) | Частично (каталог, владения, КД/атака API) |
| 6. Мультикласс и черты | [rules/06-multiclass-feats.md](rules/06-multiclass-feats.md) | Мультикласс: **запрещено**; черты: данные в YAML, UI выбора — Phase 2 |
| 7. Использование характеристик | [rules/07-ability-scores.md](rules/07-ability-scores.md) | Частично (checks API, PB по уровню) |
| 8. Приключения | [rules/08-adventures.md](rules/08-adventures.md) | Запланировано (engine) |
| 9. Сражение | [rules/09-combat.md](rules/09-combat.md) | Запланировано (engine) |
| 10–11. Заклинания | [rules/10-spells.md](rules/10-spells.md) | Не реализовано |
| Приложения | [rules/appendices.md](rules/appendices.md) | Запланировано |

## Глоссарий (русская терминология PHB)

Ключи в коде — английские (`strength`, `dexterity`, …); в UI — через `database/strings/`.

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
