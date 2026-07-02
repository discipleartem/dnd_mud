# Правила D&D 5e — справочник dnd_mud

Справочник по механикам **Dungeons & Dragons 5-й редакции** для игроков и разработчиков проекта dnd_mud. Структура следует русской **Книге игрока** (PHB 2014, перевод студии PHantom, 2016).

Индекс всей документации проекта — [`README.md`](README.md). Guide для агентов по каталогу правил — [`rules/README.md`](rules/README.md).

## Источник и авторские права

| Параметр | Значение |
|----------|----------|
| Канон | Player's Handbook 2014 (рус. перевод PHantom, файл `docs/PHB_ D&D_2023 RUS.pdf`) |
| Локальный файл | `docs/PHB_ D&D_2023 RUS.pdf` (331 стр.) |
| В репозитории | PDF **не коммитится** (см. `.gitignore`) |
| Машиночитаемый индекс | [`rules/_index/lookup.yaml`](rules/_index/lookup.yaml) (layout `agent-v2`) — единая точка входа; также [`rules/toc.yaml`](rules/toc.yaml), [`rules/_index/entities.yaml`](rules/_index/entities.yaml), [`rules/_index/spells.yaml`](rules/_index/spells.yaml) |
| Терминология RU↔EN | [`rules/reference/glossaries/ru-en.md`](rules/reference/glossaries/ru-en.md), [`rules/reference/glossaries/en-ru.md`](rules/reference/glossaries/en-ru.md) |

Имя файла PDF «2023» — локальное обозначение копии; это **не** отдельная редакция правил 2024.

### Алгоритм поиска правил

Искать **по порядку**; к следующему шагу — только если на текущем ответа нет. **Не использовать память модели.**

| Шаг | Источник | Действие |
|-----|----------|----------|
| 1 | [`docs/rules/`](rules/) | [`lookup.yaml`](rules/_index/lookup.yaml) (`by_alias` / `by_id` → `quick`, `file`); для PHB — `phb:auto` в markdown |
| 2 | `docs/PHB_ D&D_2023 RUS.pdf` | Локальный PHB (процедура доступа — [`.cursor/rules/00-project.mdc`](../.cursor/rules/00-project.mdc)) |
| 3 | Интернет | D&D **5e до редакции 2024** (PHB 2014 / SRD 5.1) |

**При расхождении:** PDF > пересказ в `docs/rules/` > веб. Код и YAML отражают реализацию в MUD.

### Политика каталога ядра

В `database/races/races.yaml` и `database/classes/classes.yaml` допускаются **только** официальные расы/подрасы и классы/подклассы из этого PHB. Расширения — моды `type: addon`.

Текст в `docs/rules/` — **пересказ механики** PHB (без лора и флавора), не дословная копия. Актуализация из PDF — **агентами** (см. [`rules/README.md`](rules/README.md)); после правок — `scripts/build_rules_index.py` для индексов. Правила PHB в `phb:auto`, MUD — в `mud:*`. Материалы D&D © Wizards of the Coast; лицензия MIT репозитория на них не распространяется.

## Аудитория

- **Игроки** — обзорные главы `00`–`11` и карточки в подкаталогах.
- **Разработчики** — блоки «Для разработчиков», `mud_status` в frontmatter, связи с `database/` и `core/`.

Игровые требования к UI и flow — в [MUD_PRD.md](MUD_PRD.md). API модулей — в [API.md](API.md).

## Оглавление

### Часть 1 — Персонаж (стр. 11–170)

| Глава PHB | Обзор | Детали | Статус в MUD |
|-----------|-------|--------|--------------|
| Введение | [chapters/00-introduction.md](rules/chapters/00-introduction.md) | — | Частично (`core/dice.py`) |
| 1. Создание персонажа | [chapters/01-character-creation.md](rules/chapters/01-character-creation.md) | — | Реализовано |
| 2. Расы | [chapters/02-races.md](rules/chapters/02-races.md) | [entities/races/](rules/entities/races/) (9 рас) | Частично (4/9 в YAML) |
| 3. Классы | [chapters/03-classes.md](rules/chapters/03-classes.md) | [entities/classes/](rules/entities/classes/) (12 классов) | Частично (4/12 в YAML) |
| 3a. Подклассы | [chapters/03-subclasses.md](rules/chapters/03-subclasses.md) | в `entities/classes/*.md` | Phase 2 |
| 4. Предыстория | [chapters/04-backgrounds.md](rules/chapters/04-backgrounds.md) | [entities/backgrounds/](rules/entities/backgrounds/) (13) | Частично |
| 5. Снаряжение | [chapters/05-equipment.md](rules/chapters/05-equipment.md) | [chapters/05-equipment-reference.md](rules/chapters/05-equipment-reference.md) | Частично |
| 6. Индивидуальные опции | [chapters/06-individual-options.md](rules/chapters/06-individual-options.md) | [chapters/06-multiclass.md](rules/chapters/06-multiclass.md), [chapters/06-feats.md](rules/chapters/06-feats.md), [entities/feats/](rules/entities/feats/) | feats: да; мультикласс: **запрещён** |

### Часть 2 — Игровой процесс (стр. 173–198)

| Глава PHB | Файл | Статус в MUD |
|-----------|------|--------------|
| 7. Использование характеристик | [chapters/07-ability-scores.md](rules/chapters/07-ability-scores.md) | Частично |
| 8. Приключения | [chapters/08-adventures.md](rules/chapters/08-adventures.md) | Запланировано |
| 9. Сражение | [chapters/09-combat.md](rules/chapters/09-combat.md) | Запланировано |

### Часть 3 — Магия (стр. 201–289)

| Глава PHB | Файл | Детали | Статус в MUD |
|-----------|------|--------|--------------|
| 10. Использование заклинаний | [chapters/10-spellcasting.md](rules/chapters/10-spellcasting.md) | — | Запланировано |
| 11. Заклинания | [chapters/11-spells.md](rules/chapters/11-spells.md) | [entities/spells/](rules/entities/spells/) (~270 карточек) | Не реализовано |

Индексы заклинаний: [по уровню](rules/_index/spells/by-level.md), [по школе](rules/_index/spells/by-school.md).

### Приложения и словари (стр. 290–326)

| Раздел | Обзор | Детали |
|--------|-------|--------|
| Приложения | [chapters/appendices.md](rules/chapters/appendices.md) | [reference/appendices/](rules/reference/appendices/) |
| Словари | [reference/glossaries/ru-en.md](rules/reference/glossaries/ru-en.md) | [reference/glossaries/en-ru.md](rules/reference/glossaries/en-ru.md) |

## Глоссарий (краткий)

Полный словарь — [`rules/reference/glossaries/`](rules/reference/glossaries/). Ключи в коде — английские; в UI — через `database/strings/`.

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
