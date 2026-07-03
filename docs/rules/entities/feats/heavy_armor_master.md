---
phb_chapter: 6
phb_section: Мастер тяжёлых доспехов
phb_pages:
- 166
- 172
phb_part: 1
id: heavy_armor_master
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#heavy_armor_master
quick: Сила +1; в тяжёлом доспехе немагический физический урон снижается на 3.
---

# Мастер тяжёлых доспехов

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | владение heavy доспехами |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Вы можете своим доспехом отклонять удары, которые других убили бы. Вы получаете следующие преимущества:
- Увеличьте значение Силы на 1, при максимуме 20.
- Если вы носите тяжёлый доспех, дробящий, колющий и рубящий урон, получаемый вами от немагического оружия, уменьшается на 3.
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#heavy_armor_master` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
