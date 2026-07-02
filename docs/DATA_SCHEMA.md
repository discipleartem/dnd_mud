# Схема YAML-справочников dnd_mud

Канон формата данных в `database/`. Источник правил — PHB (`docs/PHB_ D&D_2023 RUS.pdf`, локально). Принципы: **DRY → KISS → YAGNI**.

См. также: [`ARCHITECTURE.md`](ARCHITECTURE.md) § Data Layer, [`DEVELOPMENT.md`](DEVELOPMENT.md) § Создание мода.

## Принципы

| Принцип | Правило |
|---------|---------|
| DRY | Механика — только в `grants[]`; не дублировать в save JSON |
| KISS | ID = ключ словаря (`snake_case`, EN); монолиты PHB не дробить |
| YAGNI | Новый `type` в grants — только когда его читает runtime |

## Grants

Единый список машиночитаемых эффектов:

```yaml
grants:
  - type: skill_proficiency
    skills: [perception]
  - type: skill_proficiency
    count: 1
    choice: true
    from: all_skills
  - type: language
    count: 1
    choice: true
    pool: common
```

### Типы (runtime сейчас)

| type | Поля | Модуль |
|------|------|--------|
| `ability_increase` | `amount`, `count`, `choice`, `abilities`, `allow_duplicates` | `core/races.py`, `core/feats.py` |
| `skill_proficiency` | `skills[]` или `choice`+`from` | `core/skills.py` |
| `weapon_proficiency` | `weapons[]` | `core/proficiencies.py` |
| `armor_proficiency` | `armor[]` / `armor_types[]` | `core/proficiencies.py` |
| `tool_proficiency` | `tools[]` или `choice`+`pool` | `core/proficiencies.py` |
| `language` | `languages[]` или `choice`+`pool` | `core/backgrounds.py`, races |
| `feat` | `count`, `from` | `core/feats.py` |
| `save_proficiency` | `ability` или `choice: true` + выбор в `feat_choices` (Resilient) | `core/feat_apply.py` |
| `hit_point_bonus` | `amount`, `per_level` | `core/feats.py`, `core/races.py` |

Типы вроде `darkvision`, `resistance` — в YAML допустимы; combat engine (Phase 2) пока не читает.

Канонические поля grant — без fallback-нормализации в Python; см. [`CHANGELOG.md`](CHANGELOG.md).

## Mod overlay

[`core/catalog_loader.py`](../core/catalog_loader.py) → [`core/mod_loader.py`](../core/mod_loader.py) — `load_catalog` / `load_merged_catalog` с deep-merge overlay включённых модов. Кэш `@lru_cache` — на `load_merged_catalog`.

| Каталог | Mod overlay | Loader |
|---------|-------------|--------|
| Игровые справочники (`races`, `classes`, `backgrounds`, `feats`, `equipment`, `languages`, `abilities`, `skills`, `constants`) | ✅ | `core/catalog_loader.load_catalog` |
| Приключения, сценарии, строки UI | ❌ | `core/io.load_yaml` напрямую |

Единственный рабочий mod в репозитории: `mods/dragonborn_pack/`.

## Расы (`database/races/races.yaml`)

```yaml
races:
  human:
    name: { ru: "Человек", en: "Human" }
    description: { ru: "...", en: "..." }
    size: medium
    speed: 30
    age_range: [16, 100]
    subraces:
      standard:
        name: { ru: "Человек (стандарт)", en: "Human (standard)" }
        ability_bonuses: { strength: 1, dexterity: 1, ... }
        grants:
          - type: language
            count: 1
            choice: true
            pool: common
      variant_human:
        inherit: { ability_bonuses: false, grants: false }
        grants: [...]
```

Правила:

- **Все расы** — выбор подрасы; одна подраса → автовыбор в UI.
- Базовая раса — общие поля (`name`, `size`, `speed`, …); механика в `subraces`.
- `inherit: { ability_bonuses, grants }` — наследование grants и бонусов от базовой расы (см. §Legacy → grants).
- Saves: `race: human`, `subrace: null` → `standard` (fallback в loader).

## Предыстории (`database/backgrounds/backgrounds.yaml`)

```yaml
backgrounds:
  acolyte:
    name: { ru: "...", en: "..." }
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
          - { kind: equipment, id: book, qty: 1 }
    inventory_tool_pools:   # опционально: picks инструментов → инвентарь PHB
      - musical_instruments
    feature:   # flavor до game engine
      name: { ru: "...", en: "..." }
      description: { ru: "...", en: "..." }
```

Grant `equipment_item` — фиксированные предметы предыстории (`core/backgrounds.get_background_equipment_items`).

`inventory_tool_pools` — whitelist пулов: выбранные на шаге владений инструменты попадают в инвентарь только если id входит в разрешённый пул (например `soldier_gaming` → `dice_set` / `playing_cards`). Владение без предмета (thieves' tools у преступника) — только `tool_proficiency`, не `equipment_item`.

## Классы (`database/classes/classes.yaml`)

Помимо `features[]`, `subclasses[]`, `proficiencies`:

| Поле | Описание |
|------|----------|
| `saving_throws` | Список ability-id (`strength`, …) — два спасброска класса PHB |
| `starting_equipment` | Машиночитаемое стартовое снаряжение (см. ниже) |

### `starting_equipment`

```yaml
starting_equipment:
  choices:
    - id: armor
      options:
        - id: chain_mail
          label: { ru: "а) Кольчуга", en: "a) Chain mail" }
          items:
            - { kind: armor, id: chain_mail, qty: 1 }
          requires_armor: heavy          # опционально: подсказка в UI
        - id: martial_shield
          label: { ru: "…", en: "…" }
          items:
            - { kind: armor, id: shield, qty: 1 }
          weapon_picks:
            - pool: martial
          requires_weapon_pool: martial
  fixed:
    - { kind: equipment, id: holy_symbol, qty: 1 }
```

| Поле опции | Назначение |
|------------|------------|
| `items[]` | `{ kind, id, qty }` — `weapon`, `armor`, `tool`, `equipment` |
| `weapon_picks[]` | `{ pool }` — UI выбирает конкретное оружие из каталога |
| `tool_picks[]` | `{ pool }` — UI выбирает инструмент |
| `requires_weapon_pool` / `requires_armor` | Фильтр доступности по владениям |

Runtime: `core/starting_equipment.py` → `resolve_starting_items`; выборы игрока — `equipment_choices` на `Character`.

## Снаряжение (`database/equipment/`)

Каталог по id: `weapons.yaml`, `armor.yaml`, `tools.yaml`, `equipment.yaml`.

Наборы PHB (`category: pack`) с одноуровневым `contents[]` — при добавлении в инвентарь pack **разворачивается** (`core/inventory.expand_pack_contents`). Справочник предметов — [`rules/chapters/05-equipment-reference.md`](rules/chapters/05-equipment-reference.md).

```yaml
explorers_pack:
  name: "Набор путешественника"
  category: pack
  contents:
    - { kind: equipment, id: backpack, qty: 1 }
```

## Save JSON — поля персонажа (инвентарь и спасброски)

Опциональные ключи в `saves/characters/{save_slug}.json` (модель `Character`, `core/models.py`). Отсутствие ключа → `[]` / `{}` (обратная совместимость со старыми сейвами).

| Ключ | Тип | Описание |
|------|-----|----------|
| `save_proficiencies` | `string[]` | ability-id владения спасбросками (класс + Resilient) |
| `inventory` | `{ kind, id, qty }[]` | Стартовый и предысторический инвентарь |
| `equipped` | object | `armor`, `shield`, `main_hand`, `off_hand`, `main_hand_grip` |
| `equipment_choices` | `{ choice_id: option_id }` | Аудит выборов а/б при создании |

## Классы и черты (прочее)

- **Классы:** `features[]` с `level` — без `progression.<level>` до Phase 2; при миграции — `grants` внутри feature или параллельно.
- **Черты:** `grants[]`, `description_full` для UI PHB-текста.

## Mod overlay

```yaml
# mods/dragonborn_pack/manifest.yaml
id: dragonborn_pack
overlays:
  - target: database/races/races.yaml
    path: overlay.yaml
```

```yaml
# mods/dragonborn_pack/overlay.yaml
races:
  dragonborn:
    name: { ru: "Драконорожденный", en: "Dragonborn" }
    subraces:
      dragonborn:
        ability_bonuses: { strength: 2, charisma: 1 }
```

Включение: [`database/core/mods_state.json`](../database/core/mods_state.json). Merge: deep-merge по ключам (`core/mod_loader.py`).

## Запланировано (Phase 2+)

Правило: пункт не начинаем, пока не выполнен триггер (YAGNI).

### Сборка персонажа

**Реализовано:** `core/character_builder.py` — `ResolvedGrants`, `resolve_creation_grants`, `merge_languages_with_feats`.

| ID | Задача | Статус |
|----|--------|--------|
| `char-builder` | `core/character_builder.py`, dataclass `ResolvedGrants`, единый `resolve_creation_grants` | ✅ реализовано |

### Классы и progression

| ID | Задача | Триггер | Целевые файлы |
|----|--------|---------|---------------|
| `class-progression` | `progression.<level>.grants` вместо плоского `class_features[]` | ✅ YAML + accessor (`iter_class_grants`); авто-применение при левелапе — Phase 2 |
| `combat-usage` | Поле `usage: passive \| action \| bonus_action \| reaction` у grants/features | Реализация [`rules/chapters/09-combat.md`](rules/chapters/09-combat.md) | `database/classes/*.yaml`, combat resolver |

### Валидация и метаданные

| ID | Задача | Триггер | Целевые файлы |
|----|--------|---------|---------------|
| `json-schema` | JSON Schema в `database/schema/v1/`, pytest `tests/test_data_schema.py` | ✅ реализовано |
| `grants-yaml` | Отдельный `database/core/grants.yaml` как машиночитаемый реестр типов | Автогенерация валидатора или UI подсказок из схемы | `database/core/grants.yaml`, loader |
| `entity-metadata` | Обязательные `schema_version`, `source: phb \| mod:<id>`, `source_ref: { chapter, page }` | Несколько источников книг/DLC; аудит соответствия PHB | все `database/*/*.yaml` |

### Моды (расширение)

| ID | Задача | Триггер | Целевые файлы |
|----|--------|---------|---------------|
| `mod-deps` | `requires`, `conflicts` в manifest | Публикация 2+ зависимых модов | `core/mod_loader.py`, `mods/*/manifest.yaml` |
| `mod-delete` | action `delete` / `replace_entity` в overlay | Homebrew override официальных рас/классов | `core/mod_loader.py` |
| `mod-ui` | UI включения модов в настройках | Пользователи без ручного edit `mods_state.json` | `ui/menus/settings`, `database/core/mods_state.json` |

### Контент PHB (наполнение, не схема)

| ID | Задача | Триггер | Целевые файлы |
|----|--------|---------|---------------|
| `phb-races` | Все 9 рас и подрасы PHB в YAML | Задача наполнения из PDF гл. 2 | `database/races/races.yaml` |
| `phb-classes` | Все 12 классов и подклассы PHB | Задача наполнения из PDF гл. 3 | `database/classes/classes.yaml` |

### Локализация

| ID | Задача | Триггер | Целевые файлы |
|----|--------|---------|---------------|
| `l10n-feats-abilities` | Массовый перевод `feats.yaml`, `abilities.yaml` на `{ ru, en }` | Поддержка EN UI end-to-end | `database/progression/feats.yaml`, `database/core/abilities.yaml` |
