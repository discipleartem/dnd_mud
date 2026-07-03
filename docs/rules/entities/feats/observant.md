---
phb_chapter: 6
phb_section: Внимательный
phb_pages:
- 166
- 172
phb_part: 1
id: observant
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#observant
quick: Интеллект или Мудрость +1; чтение по губам; +5 к пассивным Внимательности и
  Анализу.
---

# Внимательный

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | — |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Вы быстро улавливаете мелкие подробности и получаете следующие преимущества:
- Увеличьте значение Интеллекта или Мудрости на 1, при максимуме 20.
- Если вы видите рот существа, когда оно говорит на языке, который вы понимаете, вы можете прочитать по его губам, что оно говорит.
- Вы получаете бонус +5 к пассивной проверке Мудрости (Внимательность) и пассивной проверке Интеллекта (Анализ).
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#observant` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
