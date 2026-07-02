---
phb_chapter: 6
phb_section: Драчун
phb_pages:
- 166
- 172
phb_part: 1
id: tavern_brawler
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#tavern_brawler
quick: Сила или Телосложение +1; импровизированное оружие; безоружный удар к4; захват
  бонусным действием.
---

# Драчун

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | — |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Привыкнув к мордобою с использованием подручных предметов, вы получаете следующие преимущества:
- Увеличьте значение Силы или Телосложения на 1, при максимуме 20.
- Вы получаете владение импровизированным оружием.
- Ваш безоружный удар использует для урона к4.
- Если вы в свой ход попадаете по существу безоружным ударом или импровизированным оружием, вы можете бонусным действием попытаться захватить цель.
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#tavern_brawler` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
