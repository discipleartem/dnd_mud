---
phb_chapter: 0
phb_section: "Название раздела"
phb_pages: [0, 0]
phb_part: 1
id: example_id
type: chapter
tags: []
mud_status: n/a
mud_refs: {}
quick: "Краткая механика в 1–2 предложения (для lookup.yaml; без флавора)"
---

# Заголовок (RU)

> Источник: PHB, стр. N–M. Пересказ правил, не дословная копия PHB. © Wizards of the Coast.

## Правила (PHB)

<!-- phb:auto:summary -->
(пересказ **механики** из PHB PDF — без лора; обновляет агент)
<!-- /phb:auto:summary -->

## Реализация в MUD

<!-- mud:implementation -->
(опционально: статус реализации, ссылки на YAML/core; не противоречит PHB)
<!-- /mud:implementation -->

---

**Заклинание:** вместо `## Правила (PHB)` — секции `## Параметры`, `## Эффект`, опционально `## На больших уровнях` с блоками `phb:auto:parameters`, `phb:auto:effect`, `phb:auto:higher-levels`.

**Черта:** секции `## Параметры` (`phb:auto:parameters`) и `## Эффект` (`phb:auto:effect`).

После создания файла — запись в `toc.yaml` и `_index/*.yaml`, затем `python scripts/build_rules_index.py`.
