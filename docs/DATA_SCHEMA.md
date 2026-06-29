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
| `hit_point_bonus` | `amount`, `per_level` | `core/feats.py`, `core/races.py` |

Типы вроде `darkvision`, `resistance` — в YAML допустимы; combat engine (Phase 2) пока не читает.

### Legacy → grants

Loader [`core/grants.py`](../core/grants.py) принимает оба формата:

| Legacy | Grants |
|--------|--------|
| `features[].type` + `features[].mechanics` | один grant с полями mechanics + `type` |
| `type: ability_bonus` | `type: ability_increase`, `value` → `amount` |
| `backgrounds.tool_proficiencies` | `type: tool_proficiency` |
| `backgrounds.skills` | `type: skill_proficiency` |
| `backgrounds.languages` | `type: language` |

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
- `inherit` (алиас `inherit_base_bonuses` / `inherit_base_features`): наследование от базовой расы.
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
    feature:   # flavor до game engine
      name: { ru: "...", en: "..." }
      description: { ru: "...", en: "..." }
```

## Классы и черты

- **Классы:** `features[]` с `level` — без `progression.<level>` до Phase 2; при миграции — `grants` внутри feature или параллельно.
- **Черты:** `grants[]`, `description_full` для UI PHB-текста.
- **Снаряжение:** dict-by-id в `database/equipment/` — без изменений.

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

| ID | Задача | Триггер | Целевые файлы |
|----|--------|---------|---------------|
| `char-builder` | `core/character_builder.py`, dataclass `ResolvedGrants`, единый `resolve_grants(character)` | Game engine или дублирование merge-логики в 3+ местах UI | `core/character_builder.py`, `ui/menus/character_flow.py`, `core/proficiencies.py` |

### Классы и progression

| ID | Задача | Триггер | Целевые файлы |
|----|--------|---------|---------------|
| `class-progression` | `progression.<level>.grants` вместо плоского `features[]` с повторяющимися ASI | Левелап применяет классовые умения из YAML автоматически | `database/classes/classes.yaml`, `core/classes.py` |
| `combat-usage` | Поле `usage: passive \| action \| bonus_action \| reaction` у grants/features | Реализация [`rules/09-combat.md`](rules/09-combat.md) | `database/classes/*.yaml`, combat resolver |

### Валидация и метаданные

| ID | Задача | Триггер | Целевые файлы |
|----|--------|---------|---------------|
| `json-schema` | JSON Schema в `database/schema/v1/`, pytest `tests/test_data_schema.py` | Частые ошибки в YAML при редактировании / PR с данными | `database/schema/`, `tests/` |
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
