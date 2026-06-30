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
| Core | [`core/feats.py`](../../core/feats.py), [`core/feats_loader.py`](../../core/feats_loader.py), [`core/asi.py`](../../core/asi.py) |
| UI | [`ui/menus/feats.py`](../../ui/menus/feats.py), [`ui/menus/asi.py`](../../ui/menus/asi.py), шаг `feats` в [`_creation_steps.py`](../../ui/menus/_creation_steps.py) |

### Реализовано

| Правило PHB | Реализация |
|-------------|------------|
| ASI **или** черта вместо `ability_score_improvement` | `core/asi.py`, `ui/menus/asi.py`, `ui/menus/level_up.py`; слоты ASI в `classes.yaml` |
| Черта при создании (variant human) | Шаг `feats` в `_creation_steps.py`, `race_feat_step_required()` |
| Каждую черту один раз | `can_take_feat()`; `repeatable: true` в YAML (`elemental_adept`) |
| Требования **при взятии** черты | `feat_meets_requirements()` + `requirements` в `feats.yaml`; фильтр в `list_available_feats()` |
| Бонусы к характеристикам, владения, навыки, языки | `resolve_feat_ability_bonuses`, `resolve_feat_grants`, `apply_feat_grants_to_character`; поля `feat_ids`, `feat_choices` |
| Tough: +2 HP/уровень и ретроактивно при взятии | `get_feat_hp_bonus_sources`, `tough_hp_adjustment_on_acquire` |

При создании: бонусы к статам — `select_creation_feats` + `save_character(apply_feat_stat_bonuses=False)`; владения/навыки — шаги proficiencies/skills и merge в `save_character`.  
При левелапе: `apply_feat_grants_to_character` после выбора черты.

Требования проверяются **только в момент выбора** (создание / левелап). Запись в `feat_ids` не снимается при временной потере характеристик.

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
| Resilient: владение спасброском по выбранной характеристике | `save_proficiency` в YAML; поле на `Character` + учёт в Phase 2 checks API |
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
