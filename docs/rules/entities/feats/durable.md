---
phb_chapter: 6
phb_section: Стойкий
phb_pages:
- 166
- 172
phb_part: 1
id: durable
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#durable
quick: Телосложение +1; минимум восстановления по Кости Хитов — удвоенный модификатор
  Телосложения (мин. 2).
---

# Стойкий

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | — |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Вы стойкий и живучий, и получаете следующие преимущества:
- Увеличьте значение Телосложения на 1, при максимуме 20.
- Когда вы бросаете Кость Хитов для восстановления хитов, минимум равен удвоенному модификатору Телосложения (минимум 2).
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#durable` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
