---
phb_chapter: 2
phb_section: Расы
phb_pages:
- 17
- 44
phb_part: 1
id: 02-races
tags:
- chapter
mud_status: partial
type: chapter
---

# Расы

> Источник: PHB, стр. 17–44. Индекс рас.

<!-- phb:auto:links -->
## Детальные карточки

| ID | Название | Файл | Статус MUD |
|----|----------|------|------------|
| `dwarf` | Дварф | [dwarf.md](entities/races/dwarf.md) | partial |
| `elf` | Эльф | [elf.md](entities/races/elf.md) | partial |
| `halfling` | Полурослик | [halfling.md](entities/races/halfling.md) | planned |
| `human` | Человек | [human.md](entities/races/human.md) | partial |
| `dragonborn` | Драконорождённый | [dragonborn.md](entities/races/dragonborn.md) | planned |
| `gnome` | Гном | [gnome.md](entities/races/gnome.md) | planned |
| `half_elf` | Полуэльф | [half_elf.md](entities/races/half_elf.md) | planned |
| `half_orc` | Полуорк | [half_orc.md](entities/races/half_orc.md) | partial |
| `tiefling` | Тифлинг | [tiefling.md](entities/races/tiefling.md) | planned |
<!-- /phb:auto:links -->

## Правила (PHB)

<!-- phb:auto:summary -->
### Общие правила

- Раса задаёт увеличение характеристик, размер, скорость, языки и расовые особенности.
- Подрасы — в карточках `entities/races/` (таблица ниже).
- **Без лора:** в справочнике только механика PHB; описания внешности, культуры и мировоззрения — в PDF, не здесь.
<!-- /phb:auto:summary -->

## Реализация в MUD

<!-- mud:implementation -->
### Политика каталога (PHB)

**В ядре допускаются только официальные расы и подрасы из** [`docs/PHB_ D&D_2023 RUS.pdf`](../PHB_%20D%26D_2023%20RUS.pdf) **(глава 2).** Канон — [`database/races/races.yaml`](../../database/races/races.yaml). Расы вне PHB — только через моды `type: addon`.

| Аспект | Значение |
|--------|----------|
| Статус | Частично: 4 расы в YAML (не все 9 PHB) |
| YAML | [`database/races/races.yaml`](../../database/races/races.yaml) |
| Core | [`core/races.py`](../../core/races.py) |
| UI | [`ui/menus/_selectors.py`](../../ui/menus/_selectors.py) (`select_subrace`), [`ui/menus/_display/`](../../ui/menus/_display/) |
| Режимы | Расовые бонусы одинаковы; отображаются до и после распределения stats |

### Расы в MUD (текущий каталог)

| ID | PHB | Подрасы в YAML |
|----|-----|----------------|
| `human` | Человек | `standard`, `variant_human` |
| `elf` | Эльф | несколько подрас |
| `dwarf` | Дварф | несколько подрас |
| `half_orc` | Полуорк | `half_orc` (автовыбор) |

Схема YAML: [`docs/DATA_SCHEMA.md`](../DATA_SCHEMA.md). Моды: `mods/<id>/` + `mods_state.json`.

Отсутствуют в ядре (можно через моды): полурослик, гном, полуэльф, тифлинг; пример — `mods/dragonborn_pack/`.

### Ключевые функции

| Функция | Назначение |
|---------|------------|
| `get_race_bonuses(race_id, subrace_id)` | Статические бонусы расы/подрасы |
| `get_choice_ability_bonus_mechanics(...)` | Параметры выборных бонусов |
| `build_bonuses_from_choices(...)` | Сбор словаря из выбора игрока |
| `get_effective_race_bonuses(...)` | Статические + выборные для отображения |
| `load_races(language)` | Список для меню |
| `load_race_full(race_id, language)` | Полное описание для экрана подрасы |

### Формат YAML (фрагмент)

```yaml
races:
  human:
    subraces:
      standard:
        ability_bonuses: { strength: 1, ... }
        grants:
          - type: language
            count: 1
            choice: true
            pool: common
      variant_human:
        inherit: { ability_bonuses: false, grants: false }
        grants:
          - type: ability_increase
            count: 2
            amount: 1
            choice: true
```

UI выборных бонусов: [`ui/menus/stats/stats_choice_bonuses.py`](../../ui/menus/stats/stats_choice_bonuses.py).

### Не реализовано

- Все 9 рас и полный набор подрас PHB
- Механика особенностей в бою (тёмное зрение, сопротивления) — нет game engine
- Дополнительные языки на выбор (только описание в features)
<!-- /mud:implementation -->
