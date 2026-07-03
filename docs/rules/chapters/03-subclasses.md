---
phb_chapter: 3
phb_section: Подклассы
phb_pages:
- 48
- 119
phb_part: 1
id: 03-subclasses
tags:
- chapter
mud_status: planned
type: chapter
---

# Подклассы

> Источник: PHB, гл. 3. Механика архетипов.

## Правила (PHB)

<!-- phb:auto:summary -->
### Подклассы (архетипы)

- Подкласс выбирается на уровне, указанном в классе (чаще всего 2–3).
- Даёт дополнительные умения на фиксированных уровнях.
- Детали — в карточке класса (`### Подклассы`) и в `database/classes/classes.yaml` для классов в ядре MUD.

### В MUD

- Выбор подкласса при создании зависит от режима сложности — см. `mud:implementation` в [01-character-creation.md](01-character-creation.md).
<!-- /phb:auto:summary -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | **Реализовано (Pre-Alpha):** UI выбора при создании и у NPC; умения в бою — Phase 2 |
| Канон каталога | Только `subclasses` из [`classes.yaml`](../../database/classes/classes.yaml) для классов, уже присутствующих в YAML |
| Потолок уровня | Умения с `level > 10` в YAML не показываются и не применяются (`MAX_CHARACTER_LEVEL`) |
| PRD | §3.4.7: выбор подкласса, режимы easy/normal/hardcore |
| Flow создания | После класса → подкласс (если `subclass_offered_at_creation`); иначе NPC на 3+ ур. (hardcore fighter/rogue/bard) |
| NPC | Меню персонажей `subclass_trainer`; сценарий `subclass_training` в `core/scenario_actions.py` |

### Режимы сложности и подкласс

| Режим | Старт | Подкласс при создании | Активация |
|-------|-------|------------------------|-----------|
| `easy` | 3 ур. | Обязателен | Сразу |
| `normal` | 1 ур. | Обязателен | `level ≥ subclass_choice_level` |
| `hardcore` | 1 ур. | Только `subclass_choice_level ≤ 1` | Иначе — наставник |

Поле `subclass_choice_level` на уровне класса в YAML: `cleric: 1`, `fighter` / `rogue` / `bard`: 3.

### Рекомендуемая схема данных (реализовано)

```yaml
subclasses:
  - id: battle_master
    name: { ru: "Мастер боевых искусств", en: "Battle Master" }
    parent_class: fighter
    choice_level: 3
    phb_pages: "72-74"
    features:
      - id: battle_maneuvers
        level: 3
        feature_type: active
```

Поле `choice_level` должно соответствовать таблице выше. Домены жреца и происхождения чародея/колдуна в PHB выбираются на **1 уровне** класса.

### Не реализовано

- Применение `features` подкласса в game engine (бой, заклинания)
- Заклинания доменов, клятв, расширенные списки колдуна
- Кости превосходства, приёмы, дикий облик, зверь-спутник и прочая механика подклассов
<!-- /mud:implementation -->
