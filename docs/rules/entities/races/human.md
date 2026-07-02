---
phb_chapter: 2
phb_section: Человек
phb_pages:
- 29
- 31
phb_part: 1
id: human
type: race
tags:
- race
mud_status: partial
quick: 'Стандарт: все характеристики +1; вариант: +1 к двум, навык, черта, язык'
mud_refs:
  yaml: database/races/races.yaml#human
---

# Человек

> Источник: PHB, стр. 29–31. Только механика.

## Правила (PHB)

<!-- phb:auto:summary -->
### Стандартный человек

- Все характеристики +1.
- Размер: Средний; скорость 30 футов.
- Языки: общий + один на выбор.

### Вариант человека (опциональное правило PHB)

- +1 к двум разным характеристикам на выбор.
- Владение одним навыком на выбор.
- Одна черта на выбор (требования черты должны выполняться).
- Один дополнительный язык.
<!-- /phb:auto:summary -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/races/races.yaml#human` |
| Core | `core/races.py` |
<!-- /mud:implementation -->
