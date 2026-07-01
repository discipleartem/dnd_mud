# Глава 4: Личность и предыстория

> Источник: PHB, стр. 121–142. Полный текст — `docs/PHB_ D&D_2023 RUS.pdf` (локально).

## Для игроков

### Описание персонажа

Помимо статистики, персонаж имеет **личность**: черты характера, идеалы, привязанности, изъяны. Это ролевые зацепки, не числа на листе.

### Вдохновение

За отыгрыш личности Мастер может дать **вдохновение** — один раз получить преимущество на проверку, связанную с чертой/идеалом/привязанностью.

### Предыстории (background)

Предыстория дополняет прошлое персонажа и даёт:
- владение **двумя навыками**;
- владение **инструментами или языками**;
- **снаряжение**;
- особенность предыстории (например, «Приют для верующих» у прислужника).

13 предысторий PHB: прислужник, шарлатан, преступник, артист, народный герой, гильдейский ремесленник, отшельник, благородный, чужеземец, мудрец, моряк, солдат, беспризорник.

## Для разработчиков

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
