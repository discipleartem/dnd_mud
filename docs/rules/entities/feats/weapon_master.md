---
phb_chapter: 6
phb_section: Мастер оружия
phb_pages:
- 166
- 172
phb_part: 1
id: weapon_master
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#weapon_master
quick: Сила или Ловкость +1; владение четырьмя видами простого или воинского оружия.
---

# Мастер оружия

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | — |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Вы знаете как пользоваться множеством видов оружия и получаете следующие преимущества:
- Увеличьте значение Силы или Ловкости на 1, при максимуме 20.
- Вы получаете владение четырьмя выбранными видами оружия. Выбранное оружие должно быть или простым или воинским.
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#weapon_master` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
