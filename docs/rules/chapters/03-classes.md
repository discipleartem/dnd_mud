---
phb_chapter: 3
phb_section: Классы
phb_pages:
- 45
- 120
phb_part: 1
id: 03-classes
tags:
- chapter
mud_status: partial
type: chapter
---

# Классы

> Источник: PHB, стр. 45–120. Индекс классов.

<!-- phb:auto:links -->
## Детальные карточки

| ID | Название | Файл | Статус MUD |
|----|----------|------|------------|
| `barbarian` | Варвар | [barbarian.md](entities/classes/barbarian.md) | planned |
| `bard` | Бард | [bard.md](entities/classes/bard.md) | partial |
| `cleric` | Жрец | [cleric.md](entities/classes/cleric.md) | partial |
| `druid` | Друид | [druid.md](entities/classes/druid.md) | planned |
| `fighter` | Воин | [fighter.md](entities/classes/fighter.md) | partial |
| `monk` | Монах | [monk.md](entities/classes/monk.md) | planned |
| `paladin` | Паладин | [paladin.md](entities/classes/paladin.md) | planned |
| `ranger` | Следопыт | [ranger.md](entities/classes/ranger.md) | planned |
| `rogue` | Плут | [rogue.md](entities/classes/rogue.md) | partial |
| `sorcerer` | Чародей | [sorcerer.md](entities/classes/sorcerer.md) | planned |
| `warlock` | Колдун | [warlock.md](entities/classes/warlock.md) | planned |
| `wizard` | Волшебник | [wizard.md](entities/classes/wizard.md) | planned |
<!-- /phb:auto:links -->

## Правила (PHB)

<!-- phb:auto:summary -->
### Общие правила

- Класс задаёт кость хитов, владения, спасброски, умения по уровням и момент выбора подкласса (обычно 3 ур.).
- Мультиклассирование — опциональное правило PHB (см. [06-multiclass.md](06-multiclass.md)); в MUD **запрещено**.
- Механика каждого класса — в карточках `entities/classes/` (таблица ниже).
<!-- /phb:auto:summary -->

## Реализация в MUD

<!-- mud:implementation -->
### Политика каталога (PHB)

**В ядре допускаются только официальные классы и подклассы из** [`docs/PHB_ D&D_2023 RUS.pdf`](../PHB_%20D%26D_2023%20RUS.pdf) **(глава 3).** Канон — [`database/classes/classes.yaml`](../../database/classes/classes.yaml). Классы и подклассы вне PHB — только через моды `type: addon`.

| Аспект | Значение |
|--------|----------|
| Статус | Частично: 4 класса в YAML; выбор класса в UI; HP по режиму сложности; **спасброски и стартовое снаряжение** при создании |
| YAML | [`database/classes/classes.yaml`](../../database/classes/classes.yaml) |
| Core | [`core/classes.py`](../../core/classes.py): `load_classes()`, `get_class_hit_dice()` |
| UI | [`ui/menus/_selectors.py`](../../ui/menus/_selectors.py) — `select_class` |
| Режимы | Класс не зависит от режима сложности |
| Заметки | `features` и `subclasses` в YAML — справочные; runtime не применяет умения. **Мультикласс запрещён** — один класс на персонажа (см. [chapters/06-multiclass.md](chapters/06-multiclass.md)). **Подклассы:** реализуем только перечисленные в YAML (см. [chapters/03-subclasses.md](chapters/03-subclasses.md) §Политика MUD) |

### Классы в MUD (текущий каталог)

| ID | PHB | hit_dice в YAML |
|----|-----|-----------------|
| `fighter` | Воин | 10 |
| `rogue` | Плут | 8 |
| `cleric` | Жрец | 8 |
| `bard` | Бард | 8 |

Остальные 8 классов PHB — расширение каталога или моды.

### Расчёт HP

```python
# core/progression.py
max_hp_for_level(class_id, stats, level, difficulty)
```

- **Normal / Easy:** 1 ур. — `max(1, hit_dice + CON)`; 2+ — `(hit_dice // 2 + 1) + CON` за каждый уровень.
- **HardCore:** на каждом уровне — `max(1, roll(1, hit_dice) + CON)`; расовые/чертовые бонусы сверху.
- При левелапе HardCore прирост **добавляется** к текущему `max_hp` (`apply_experience`), не пересчитывается по среднему.

### Формат YAML (фрагмент)

```yaml
classes:
  fighter:
    hit_dice: 10
    prime_ability: strength
    saving_throws: [strength, constitution]
    starting_equipment:
      choices: [...]
      fixed: [...]
    features: [...]
    subclasses: [...]
```

### Не реализовано

- Применение `features` в бою и сценариях (ячейки заклинаний, пассивные умения)

Выбор навыков и владений при создании — **реализовано** (`_creation_steps`, `proficiencies.py`, `skills.py`).  
**Спасброски и стартовое снаряжение класса** — **реализовано** (`core/checks.py`, `core/starting_equipment.py`, `core/inventory.py`, шаг `equipment` в flow).  
Выбор подкласса и прогрессия умений — см. [chapters/03-subclasses.md](chapters/03-subclasses.md).
<!-- /mud:implementation -->
