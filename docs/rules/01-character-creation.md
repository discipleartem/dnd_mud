# Глава 1: Создание персонажа

> Источник: PHB, стр. 11–16. Полный текст — `docs/PHB_ D&D_2023 RUS.pdf` (локально).

## Для игроков

### Шаги по PHB

1. **Раса** — внешность, расовые особенности, бонусы к характеристикам.
2. **Класс** — призвание, кость хитов, владения, классовые умения.
3. **Значения характеристик** — шесть чисел (Сила … Харизма).
4. **Описание** — имя, внешность, личность, предыстория.
5. **Снаряжение** — из класса и предыстории.
6. **Группа** — связь с другими персонажами (в MUD — одиночная игра).

### Уровень и опыт

- Старт обычно с **1 уровня**, 0 опыта; режим **Лёгкая** (`easy`) — с **3 уровня**.
- Повышение уровня — по таблице опыта PHB (уровни **1–10** в MUD); см. `core/progression.py`.
- Потолок уровня в игре: **10** (`MAX_CHARACTER_LEVEL`).

### Хиты на 1 уровне (Normal / Easy)

```
максимум хитов = максимум кости хитов класса + модификатор Телосложения
```

Пример: воин (к10), Телосложение 14 (+2) → 10 + 2 = **12 HP**. Минимум на 1 уровне — **1 HP** (`max(1, …)`).

### Хиты в HardCore

На **каждом** уровне (включая 1-й): бросок кости хитов класса + модификатор Телосложения. На 1 уровне **без** нижней границы `max(1, …)` — возможны отрицательные итоги при низком Телосложении.

При повышении уровня прирост фиксируется в `max_hp` и не пересчитывается задним числом.

Текущие хиты не могут превышать максимум без особых эффектов (`max_hp` в модели `Character`).

### Бонус мастерства

На 1 уровне **+2**. Добавляется к броскам, где есть владение (навык, спасбросок, атака оружием).

### Методы генерации характеристик (PHB)

| Метод | Описание |
|-------|----------|
| Стандартный массив | Распределить `[15, 14, 13, 12, 10, 8]` по шести характеристикам |
| Покупка очков | Старт с 8; бюджет **27 очков**; значения 8–15 по таблице стоимости |
| Случайный | Шесть раз 4к6, отбросить наименьший куб в каждом броске |

**Расовые бонусы** применяются после распределения базовых значений.

#### Таблица стоимости point-buy

| Значение | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|----------|---|---|----|----|----|----|----|-----|
| Стоимость | 0 | 1 | 2 | 3 | 4 | 5 | 7 | 9 |

### Порядок характеристик в MUD

Сила → Ловкость → Телосложение → Интеллект → Мудрость → Харизма (`STAT_NAMES` в `core/stats.py`).

### Режимы создания в dnd_mud

| Режим | Генерация характеристик | Подтверждение | Старт / подкласс |
|-------|-------------------------|---------------|------------------|
| Normal | Выбор метода: массив / point-buy / 4d6 | Принять или переквалификация | 1 ур.; подкласс обязателен |
| HardCore | Авто: по одному 4d6 на характеристику по порядку | Без переквалификации | 1 ур.; подкласс только при `subclass_choice_level ≤ 1` |
| Easy | Как Normal | Как Normal | **3 ур.**; подкласс обязателен |

Сложность (`Character.difficulty`) выбирается **до** имени и сохраняется в JSON персонажа.

## Для разработчиков

| Аспект | Значение |
|--------|----------|
| Статус | Реализовано: сложность → имя → раса → подраса → характеристики → **предыстория** → **языки** → класс → подкласс → (**черты**, если раса даёт слот) → **владения** → **навыки** → (компетентность?) → сохранение |
| YAML | [`database/races/races.yaml`](../../database/races/races.yaml), [`database/classes/classes.yaml`](../../database/classes/classes.yaml), [`database/core/languages.yaml`](../../database/core/languages.yaml), [`database/backgrounds/backgrounds.yaml`](../../database/backgrounds/backgrounds.yaml), [`database/progression/feats.yaml`](../../database/progression/feats.yaml) |
| Core | [`core/character_storage.py`](../../core/character_storage.py), [`core/character_builder.py`](../../core/character_builder.py), [`core/stats.py`](../../core/stats.py), [`core/races.py`](../../core/races.py), [`core/classes.py`](../../core/classes.py), [`core/languages.py`](../../core/languages.py), [`core/backgrounds.py`](../../core/backgrounds.py), [`core/subclasses.py`](../../core/subclasses.py), [`core/skills.py`](../../core/skills.py), [`core/proficiencies.py`](../../core/proficiencies.py), [`core/progression.py`](../../core/progression.py), [`core/feats.py`](../../core/feats.py), [`core/asi.py`](../../core/asi.py) |
| UI | [`ui/menus/_creation_steps.py`](../../ui/menus/_creation_steps.py), [`ui/menus/_creation_handlers.py`](../../ui/menus/_creation_handlers.py), [`ui/menus/_selectors.py`](../../ui/menus/_selectors.py), [`ui/menus/feats/`](../../ui/menus/feats/), [`ui/menus/languages.py`](../../ui/menus/languages.py), [`ui/menus/backgrounds.py`](../../ui/menus/backgrounds.py), [`ui/menus/proficiencies.py`](../../ui/menus/proficiencies.py), [`ui/menus/skills.py`](../../ui/menus/skills.py), [`ui/menus/asi.py`](../../ui/menus/asi.py), [`ui/menus/stats/`](../../ui/menus/stats/), [`ui/menus/settings.py`](../../ui/menus/settings.py), [`ui/menus/subclass_trainer.py`](../../ui/menus/subclass_trainer.py) |
| Режимы | Normal / Easy: 3 метода + confirm; HardCore: `_select_stats_random_hardcore` |
| Заметки | Снаряжение предыстории — не в flow; **мультикласс запрещён**; языки: common по умолчанию, exotic — только при явном `pool` в YAML; владения инструментов с `choice: true` — только через шаг выбора (см. [05-equipment.md](05-equipment.md)) |

### Сохранение персонажа

Путь: `saves/characters/{save_slug}.json`. Поля модели `Character` совпадают с ключами JSON: `name`, `race`, `class_id`, `level`, `stats`, `current_hp`, `max_hp`, `experience`, `difficulty`, `subrace`, `subclass_id`, `languages`, `background_id`, …

### Константы генерации (`core/stats.py`)

```python
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
POINT_BUY_BUDGET = 27
POINT_BUY_COSTS = {8: 0, 9: 1, ..., 15: 9}
ABILITY_SCORE_MAX = 20
```

### Не реализовано из главы 1

- Быстрое создание (готовые наборы класса)
- Стартовое снаряжение из класса и предыстории
- Применение умений класса/подкласса в бою
