---
phb_chapter: 4
phb_section: Личность и предыстория
phb_pages:
- 121
- 142
phb_part: 1
id: 04-backgrounds
tags:
- chapter
mud_status: partial
type: chapter
---

# Личность и предыстория

> Источник: PHB, стр. 121–142. Индекс предысторий.

<!-- phb:auto:links -->
## Детальные карточки

| ID | Название | Файл | Статус MUD |
|----|----------|------|------------|
| `acolyte` | Прислужник | [acolyte.md](entities/backgrounds/acolyte.md) | partial |
| `charlatan` | Шарлатан | [charlatan.md](entities/backgrounds/charlatan.md) | partial |
| `criminal` | Преступник | [criminal.md](entities/backgrounds/criminal.md) | partial |
| `entertainer` | Артист | [entertainer.md](entities/backgrounds/entertainer.md) | partial |
| `folk_hero` | Народный герой | [folk_hero.md](entities/backgrounds/folk_hero.md) | partial |
| `guild_artisan` | Гильдейский ремесленник | [guild_artisan.md](entities/backgrounds/guild_artisan.md) | partial |
| `hermit` | Отшельник | [hermit.md](entities/backgrounds/hermit.md) | partial |
| `noble` | Благородный | [noble.md](entities/backgrounds/noble.md) | partial |
| `outlander` | Чужеземец | [outlander.md](entities/backgrounds/outlander.md) | partial |
| `sage` | Мудрец | [sage.md](entities/backgrounds/sage.md) | partial |
| `sailor` | Моряк | [sailor.md](entities/backgrounds/sailor.md) | partial |
| `soldier` | Солдат | [soldier.md](entities/backgrounds/soldier.md) | partial |
| `urchin` | Беспризорник | [urchin.md](entities/backgrounds/urchin.md) | partial |
<!-- /phb:auto:links -->

## Правила (PHB)

<!-- phb:auto:summary -->
### Предыстории PHB

- Каждая предыстория: владение навыками, языками/инструментами, стартовое снаряжение и умение (feature).
- Детали — в карточках `entities/backgrounds/` (таблица ниже).

### Не в справочнике (ролевой отыгрыш)

- Таблицы черт личности, идеалов, привязанностей, слабостей и правило «Вдохновение» — для DM; в MUD не реализованы.
<!-- /phb:auto:summary -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | **Частично** — выбор предыстории, навыки, языки, **стартовое снаряжение в инвентаре**; personality/inspiration/feature runtime — Phase 2 |
| YAML | [`database/backgrounds/backgrounds.yaml`](../../database/backgrounds/backgrounds.yaml) |
| Core | [`core/backgrounds.py`](../../core/backgrounds.py) |
| UI | [`ui/menus/backgrounds.py`](../../ui/menus/backgrounds.py) |
| Flow | После **характеристик**, до **класса**; языки — отдельный шаг после предыстории |

### YAML-схема

Канон: [`docs/DATA_SCHEMA.md`](../DATA_SCHEMA.md). Механика — только в `grants[]`.

```yaml
backgrounds:
  acolyte:
    name: { ru: "...", en: "..." }
    description: { ru: "...", en: "..." }
    grants:
      - type: skill_proficiency
        skills: [insight, religion]
      - type: language
        count: 2
        choice: true
        pool: common
      - type: equipment_item
        items:
          - { kind: equipment, id: emblem, qty: 1 }
    inventory_tool_pools:   # опционально: picks → инвентарь PHB
      - musical_instruments
    equipment: { ru: [...], en: [...] }   # flavor для UI; предметы — в equipment_item
    feature:   # flavor; не game engine
      name: { ru: "...", en: "..." }
      description: { ru: "...", en: "..." }
```

- `language` grant, поле `pool`: `common` (по умолчанию), `exotic` или `any` — см. [`database/core/languages.yaml`](../../database/core/languages.yaml).
- **Экзотические языки** доступны для выбора только при `pool: exotic` / `pool: any`.

### Модель и сохранение

- `Character.background_id` в JSON сейва.
- Навыки предыстории входят в `Character.skills` с источником `background` при выборе классовых навыков.
- Стартовое снаряжение: grant `equipment_item` + picks из `inventory_tool_pools` → `core/backgrounds.get_background_equipment_items`, merge в `save_character`.

### Не реализовано

- Таблицы personality (черты, идеалы, привязанности, изъяны) и Inspiration.
- Механика background feature в engine.
<!-- /mud:implementation -->
