---
phb_chapter: 6
phb_section: Оборонительный дуэлянт
phb_pages:
- 166
- 172
phb_part: 1
id: defensive_duelist
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#defensive_duelist
quick: Реакцией добавить бонус мастерства к КД против рукопашной атаки с фехтовальным
  оружием.
---

# Оборонительный дуэлянт

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | Ловкость 13+ |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Если вы используете оружие со свойством «фехтовальное», которым владеете, и другое существо попадает по вам рукопашной атакой, вы можете для этой атаки реакцией добавить бонус мастерства к КД, что потенциально может привести к промаху атаки.
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#defensive_duelist` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
