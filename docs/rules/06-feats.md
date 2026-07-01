# Глава 6: Черты (feats)

> Источник: PHB, стр. 165–170. Полный текст — `docs/PHB_ D&D_2023 RUS.pdf` (локально).  
> См. также: [Мультиклассирование](06-multiclass.md) — отдельная опция PHB из той же главы.

## Для игроков

Черты отражают тренировку и опыт **сверх** того, что даёт класс.

По PHB (опциональное правило):

- на уровнях с **увеличением характеристик** можно вместо ASI взять **черту**;
- **каждую черту один раз**, если в описании не указано иное (`repeatable` в YAML);
- для получения черты нужно **выполнить требования**;
- если требования **перестали выполняться** (проклятие, падение Силы и т.п.), эффекты черты **не применяются**, пока требования снова не выполнены (пример: Борец / Grappler при Силе < 13).

В MUD: на уровнях ASI — выбор ASI или черты; variant human получает одну черту при создании (шаг после класса/подкласса, чтобы учесть владения и заклинания).

## Для разработчиков

### Политика MUD (текущий этап)

| Аспект | Реализация |
|--------|------------|
| Статус | **Реализовано** (создание + ASI/feat при левелапе) |
| YAML | [`database/progression/feats.yaml`](../../database/progression/feats.yaml) |
| Core | [`core/feats.py`](../../core/feats.py), [`core/feat_visibility.py`](../../core/feat_visibility.py), [`core/feats_loader.py`](../../core/feats_loader.py), [`core/asi.py`](../../core/asi.py) |
| UI | [`ui/menus/feats/`](../../ui/menus/feats/), [`ui/menus/asi.py`](../../ui/menus/asi.py), шаг `feats` в [`_creation_steps.py`](../../ui/menus/_creation_steps.py) |

### Реализовано

| Правило PHB | Реализация |
|-------------|------------|
| ASI **или** черта вместо `ability_score_improvement` | `core/asi.py`, `ui/menus/asi.py`, `ui/menus/level_up.py`; слоты ASI в `classes.yaml` |
| Черта при создании (variant human) | Шаг `feats` в `_creation_steps.py`, `race_feat_step_required()` |
| Каждую черту один раз | `can_take_feat()`; `repeatable: true` в YAML (`elemental_adept`) |
| Требования **при взятии** черты | `feat_meets_requirements()` + `requirements` в `feats.yaml`; фильтр в `list_feats_for_selection()` |
| Скрытие черт без новых владений | `feat_visible_for_selection()` в `core/feat_visibility.py`; вызывается из `list_feats_for_selection()` — см. §«Фильтрация списка» |
| Бонусы к характеристикам, владения, навыки, языки | `resolve_feat_ability_bonuses`, `resolve_feat_grants`, `apply_feat_grants_to_character`; поля `feat_ids`, `feat_choices` |
| Tough: +2 HP/уровень и ретроактивно при взятии | `get_feat_hp_bonus_sources`, `tough_hp_adjustment_on_acquire` |

При создании: бонусы к статам — `select_creation_feats` + `save_character(apply_feat_stat_bonuses=False)`; владения/навыки — шаги proficiencies/skills и merge в `save_character`.  
При левелапе: `apply_feat_grants_to_character` после выбора черты.

Требования проверяются **только в момент выбора** (создание / левелап). Запись в `feat_ids` не снимается при временной потере характеристик.

### Фильтрация списка черт

При выборе (создание variant human, ASI → черта) `list_feats_for_selection(ctx, existing_ids)` делит каталог на три группы:

| Группа | Условие | В UI |
|--------|---------|------|
| **Доступные** | требования выполнены, черта ещё не взята, есть **новое** владение | нумерованный список |
| **Требования не выполнены** | есть `requirements` в YAML, контекст не проходит | секция «Требования не выполнены» (`—.`) |
| **Скрыты** | нет новых владений (`feat_visible_for_selection`) | секция «Скрыто» в конце списка (`—.`, серый текст); выбрать нельзя |

**Контекст** (`FeatRequirementContext`) на шаге создания собирается в `build_feat_selection_context()` (`core/feat_visibility.py`) **после** выбора класса и подкласса, **до** шагов владений и навыков класса:

- оружие / доспехи / инструменты: раса, подраса, класс, подкласс (с учётом `level`), фиксированные инструменты предыстории;
- навыки: расовые + предыстория (классовые навыки **ещё не** учтены);
- заклинания: `character_has_spellcasting(class, subclass, level)`.

Опциональные аргументы `skills`, `weapon_tokens`, `tool_tokens` **дополняют** базовый контекст (напр. владения от уже выбранных черт при нескольких расовых picks подряд).

При левелапе контекст строится из текущего `Character` (`build_feat_selection_context_from_character`).

#### Правило `feat_visible_for_selection`

Черта **скрывается**, если **все** её `grants[]` с типами владения уже покрыты контекстом. Проверяются типы:

`weapon_proficiency`, `armor_proficiency`, `skill_proficiency`, `tool_proficiency`, `multiple_proficiency`, `bonus_proficiencies`.

| Grant в черте | Скрыта, когда… |
|---------------|----------------|
| `armor_proficiency` | все категории доспехов из grant уже в `armor_tokens` |
| `weapon_proficiency` (фикс. список) | все виды оружия уже покрыты токенами (`simple`, `martial`, …) |
| `weapon_proficiency` + `choice` (**Мастер оружия**) | любое PHB-оружие уже покрыто токенами |
| `skill_proficiency` (фикс. список или `choice`) | перечисленные навыки уже в `skills`; при `choice` — нет свободных навыков в пуле PHB |
| `tool_proficiency` (фикс. список или `choice`) | перечисленные инструменты уже в `tool_tokens`; при `choice` — нет свободных инструментов в пуле PHB |
| `multiple_proficiency` (**Одарённый**) | все 18 навыков **и** все инструменты каталога уже известны |

Если в `grants[]` есть **хотя бы один** grant другого типа (`damage_reduction`, `lucky`, `medium_armor_master`, `hit_point_bonus`, …), черта **остаётся** в списке — даже при полном перекрытии владений. Примеры: **Мастер тяжёлых доспехов** (`heavy_armor_master`), **Мастер средних доспехов**, **Мастер щитов**, **Крепкий**, **Атлетичный**.

Бонусы к характеристикам (`ability_bonuses` / `ability_bonuses_choice` вне `grants[]`) **не** спасают черту от скрытия: если единственные grants — владения и они все дублируются, черта скрыта (напр. **Знаток тяжёлых доспехов** у воина).

#### Черты, которые чаще всего скрываются (только владения)

| ID (YAML) | Название | Что даёт из владений |
|-----------|----------|----------------------|
| `lightly_armored` | Знаток лёгких доспехов | `light` |
| `moderately_armored` | Знаток средних доспехов | `medium`, `shield` |
| `heavily_armored` | Знаток тяжёлых доспехов | `heavy` |
| `weapon_master` | Мастер оружия | 4 вида оружия на выбор |
| `skilled` | Одарённый | 3 навыка/инструмента на выбор |

#### Справочник по классам и подклассам (PHB-каталог)

Условия: человек (вариант), предыстория **Солдат**, стартовый уровень создания **1** или **3** (подкласс активен с 3 ур.). Скрыты только черты из таблицы выше, требования которых **выполнены**.

| Класс | Подкласс | Ур. | Скрытые черты (владения) |
|-------|----------|-----|--------------------------|
| **Воин** | любой | 1, 3 | `lightly_armored`, `moderately_armored`, `heavily_armored`, `weapon_master` |
| **Плут** | любой | 1, 3 | `lightly_armored` |
| **Жрец** | Домен жизни | 1, 3 | `lightly_armored`, `moderately_armored`, `heavily_armored` |
| **Жрец** | Домен обмана, Домен света | 1, 3 | `lightly_armored`, `moderately_armored` |
| **Бард** | Коллегия доблести | 1 | `lightly_armored` |
| **Бард** | Коллегия доблести | 3 | `lightly_armored`, `moderately_armored`, `weapon_master` |
| **Бард** | Коллегия знаний | 1, 3 | `lightly_armored` |

На 3 уровне у **Коллегии доблести** подкласс добавляет `medium`, `shield`, `martial` — поэтому на 1 ур. ещё доступны `moderately_armored` и `weapon_master`, на 3 ур. — нет.

#### Справочник по расам (воин / Чемпион, 1 ур.)

Дополнительные расовые владения **добавляют** к скрытию черт с перекрывающимися категориями:

| Раса | Подраса | Дополнительно скрывает (к базе воина) |
|------|---------|----------------------------------------|
| **Горный дварф** | `mountain_dwarf` | — (у воина уже всё; дварф даёт `light`, `medium`) |
| **Эльф** | любая | — (воинское владение шире эльфийского списка оружия) |
| **Человек** | `standard`, `variant_human` | — (владения только от класса) |

У **горного дварфа** без уровня воина (другой класс): появляются `light` и `medium` от расы → скрываются `lightly_armored` и частично `moderately_armored` (щит всё ещё может понадобиться).

#### Фильтрация подвыборов внутри черты

После выбора черты `_resolve_feat_subchoices()` исключает из пулов уже известные владения (список черты не пересчитывается):

| Черта | Подвыбор | Исключается |
|-------|----------|-------------|
| `skilled` | навык / инструмент | уже в `skills` / `tool_proficiencies` |
| `weapon_master` | 4 оружия | оружие, покрытое токенами `simple` / `martial` / … |
| `linguist` | 3 языка | уже в `languages` персонажа |

Канон в коде: `core/feat_visibility.py` (`build_feat_selection_context`, `feat_visible_for_selection`), `core/feats.py` (`list_feats_for_selection`), `ui/menus/feats/_selection.py`, `ui/menus/feats/_subchoices.py`. Тесты: `tests/test_feats.py` (параметризация по всем подклассам PHB).

### Запланировано (Phase 2)

Правила PHB, которые **ещё не** отражены в runtime:

| Правило PHB | Целевая реализация |
|-------------|-------------------|
| Пока требования **не выполнены** — нельзя **пользоваться** чертой | `feat_is_active(feat_id, character) -> bool` — обёртка над `feat_meets_requirements()` с полным `FeatRequirementContext` из текущего состояния персонажа |
| Эффекты черты только при `feat_is_active` | В `game_engine` перед применением механики из `grants[]` / YAML |
| Проклятия и временное снижение характеристик | Отдельный слой модификаторов статов (база + временные эффекты); `feat_is_active` смотрит на **эффективные** статы, не только `Character.stats` |
| Бонусы к характеристикам от черты при потере требований | Вариант A: не вычитать из `stats` (PHB: «не получаете преимуществ», не отзыв ASI); вариант B: пересчёт при смене эффективных статов — решить при появлении curse-механики |
| HP от Tough при неактивной черте | `get_feat_hp_bonus_sources` / `max_hp_for_level` — учитывать только **активные** черты при пересчёте HP (если появится динамический пересчёт max HP) |
| Боевые и пассивные механики (`alert`, `sharpshooter`, `war_caster`, …) | Резолвер по `mechanics.type` в `feats.yaml`; интеграция в бой и сценарии ([09-combat.md](09-combat.md)) |
| Resilient: владение спасброском по выбранной характеристике | ✅ при создании: `save_proficiency` → `get_feat_save_proficiencies` → `Character.save_proficiencies`; ongoing `feat_is_active` — Phase 2 |
| Отображение неактивных черт в UI | В карточке персонажа: черта в списке, пометка «требования не выполнены» (опционально) |

**Черновой API (не реализован):**

```python
def feat_requirement_context_from_character(character: Character) -> FeatRequirementContext: ...
def feat_is_active(feat_id: str, character: Character) -> bool: ...
def active_feat_ids(character: Character) -> list[str]: ...
```

**Порядок внедрения:** (1) `feat_is_active` + тесты на падение Силы ниже порога → (2) фильтр в боевых/проверочных резолверах → (3) механики из YAML в `game_engine` → (4) UI и пересчёт HP при необходимости.

### Связь с расами

`variant_human` → feature `type: feat` — шаг `feats` после класса/подкласса, если у расы/подрасы есть слот черты.
