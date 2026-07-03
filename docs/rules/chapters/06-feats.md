---
phb_chapter: 6
phb_section: Черты
phb_pages:
- 166
- 172
phb_part: 1
id: 06-feats
tags:
- chapter
mud_status: partial
type: chapter
---

# Черты

> Источник: PHB, стр. 166–172. Пересказ правил.

<!-- phb:auto:links -->
## Детальные карточки

| ID | Название | Файл | Статус MUD |
|----|----------|------|------------|
| `actor` | Артистичный | [actor.md](entities/feats/actor.md) | partial |
| `athlete` | Атлетичный | [athlete.md](entities/feats/athlete.md) | partial |
| `alert` | Бдительный | [alert.md](entities/feats/alert.md) | partial |
| `war_caster` | Боевой Заклинатель | [war_caster.md](entities/feats/war_caster.md) | partial |
| `grappler` | Борец | [grappler.md](entities/feats/grappler.md) | partial |
| `lucky` | Везунчик | [lucky.md](entities/feats/lucky.md) | partial |
| `mounted_combatant` | Верховой Боец | [mounted_combatant.md](entities/feats/mounted_combatant.md) | partial |
| `observant` | Внимательный | [observant.md](entities/feats/observant.md) | partial |
| `martial_adept` | Воинский Адепт | [martial_adept.md](entities/feats/martial_adept.md) | partial |
| `inspiring_leader` | Воодушевляющий Лидер | [inspiring_leader.md](entities/feats/inspiring_leader.md) | partial |
| `savage_attacker` | Дикий Атакующий | [savage_attacker.md](entities/feats/savage_attacker.md) | partial |
| `tavern_brawler` | Драчун | [tavern_brawler.md](entities/feats/tavern_brawler.md) | partial |
| `lightly_armored` | Знаток Лёгких Доспехов | [lightly_armored.md](entities/feats/lightly_armored.md) | partial |
| `moderately_armored` | Знаток Средних Доспехов | [moderately_armored.md](entities/feats/moderately_armored.md) | partial |
| `heavily_armored` | Знаток Тяжёлых Доспехов | [heavily_armored.md](entities/feats/heavily_armored.md) | partial |
| `dual_wielder` | Использование Двух Оружий | [dual_wielder.md](entities/feats/dual_wielder.md) | partial |
| `dungeon_delver` | Исследователь Подземелий | [dungeon_delver.md](entities/feats/dungeon_delver.md) | partial |
| `tough` | Крепкий | [tough.md](entities/feats/tough.md) | partial |
| `healer` | Лекарь | [healer.md](entities/feats/healer.md) | partial |
| `great_weapon_master` | Мастер Большого Оружия | [great_weapon_master.md](entities/feats/great_weapon_master.md) | partial |
| `polearm_master` | Мастер Древкового Оружия | [polearm_master.md](entities/feats/polearm_master.md) | partial |
| `weapon_master` | Мастер Оружия | [weapon_master.md](entities/feats/weapon_master.md) | partial |
| `medium_armor_master` | Мастер Средних Доспехов | [medium_armor_master.md](entities/feats/medium_armor_master.md) | partial |
| `heavy_armor_master` | Мастер Тяжёлых Доспехов | [heavy_armor_master.md](entities/feats/heavy_armor_master.md) | partial |
| `shield_master` | Мастер Щитов | [shield_master.md](entities/feats/shield_master.md) | partial |
| `spell_sniper` | Меткие Заклинания | [spell_sniper.md](entities/feats/spell_sniper.md) | partial |
| `sharpshooter` | Меткий Стрелок | [sharpshooter.md](entities/feats/sharpshooter.md) | partial |
| `charger` | Налётчик | [charger.md](entities/feats/charger.md) | partial |
| `defensive_duelist` | Оборонительный Дуэлянт | [defensive_duelist.md](entities/feats/defensive_duelist.md) | partial |
| `skilled` | Одарённый | [skilled.md](entities/feats/skilled.md) | partial |
| `keen_mind` | Отличная Память | [keen_mind.md](entities/feats/keen_mind.md) | partial |
| `mobile` | Подвижный | [mobile.md](entities/feats/mobile.md) | partial |
| `magic_initiate` | Посвящённый В Магию | [magic_initiate.md](entities/feats/magic_initiate.md) | partial |
| `skulker` | Проныра | [skulker.md](entities/feats/skulker.md) | partial |
| `ritual_caster` | Ритуальный Заклинатель | [ritual_caster.md](entities/feats/ritual_caster.md) | partial |
| `elemental_adept` | Стихийный Адепт | [elemental_adept.md](entities/feats/elemental_adept.md) | partial |
| `durable` | Стойкий | [durable.md](entities/feats/durable.md) | partial |
| `sentinel` | Страж | [sentinel.md](entities/feats/sentinel.md) | partial |
| `mage_slayer` | Убийца Магов | [mage_slayer.md](entities/feats/mage_slayer.md) | partial |
| `resilient` | Устойчивый | [resilient.md](entities/feats/resilient.md) | partial |
| `crossbow_expert` | Эксперт В Арбалетах | [crossbow_expert.md](entities/feats/crossbow_expert.md) | partial |
| `linguist` | Языковед | [linguist.md](entities/feats/linguist.md) | partial |
<!-- /phb:auto:links -->

## Правила (PHB)

<!-- phb:auto:summary -->
### Общие правила

- Черты — опциональная замена умения «Улучшение характеристик» на некоторых уровнях.
- Каждую черту можно взять **один раз**, если в описании не указано иное.
- Требования черты проверяются **в момент выбора**; при их потере эффект не работает.
- Механика каждой черты — в карточках `entities/feats/` (таблица ниже).
<!-- /phb:auto:summary -->

## Реализация в MUD

<!-- mud:implementation -->
| Аспект | Значение |
|--------|----------|
| Статус | partial |
| YAML | `database/progression/feats.yaml` |
| Core | `core/feats.py`, `core/feat_requirements.py` |
| UI | `ui/menus/feats/` |
| Детали | `docs/API.md` §core.feats |

### Фильтрация списка

`list_feats_for_selection` возвращает три группы:

| Группа | Условие | UI |
|--------|---------|----|
| **eligible** | Требования выполнены и черта даёт **новые** владения | Выбираемые |
| **blocked** | Требования не выполнены | Показ с причиной, не выбираются |
| **hidden** | Требования OK, но владения уже есть (раса/класс/другие черты) | Секция «Скрыто» в конце списка |

Уже взятые черты не возвращаются.

### Запланировано (Phase 2)

- Постоянная проверка требований в runtime: `feat_is_active`, `active_feat_ids`, `feat_requirement_context_from_character`.
- Потеря требований (смена доспехов и т.п.) отключает эффект черты.
<!-- /mud:implementation -->
