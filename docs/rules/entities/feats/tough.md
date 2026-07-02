---
phb_chapter: 6
phb_section: Крепкий
phb_pages:
- 166
- 172
phb_part: 1
id: tough
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#tough
quick: Максимум хитов +2× уровень при взятии; +2 за каждый последующий уровень.
---

# Крепкий

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | — |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Максимум ваших хитов увеличивается на количество, равное удвоенному уровню, на котором берётся эта черта. Каждый раз, когда вы впоследствии будете получать уровень, максимум ваших хитов будет дополнительно увеличиваться на 2.
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#tough` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
