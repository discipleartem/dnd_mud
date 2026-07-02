---
phb_chapter: 0
phb_section: Введение
phb_pages:
- 5
- 9
phb_part: 0
id: 00-introduction
tags:
- chapter
mud_status: partial
type: chapter
---

# Введение

> Источник: PHB, стр. 5–9. Механика кубов и структура игры.

## Правила (PHB)

<!-- phb:auto:summary -->
### Роль кубов

- Для исходов с риском неудачи — бросок d20 + модификаторы против Сл.
- Преимущество / помеха: два d20, лучший / худший.
- Другие кости — урон, исцеление, случайные таблицы.

### Структура игры

- Мастер описывает ситуацию; игроки объявляют действия персонажей.
- Три типа активности: **исследование** (проверки, перемещение), **социальное взаимодействие** (проверки Харизмы и др.), **сражение** (инициатива, раунды, действия).
- Подробнее: [07-ability-scores.md](07-ability-scores.md), [09-combat.md](09-combat.md).

### Не в справочнике

- Советы по отыгрышу, примеры NPC и атмосферные описания — в PDF PHB.
<!-- /phb:auto:summary -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | Частично: генерация костей; **спасброски при создании** (`core/checks.py`); проверки навыков и атаки в engine — Phase 2 |
| YAML | — |
| Core | [`core/dice.py`](../../core/dice.py): `roll()`, `roll_ability_score()`, `ability_modifier()`; [`core/checks.py`](../../core/checks.py): `saving_throw`, `saving_throw_modifier` |
| Режимы | Одинаковые формулы кубов; режим влияет на контент и строгость engine (Phase 2) |
| Заметки | Проверки характеристик и атаки — Phase 2; спасброски — см. [07-ability-scores.md](07-ability-scores.md), бой — [09-combat.md](09-combat.md) |

### Реализованные функции кубов

```python
roll(count=1, sides=20, modifier=0)      # общий бросок
roll_ability_score()                        # 4к6, отбросить наименьший
ability_modifier(score)                     # (score - 10) // 2
```

Тесты: `tests/test_dice.py`.
<!-- /mud:implementation -->
