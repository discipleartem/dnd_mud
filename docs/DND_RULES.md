# Правила D&D 5e — справочник dnd_mud

Справочник механики **Dungeons & Dragons 5-й редакции** (PHB **2014**, перевод PHantom 2016). Карточки — [`rules/`](rules/) (только механика, без лора). **Статус реализации в MUD** описан ниже и в `database/`.

Индекс документации — [`README.md`](README.md). Guide для агентов — [`rules/README.md`](rules/README.md).

## Источник и авторские права

| Параметр | Значение |
|----------|----------|
| Канон | Player's Handbook **2014** (рус. перевод PHantom, 2016); не редакция 2024 |
| Машиночитаемый индекс | [`rules/_index/lookup.yaml`](rules/_index/lookup.yaml) |
| Терминология RU↔EN | [`rules/reference/glossaries/`](rules/reference/glossaries/) (заполняется в reference-part) |

### Алгоритм поиска правил

| Шаг | Источник | Действие |
|-----|----------|----------|
| 1 | [`docs/rules/`](rules/) | [`lookup.yaml`](rules/_index/lookup.yaml) (`by_alias` / `by_id` → `quick`, `file`) |
| 2 | Интернет | D&D **5e до редакции 2024** (PHB 2014 / SRD 5.1) |

**При расхождении:** официальные правила 5e до 2024 > пересказ в `docs/rules/`. Текст в `docs/rules/` — **пересказ механики**, не дословная копия. Материалы D&D © Wizards of the Coast.

## Статус реализации в MUD (кратко)

Подробное оглавление PHB и таблицы статусов обновляются после наполнения `rules/` (character / play / magic / reference parts). Текущий Pre-Alpha: создание персонажа, частичные каталоги рас/классов/предысторий/черт в `database/`; бой и заклинания — запланированы. См. [`MUD_PRD.md`](MUD_PRD.md).

## Политика каталога ядра

В `database/races/races.yaml` и `database/classes/classes.yaml` допускаются **только** официальные расы/подрасы и классы/подклассы из PHB 2014. Расширения — моды `type: addon`.
