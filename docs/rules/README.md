# Справочник правил — guide для агентов и игроков

**Layout:** `agent-v2` · **Канон:** PHB **2014** (PHantom 2016). Локальный PDF не коммитится.

| Аудитория | Точка входа |
|-----------|-------------|
| Человек / игрок | [`INDEX.md`](INDEX.md) — оглавление по главам |
| Агент | [`_index/lookup.yaml`](_index/lookup.yaml) — поиск по имени |
| Статус MUD | [`../DND_RULES.md`](../DND_RULES.md) |

## Политика контента

**Только механика** — без лора, флавора, идеалов и дословных цитат PHB.

| Включать | Исключать |
|----------|-----------|
| Числа, таблицы, условия, действия | Культура, внешность, «характер расы» |
| Владения, сопротивления, эффекты | Идеалы, привязанности, примеры NPC |
| Параметры и эффекты заклинаний | Поэтические вступления |

## Алгоритм агента (обязательный)

1. [`lookup.yaml`](_index/lookup.yaml) → `by_alias` (RU/EN/slug, регистр не важен) → `id`
2. `by_id[id].quick` — ответ без открытия файла, если хватает
3. Иначе открыть `by_id[id].file`
4. Нет / неполно → веб PHB 2014 / SRD 5.1 → обновить карточку + `quick` + `lookup.yaml`

**Не использовать память модели.** Конфликт: официальные правила 5e до 2024 > этот каталог.

## Индексы

| Файл | Зачем |
|------|-------|
| [`lookup.yaml`](_index/lookup.yaml) | Единый SoT: `by_id`, `by_alias`, `summaries` (`quick`) |
| [`toc.yaml`](toc.yaml) | Полный каталог `id → file/pages` |
| [`entities.yaml`](_index/entities.yaml) | Всё кроме заклинаний |
| [`spells.yaml`](_index/spells.yaml) | Заклинания + `level` / `school` |
| [by-level](_index/spells/by-level.md) / [by-school](_index/spells/by-school.md) | Обзор для людей |

## Структура файла

```yaml
---
id: fighter
type: class          # chapter|race|class|background|feat|spell|appendix|glossary
phb_pages: [70, 75]
quick: "одна строка механики для lookup"
aliases: [fighter, Воин, воин]
# spell: level, school, casting_time, range, components, duration
---
```

- Главы / расы / классы: секции механики списками
- Заклинания: `## Параметры` → `## Эффект` → опционально `## На больших уровнях`
- `quick` обязателен; для заклинаний — уровень, школа, дистанция, ключ эффекта (урон/сейв)

## Обновление

1. Механика из PHB 2014 / SRD 5.1 (или локальный PDF).
2. Пересказ в markdown + актуальный `quick` / `aliases`.
3. Записи в `toc.yaml`, `_index/*.yaml`, `lookup.yaml` (вручную, без генераторов).
4. Шаблон: [`_templates/frontmatter-template.md`](_templates/frontmatter-template.md).
