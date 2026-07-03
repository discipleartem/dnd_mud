---
phb_chapter: 6
phb_section: Атлетичный
phb_pages:
- 166
- 172
phb_part: 1
id: athlete
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#athlete
quick: Сила или Ловкость +1; вставание с 5 фт.; лазание без штрафа; прыжок с разбега
  5 фт.
---

# Атлетичный

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | — |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Увеличьте значение Силы или Ловкости на 1, при максимуме 20.
- Если вы лежите ничком, вставание использует только 5 футов перемещения.
- Лазание не заставляет вас тратить дополнительное перемещение.
- Вы можете совершать прыжок в длину или высоту с разбега, переместившись только на 5 футов, а не на 10.
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#athlete` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
