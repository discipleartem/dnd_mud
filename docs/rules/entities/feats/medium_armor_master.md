---
phb_chapter: 6
phb_section: Мастер средних доспехов
phb_pages:
- 166
- 172
phb_part: 1
id: medium_armor_master
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#medium_armor_master
quick: Средние доспехи без помехи Скрытности; +3 к КД при Ловкости 16+.
---

# Мастер средних доспехов

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | владение medium доспехами |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Вы привыкли к перемещению в средних доспехах и получаете следующие преимущества:
- Ношение среднего доспеха не накладывает помеху к проверкам Ловкости (Скрытность).
- Когда вы носите средний доспех, вы можете добавлять к КД 3, а не 2, если ваша Ловкость 16 или выше.
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#medium_armor_master` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
