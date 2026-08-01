# Правила D&D 5e — справочник dnd_mud

Справочник механики **Dungeons & Dragons 5-й редакции** для разработчиков и агентов проекта dnd_mud. Пересказ следует русской **Книге игрока** (PHB **2014**, перевод студии PHantom, 2016).

Индекс документации — [`README.md`](README.md). Оглавление справочника для людей — [`rules/INDEX.md`](rules/INDEX.md). Guide для агентов — [`rules/README.md`](rules/README.md) → [`rules/_index/lookup.yaml`](rules/_index/lookup.yaml).

## Источник и авторские права

| Параметр | Значение |
|----------|----------|
| Канон | Player's Handbook **2014** (рус. перевод PHantom, 2016); не редакция 2024 |
| Машиночитаемый индекс | [`rules/_index/lookup.yaml`](rules/_index/lookup.yaml) |
| Терминология RU↔EN | [`rules/reference/glossaries/ru-en.md`](rules/reference/glossaries/ru-en.md), [`rules/reference/glossaries/en-ru.md`](rules/reference/glossaries/en-ru.md) |

### Алгоритм поиска правил

**Не использовать память модели.** Полный канон — [`.cursor/rules/00-project.mdc`](../.cursor/rules/00-project.mdc) §D&D 5e.

| Шаг | Источник | Действие |
|-----|----------|----------|
| 1a | [`lookup.yaml`](rules/_index/lookup.yaml) | `by_alias` (RU/EN/slug) → `id` или сразу `by_id` |
| 1b | `by_id` | Прочитать `quick` (часто достаточно) |
| 1c | `file` | Детали карточки в `docs/rules/` |
| 1d | обзор | Люди: [`INDEX.md`](rules/INDEX.md); MUD-статус: этот файл; guide: [`rules/README.md`](rules/README.md) |
| 2 | Интернет | D&D **5e до редакции 2024** (PHB 2014 / SRD 5.1); затем обновить карточку + индексы вручную |

**При расхождении:** шаг 2 > шаг 1. Код и YAML отражают реализацию в MUD. Текст в `docs/rules/` — **пересказ механики** (без лора), не дословная копия. Материалы D&D © Wizards of the Coast.

### Политика каталога ядра

В `database/races/races.yaml` и `database/classes/classes.yaml` допускаются **только** официальные расы/подрасы и классы/подклассы из PHB 2014. Расширения — моды `type: addon`.

## Статус реализации в MUD

Карточки `docs/rules/` **не** содержат `mud_status`. Ниже — сводка Pre-Alpha; детали UI — [`MUD_PRD.md`](MUD_PRD.md), данные — `database/`.

### Часть 1 — Персонаж

| Тема | Карточки | MUD |
|------|----------|-----|
| Введение / создание | [chapters/00](rules/chapters/00-introduction.md), [01](rules/chapters/01-character-creation.md) | Создание персонажа реализовано частично |
| Расы | [entities/races/](rules/entities/races/) (9) | Частично в YAML |
| Классы / подклассы | [entities/classes/](rules/entities/classes/) (12) | Частично в YAML; подклассы Phase 2 |
| Предыстории | [entities/backgrounds/](rules/entities/backgrounds/) (13) | Частично |
| Снаряжение | [05-equipment](rules/chapters/05-equipment.md) | Частично |
| Черты | [entities/feats/](rules/entities/feats/) | Реализованы |
| Мультикласс | [06-multiclass](rules/chapters/06-multiclass.md) | **Запрещён** |

### Часть 2 — Игровой процесс

| Тема | Карточки | MUD |
|------|----------|-----|
| Характеристики | [07-ability-scores](rules/chapters/07-ability-scores.md) | Частично |
| Приключения | [08-adventures](rules/chapters/08-adventures.md) | Запланировано |
| Сражение | [09-combat](rules/chapters/09-combat.md) | Запланировано |

### Часть 3 — Магия

| Тема | Карточки | MUD |
|------|----------|-----|
| Накладывание | [10-spellcasting](rules/chapters/10-spellcasting.md) | Запланировано |
| Заклинания | [entities/spells/](rules/entities/spells/) (~273) | Не реализовано |

Индексы заклинаний: [по уровню](rules/_index/spells/by-level.md), [по школе](rules/_index/spells/by-school.md).

### Приложения

| Раздел | Файл | Примечание |
|--------|------|------------|
| Состояния | [A-conditions](rules/reference/appendices/A-conditions.md) | Механика |
| Параметры существ | [D-creatures](rules/reference/appendices/D-creatures.md) | Краткие статблоки |
| Боги / планы / литература | stubs в `reference/appendices/` | Лор исключён |
| Словари | [glossaries/](rules/reference/glossaries/) | EN↔RU |

## Глоссарий (краткий)

Полный словарь — [`rules/reference/glossaries/`](rules/reference/glossaries/). Ключи в коде — английские; в UI — через `database/strings/`.
