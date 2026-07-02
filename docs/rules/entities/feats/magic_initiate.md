---
phb_chapter: 6
phb_section: Посвящённый в магию
phb_pages:
- 166
- 172
phb_part: 1
id: magic_initiate
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#magic_initiate
quick: Два заговора и одно заклинание 1 уровня от выбранного класса; 1/продолжительный
  отдых.
---

# Посвящённый в магию

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | — |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Выберите класс: бард, волшебник, друид, жрец, колдун или чародей. Вы узнаёте два заговора на свой выбор из списка заклинаний этого класса.
- Кроме того, выберите одно заклинание 1 уровня из этого же списка. Вы узнаёте это заклинание и можете накладывать его на минимально возможном уровне. После использования заклинания вы должны закончить продолжительный отдых, прежде чем сможете снова использовать его этой чертой.
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#magic_initiate` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
