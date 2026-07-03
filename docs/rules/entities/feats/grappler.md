---
phb_chapter: 6
phb_section: Борец
phb_pages:
- 166
- 172
phb_part: 1
id: grappler
tags:
- feat
mud_status: partial
type: feat
mud_refs:
  yaml: database/progression/feats.yaml#grappler
quick: Преимущество на атаки по захваченным; действием — сковать захваченное существо.
---

# Борец

> Источник: PHB, гл. 6. Пересказ из feats.yaml / PHB PDF.

## Параметры

<!-- phb:auto:parameters -->
| Параметр | Значение |
|----------|----------|
| Требование | Сила 13+ |
<!-- /phb:auto:parameters -->

## Эффект

<!-- phb:auto:effect -->
- Вы развили навыки, нужные для тесного захвата противников. Вы получаете следующие преимущества:
- Вы совершаете с преимуществом броски атаки по существу, которое держите в захвате.
- Вы можете действием попытаться скрутить захваченное вами существо. Для этого совершите ещё одну проверку захвата. В случае успеха и вы и это существо становитесь опутанными до окончания захвата.
<!-- /phb:auto:effect -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml#grappler` |
| Core | `core/feats.py` |
<!-- /mud:implementation -->
