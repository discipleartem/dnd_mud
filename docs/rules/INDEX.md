# Справочник PHB — оглавление

Канон: **Player's Handbook 2014** (PHantom 2016). Только механика, без лора.

| Кому | С чего начать |
|------|----------------|
| **Игрок / человек** | Этот файл → нужная глава или карточка |
| **Агент (Cursor)** | [`_index/lookup.yaml`](_index/lookup.yaml) → `by_alias` / `by_id` → `quick` → `file` |
| **Статус в MUD** | [`../DND_RULES.md`](../DND_RULES.md) |

Guide агента: [`README.md`](README.md).

## Часть 1 — Персонаж

| Тема | Обзор | Карточки |
|------|-------|----------|
| Введение | [00-introduction](chapters/00-introduction.md) | — |
| Создание персонажа | [01-character-creation](chapters/01-character-creation.md) | — |
| Расы | [02-races](chapters/02-races.md) | [entities/races/](entities/races/) |
| Классы | [03-classes](chapters/03-classes.md) | [entities/classes/](entities/classes/) |
| Подклассы | [03-subclasses](chapters/03-subclasses.md) | в файлах классов |
| Предыстории | [04-backgrounds](chapters/04-backgrounds.md) | [entities/backgrounds/](entities/backgrounds/) |
| Снаряжение | [05-equipment](chapters/05-equipment.md) | [таблицы](chapters/05-equipment-reference.md) |
| Мультикласс / черты | [06-individual-options](chapters/06-individual-options.md) | [feats](entities/feats/), [мультикласс](chapters/06-multiclass.md) |

## Часть 2 — Игра

| Тема | Файл |
|------|------|
| Характеристики | [07-ability-scores](chapters/07-ability-scores.md) |
| Приключения | [08-adventures](chapters/08-adventures.md) |
| Сражение | [09-combat](chapters/09-combat.md) |

## Часть 3 — Магия

| Тема | Обзор | Каталог |
|------|-------|---------|
| Накладывание | [10-spellcasting](chapters/10-spellcasting.md) | — |
| Заклинания | [11-spells](chapters/11-spells.md) | [по уровню](_index/spells/by-level.md) · [по школе](_index/spells/by-school.md) · [entities/spells/](entities/spells/) |

## Приложения и словари

| Раздел | Файл |
|--------|------|
| Обзор | [appendices](chapters/appendices.md) |
| Состояния | [A-conditions](reference/appendices/A-conditions.md) |
| Параметры существ | [D-creatures](reference/appendices/D-creatures.md) |
| EN→RU | [en-ru](reference/glossaries/en-ru.md) |
| RU→EN | [ru-en](reference/glossaries/ru-en.md) |

## Быстрый поиск по имени

1. Откройте [`_index/lookup.yaml`](_index/lookup.yaml).
2. В `by_alias` найдите RU- или EN-название (например `воин`, `fireball`).
3. По `id` в `by_id` прочитайте `quick`; при необходимости откройте `file`.
