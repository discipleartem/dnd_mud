---
phb_chapter: 1
phb_section: Создание персонажа
phb_pages:
- 11
- 16
phb_part: 1
id: 01-character-creation
tags:
- chapter
mud_status: implemented
type: chapter
---

# Глава 1: Создание персонажа

> Источник: PHB, стр. 11–16. Порядок создания и методы характеристик.

## Правила (PHB)

<!-- phb:auto:summary -->
### Шаги PHB

1. Выбор расы и подрасы.
2. Выбор класса.
3. Определение значений характеристик.
4. Описание персонажа (имя, внешность — ролевой слой, не механика).
5. Выбор предыстории.
6. Снаряжение (класс + предыстория).

### Характеристики

- **Стандартный массив:** 15, 14, 13, 12, 10, 8.
- **Распределение очков:** бюджет 27 (стоимость значений 8–15 по таблице PHB).
- **Случайный:** 4d6, отбросить низший, шесть раз; распределить по характеристикам.
- Расовые бонусы применяются после распределения.

### Ссылки

- Расы: [02-races.md](02-races.md) · Классы: [03-classes.md](03-classes.md) · Предыстории: [04-backgrounds.md](04-backgrounds.md).
<!-- /phb:auto:summary -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | Реализовано: сложность → имя → раса → подраса → характеристики → **предыстория** → **языки** → класс → подкласс → (**черты**, если раса даёт слот) → **владения** → **навыки** → (компетентность?) → **снаряжение** → сохранение |
| YAML | [`database/races/races.yaml`](../../database/races/races.yaml), [`database/classes/classes.yaml`](../../database/classes/classes.yaml), [`database/core/languages.yaml`](../../database/core/languages.yaml), [`database/backgrounds/backgrounds.yaml`](../../database/backgrounds/backgrounds.yaml), [`database/progression/feats.yaml`](../../database/progression/feats.yaml), [`database/equipment/`](../../database/equipment/) |
| Core | [`core/character_storage.py`](../../core/character_storage.py), [`core/character_builder.py`](../../core/character_builder.py), [`core/stats.py`](../../core/stats.py), [`core/races.py`](../../core/races.py), [`core/classes.py`](../../core/classes.py), [`core/languages.py`](../../core/languages.py), [`core/backgrounds.py`](../../core/backgrounds.py), [`core/subclasses.py`](../../core/subclasses.py), [`core/skills.py`](../../core/skills.py), [`core/proficiencies.py`](../../core/proficiencies.py), [`core/progression.py`](../../core/progression.py), [`core/feats.py`](../../core/feats.py), [`core/asi.py`](../../core/asi.py), [`core/checks.py`](../../core/checks.py), [`core/inventory.py`](../../core/inventory.py), [`core/starting_equipment.py`](../../core/starting_equipment.py) |
| UI | [`ui/menus/_creation_steps.py`](../../ui/menus/_creation_steps.py), [`ui/menus/_creation_handlers.py`](../../ui/menus/_creation_handlers.py), [`ui/menus/_selectors.py`](../../ui/menus/_selectors.py), [`ui/menus/feats/`](../../ui/menus/feats/), [`ui/menus/languages.py`](../../ui/menus/languages.py), [`ui/menus/backgrounds.py`](../../ui/menus/backgrounds.py), [`ui/menus/proficiencies.py`](../../ui/menus/proficiencies.py), [`ui/menus/skills.py`](../../ui/menus/skills.py), [`ui/menus/equipment.py`](../../ui/menus/equipment.py), [`ui/menus/asi.py`](../../ui/menus/asi.py), [`ui/menus/stats/`](../../ui/menus/stats/), [`ui/menus/settings.py`](../../ui/menus/settings.py), [`ui/menus/subclass_trainer.py`](../../ui/menus/subclass_trainer.py) |
| Режимы | Normal / Easy: 3 метода + confirm; HardCore: `_select_stats_random_hardcore` |
| Заметки | Снаряжение предыстории мержится в инвентарь в `save_character` (`get_background_equipment_items`); **мультикласс запрещён**; языки: common по умолчанию, exotic — только при явном `pool` в YAML; владения инструментов с `choice: true` — только через шаг выбора (см. [05-equipment.md](05-equipment.md)) |

### Сохранение персонажа

Путь: `saves/characters/{save_slug}.json`. Поля модели `Character` совпадают с ключами JSON: `name`, `race`, `class_id`, `level`, `stats`, `current_hp`, `max_hp`, `experience`, `difficulty`, `subrace`, `subclass_id`, `languages`, `background_id`, `skills`, `save_proficiencies`, `inventory`, `equipped`, `equipment_choices`, … См. [`DATA_SCHEMA.md`](../../DATA_SCHEMA.md) §Save JSON.

### Константы генерации (`core/stats.py`)

```python
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
POINT_BUY_BUDGET = 27
POINT_BUY_COSTS = {8: 0, 9: 1, ..., 15: 9}
ABILITY_SCORE_MAX = 20
```

### Не реализовано из главы 1

- Быстрое создание (готовые наборы класса)
- Применение умений класса/подкласса в бою
<!-- /mud:implementation -->
