# API Reference — dnd_mud Core

Справочник публичного API модулей `core/` и точки входа `main.py`.  
UI (`ui/`) обращается к данным только через `core/`.

---

## core.types — Псевдонимы типов (PEP 695 / 692)

```python
type StatMap = dict[str, int]
type StringsDict = dict[str, Any]
type GameDifficulty = Literal["easy", "normal", "hardcore"]
type LanguageCode = Literal["ru", "en"]

class RuntimeSettings(TypedDict):
    language: LanguageCode
```

Re-export типов: `core.types`. Фасад функций персонажа — `core.character`.

---

## core.models — Модели данных

### Character

```python
@dataclass
class Character:
    name: str
    race: str
    class_id: str
    level: int = 1
    stats: StatMap = field(default_factory=dict)
    current_hp: int = 0
    max_hp: int = 0
    experience: int = 0
    difficulty: GameDifficulty = "normal"
    subrace: str | None = None
    subclass_id: str | None = None
    languages: list[str] = field(default_factory=list)
    background_id: str | None = None
    skills: list[str] = field(default_factory=list)
    skill_expertise: list[str] = field(default_factory=list)
    tool_expertise: list[str] = field(default_factory=list)
    weapon_proficiencies: list[str] = field(default_factory=list)
    armor_proficiencies: list[str] = field(default_factory=list)
    tool_proficiencies: list[str] = field(default_factory=list)
    feat_ids: list[str] = field(default_factory=list)
    save_slug: str | None = None
```

**Методы:**
- `to_dict() -> dict[str, Any]` — сериализация для JSON (ключ класса — `class_id`)
- `from_dict(data: dict[str, Any]) -> Character` — десериализация; ключ класса — `class_id` (при загрузке старых сейвов — fallback на `"class"`)

### Adventure

```python
@dataclass
class Adventure:
    id: str
    name: dict[str, str] | str
    description: str = ""
    difficulty: str = "normal"  # content tier в YAML, НЕ режим игрока — см. ниже
    author: str = ""
    version: str = "1.0"
    allowed_game_difficulties: list[str] | None = None
    hardcore_only: bool = False
    min_level: int = 1
```

**Методы:**
- `get_name(language: str = "ru") -> str` — локализованное название
- `from_dict(data: dict[str, Any]) -> Adventure` — десериализация

> Поле `Adventure.difficulty` — **уровень контента** (`easy`, `normal`). Это не режим сложности игры (`Character.difficulty`). Ограничения (`allowed_game_difficulties`, `hardcore_only`, `min_level`) загружаются из YAML и проверяются через `adventure_unavailable_reason()` в `_select_adventure()`. HardCore-персонаж не блокируется на приключениях без требования HardCore.

---

## core.character — Персонажи

### Константы

```python
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
STAT_NAMES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
CHARACTERS_DIR = Path("saves/characters")
RACES_FILE = Path("database/races/races.yaml")
CLASSES_FILE = Path("database/classes/classes.yaml")
```

### Сохранение и загрузка

```python
save_character(...) -> Character
update_character(character: Character) -> Character
load_characters() -> LoadCharactersResult
# LoadCharactersResult.characters — tuple[Character, ...]
# LoadCharactersResult.corrupt_save_warnings — имя или save_slug битых JSON
load_races(language: str = "ru") -> list[dict[str, Any]]
load_race_full(race_id: str, language: str = "ru") -> dict[str, Any]
load_classes(language: str = "ru") -> list[dict[str, Any]]
get_race_bonuses(race_id: str, subrace_id: str | None = None) -> StatMap
apply_bonuses_to_stats(stats: StatMap, bonuses: StatMap) -> StatMap
get_choice_ability_bonus_mechanics(race_id: str, subrace_id: str | None = None) -> dict[str, Any] | None
has_choice_ability_bonuses(race_id: str, subrace_id: str | None = None) -> bool
build_bonuses_from_choices(chosen_stats: list[str], value: int = 1) -> StatMap
get_effective_race_bonuses(
    race_id: str,
    subrace_id: str | None = None,
    choice_bonuses: StatMap | None = None,
) -> StatMap

POINT_BUY_BUDGET = 27
POINT_BUY_COSTS: dict[int, int]
point_buy_cost(score: int) -> int
remaining_standard_array_pool(used: list[int]) -> list[int]
point_buy_total_cost(values: list[int]) -> int
can_assign_point_buy_value(current: StatMap, stat: str, new_value: int) -> bool
validate_final_stats(stats: StatMap) -> tuple[str, int] | None
ABILITY_SCORE_MAX = 20
```

`save_character` создаёт `Character` (`current_hp` = `max_hp` = `max_hp_for_level(..., difficulty)`) и сохраняет в `saves/characters/{save_slug}.json`.  
Параметр `apply_feat_stat_bonuses=False` — если `stats` уже содержат бонусы черт (flow создания после `select_creation_feats`).  
`max_hp_for_level` — см. `core.progression` (HP на уровне 1–10, включая режим Normal/Easy/HardCore).  
`update_character` — перезапись JSON после изменений (подкласс, XP и т.д.).
`validate_final_stats` — первое превышение потолка 20 после всех бонусов; UI вызывает при финализации характеристик.

### Генерация характеристик

**Константы** (`core/character.py`):

```python
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
STAT_NAMES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
POINT_BUY_BUDGET = 27
POINT_BUY_COSTS = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
```

**Point-buy** (бюджет 27 очков):

| Значение | Стоимость |
|----------|-----------|
| 8 | 0 |
| 9 | 1 |
| 10 | 2 |
| 11 | 3 |
| 12 | 4 |
| 13 | 5 |
| 14 | 7 |
| 15 | 9 |

**Core-функции:**

```python
generate_stats_standard_array(selected_values: list[int], race_id: str, subrace_id: str | None = None) -> StatMap
generate_stats_point_buy(point_buy_values: list[int], race_id: str, subrace_id: str | None = None) -> StatMap
generate_stats_random(random_values: list[int], race_id: str, subrace_id: str | None = None) -> StatMap
```

Все функции возвращают словарь `{stat_name: value}` с **уже применёнными** расовыми бонусами.

`roll_ability_score()` — в `core.dice` (4d6, убрать наименьший, сумма остальных трёх).

**UI** (`ui/menus.py`):

```python
show_stats_generation_flow(
    strings: dict[str, Any],
    race_id: str,
    subrace_id: str | None,
    difficulty: str,
) -> StatMap | None
```

Поведение по `difficulty`:
- `normal` — меню из 3 методов (standard array / point-buy / 4d6) + экран подтверждения с переквалификацией
- `hardcore` — автоматический 4d6×6 по порядку `STAT_NAMES`, без выбора метода и без переквалификации

UX-детали (расовые бонусы до/после, экран подтверждения): [MUD_PRD.md §3.4.6](MUD_PRD.md#346-генерация-характеристик-реализовано).

### Языки (`core/languages.py`)

```python
load_languages(language: str = "ru") -> list[dict[str, Any]]
get_language_name(lang_id: str, language: str = "ru") -> str
get_fixed_racial_languages(race_id: str, subrace_id: str | None = None) -> list[str]
get_racial_language_choices(race_id: str, subrace_id: str | None = None) -> list[dict[str, Any]]
resolve_language_pool(pool: str, known_languages: list[str]) -> list[str]
racial_languages_step_required(race_id: str, subrace_id: str | None = None) -> bool
```

Каталог: `database/core/languages.yaml`. Пул `common` — только обычные языки PHB; `exotic` / `any` — по явному разрешению в YAML расы или предыстории.

**UI:** `select_creation_languages(strings, race_id, subrace_id, background_id, language) -> list[str] | None` (`ui/menus/languages.py`).

### Расы (`core/races.py`)

Каталог: `database/races/races.yaml` через `load_merged_catalog` (overlay модов). Схема: [`DATA_SCHEMA.md`](DATA_SCHEMA.md).

```python
resolve_subrace_id(race_id: str, subrace_id: str | None = None) -> str | None
auto_select_subrace_id(race_id: str) -> str | None
collect_race_grants(race_id: str, subrace_id: str | None = None) -> list[dict[str, Any]]
clear_races_cache() -> None
```

`resolve_subrace_id` — fallback `human` + `subrace: null` → `standard`.  
`auto_select_subrace_id` — единственная подраса (напр. `half_orc`) без экрана выбора.

### Предыстории (`core/backgrounds.py`)

```python
load_backgrounds(language: str = "ru") -> list[dict[str, Any]]
load_background_full(background_id: str, language: str = "ru") -> dict[str, Any]
get_background_skills(background_id: str) -> list[str]
get_background_language_choice(background_id: str) -> dict[str, Any] | None
```

Каталог: `database/backgrounds/backgrounds.yaml` (13 PHB); механика — `grants[]` (legacy поля нормализуются в loader).

**UI:** `select_creation_background(strings, language) -> tuple[str, list[str]] | None` (`ui/menus/backgrounds.py`) — `(background_id, skills)`.

**UI:** `select_creation_proficiencies(...)` (`ui/menus/proficiencies.py`) — выбор инструментов из пулов класса/предыстории/расы.

---

## core.character_builder — Сборка владений

```python
@dataclass(frozen=True)
class ResolvedGrants:
    weapon_tokens: tuple[str, ...]
    armor_tokens: tuple[str, ...]
    tool_tokens: tuple[str, ...]
    skill_ids: tuple[str, ...]
    language_ids: tuple[str, ...]

resolve_creation_grants(
    race_id, subrace_id, class_id, background_id, subclass_id, level, *,
    feat_ids=None, feat_choices=None,
    extra_skills=None, extra_weapon_tokens=None, extra_tool_tokens=None,
    extra_languages=None, include_feat_languages=True,
) -> ResolvedGrants
merge_languages_with_feats(languages, feat_ids, feat_choices) -> list[str]
merge_expertise_with_feats(skill_expertise, feat_ids, feat_choices) -> list[str]
```

`build_fixed_proficiencies`, `creation_known_for_feat_picks`, `build_feat_selection_context` делегируют в `resolve_creation_grants`.

---

## core.grants — Нормализация grants

Единый формат эффектов из YAML (`grants[]`). Схема типов: [`DATA_SCHEMA.md`](DATA_SCHEMA.md).

```python
inherit_flags(entity: dict[str, Any]) -> tuple[bool, bool]
normalize_grant(raw: dict[str, Any]) -> dict[str, Any]
grants_from_entity(entity: dict[str, Any]) -> list[dict[str, Any]]
merge_entity_grants(
    parent: dict[str, Any] | None,
    entity: dict[str, Any],
    *,
    use_parent: bool,
) -> list[dict[str, Any]]
grant_type(grant: dict[str, Any]) -> str
grants_of_type(grants: list[dict[str, Any]], type_name: str) -> list[dict[str, Any]]
```

`inherit_flags` — `(ability_bonuses, grants)` из `inherit` или legacy `inherit_base_*`.  
`merge_entity_grants` — grants подрасы с наследованием от базовой расы.

---

## core.grant_mechanics — Парсинг proficiency-grants

Разбор владений из `grants[]` (расы, классы, черты). См. также `core/feat_visibility` для скрытия черт в меню.

```python
normalize_armor_token(token: str) -> str
proficiency_tokens_from_grant(grant, choices=None) -> tuple[weapons, armors, tools]
proficiency_tokens_and_skills_from_grant(grant, choices=None) -> tuple[weapons, armors, tools, skills]
```

`normalize_armor_token` — алиасы YAML (`light_armor` → `light` и т.д.).

---

## core.catalog_loader — Единая загрузка каталогов

```python
load_catalog(path: Path | str, root_key: str) -> dict[str, Any]
clear_catalog_cache() -> None
clear_all_catalog_caches() -> None
```

Deep-merge модов через `mod_loader` (overlay по полю `target` — путь к базовому YAML в `manifest.yaml`); кэш `@lru_cache` на `load_catalog` и `load_merged_catalog`.

---

## core.mod_loader — Overlay модов (низкий уровень)

```python
MODS_DIR = Path("mods")
MODS_STATE_FILE = Path("database/core/mods_state.json")

load_merged_yaml(path: Path) -> dict[str, Any]
load_merged_catalog(path_str: str, catalog_key: str) -> dict[str, Any]
clear_mod_loader_cache() -> None
```

`load_merged_catalog` — deep-merge overlay включённых модов. Потребители каталогов — `core/catalog_loader.load_catalog`. Кэш: `@lru_cache` на `load_merged_catalog`.

Формат мода: [`DATA_SCHEMA.md`](DATA_SCHEMA.md) § Mod overlay, [`DEVELOPMENT.md`](DEVELOPMENT.md) § Создание мода.

---

## core.equipment — Каталог снаряжения

Источник: `database/equipment/*.yaml`.

```python
load_weapon(weapon_id: str) -> dict[str, Any]
load_armor(armor_id: str) -> dict[str, Any]
load_tool(tool_id: str) -> dict[str, Any]
load_equipment_item(item_id: str) -> dict[str, Any]
weapon_category(weapon_id: str) -> str
armor_category(armor_id: str) -> str
tool_category(tool_id: str) -> str
tools_by_category(category: str) -> list[str]
resolve_tool_pool(pool: str) -> list[str]
get_weapon_name(weapon_id: str, language: str = "ru") -> str
get_armor_name(armor_id: str, language: str = "ru") -> str
get_tool_name(tool_id: str, language: str = "ru") -> str
weapon_matches_category(category: str, weapon_id: str) -> bool
```

---

## core.constants — Константы PHB

Источник: `database/core/constants.yaml`.

```python
proficiency_bonus(level: int) -> int
difficulty_class(tier: str) -> int
cover_bonus(tier: str) -> int | str | None
size_label(size_id: str) -> str
```

---

## core.abilities — Характеристики и навыки (метаданные)

Источники: `database/core/abilities.yaml`, `database/core/skills.yaml`.

```python
ability_ids() -> tuple[str, ...]
skill_ids() -> tuple[str, ...]
skill_ability_map() -> dict[str, str]
ability_for_skill(skill_id: str) -> str | None
load_skill_info(skill_id: str) -> dict[str, Any]
```

`core/stats.py` → `STAT_NAMES` и `core/skills.py` → `PHB_SKILL_IDS` загружаются из YAML с fallback.

---

## core.feats — Черты

Источник: `database/progression/feats.yaml`. Загрузка — `core/feats_loader.py`; гранты и apply — в `core/feats.py`; скрытие в меню выбора — `core/feat_visibility.py`. UI: пакет `ui/menus/feats/` (`select_creation_feats`, `select_level_up_feat_or_asi`).

```python
load_feats() -> list[dict[str, Any]]
load_feat(feat_id: str) -> dict[str, Any]
race_feat_step_required(race_id, subrace_id) -> bool
feat_meets_requirements(feat_id, ctx) -> bool
feat_visible_for_selection(feat_id, ctx) -> bool
build_feat_selection_context(stats, race_id, subrace_id, background_id, class_id, subclass_id, level, *, skills=None, weapon_tokens=None, tool_tokens=None) -> FeatRequirementContext
list_feats_for_selection(ctx, existing_ids) -> tuple[eligible, blocked, hidden]
resolve_feat_grants(feat_id, choices) -> tuple[weapons, armors, tools, skills]
get_feat_skill_ids(feat_ids, feat_choices) -> list[str]
apply_feats_to_stats(stats, feat_ids, feat_choices) -> StatMap
apply_feat_grants_to_character(character, feat_id, choices) -> Character
tough_hp_adjustment_on_acquire(level) -> int
```

`apply_feat_grants_to_character` — владения, навыки, языки и экспертиза одной черты; вызывается при левелапе (`level_up.py`, `resolve_pending_level_ups`).

`list_feats_for_selection` — eligible (требования OK + новые владения), blocked (требования не выполнены) и hidden (нет новых владений; показываются в конце списка, не выбираются). Уже взятые черты не возвращаются. См. [`06-feats.md`](rules/06-feats.md) §«Фильтрация списка».

**Запланировано (Phase 2):** постоянная проверка требований — `feat_is_active`, `active_feat_ids`, `feat_requirement_context_from_character`; владение спасброском Resilient (`save_proficiency`); см. [`06-feats.md`](rules/06-feats.md) §«Запланировано».

## core.asi — Увеличение характеристик

```python
class_grants_asi_at_level(class_id, level) -> bool
pending_asi_at_level(character, new_level) -> bool
apply_asi_two_one(stats, stat) -> StatMap
con_hp_bonus_from_asi(old_stats, new_stats, level) -> int
```

---

## core.proficiencies — Владения

Merge токенов из класса, подкласса, расы, предыстории и черт. На персонаже хранятся **токены** (`simple`, `martial`, `longsword`, `light`, `thieves_tools`, …), не развёрнутые списки предметов.

```python
ProficiencyChoice  # dataclass: pool, count, label

merge_proficiency_tokens(*parts: list[str]) -> list[str]
get_class_proficiency_tokens(class_id: str) -> tuple[list[str], list[str], list[str]]
get_class_tool_choices(class_id: str) -> list[ProficiencyChoice]
get_subclass_proficiency_tokens(class_id, subclass_id, level) -> tuple[...]
get_racial_proficiency_tokens(race_id, subrace_id) -> tuple[...]
get_background_tool_proficiencies(background_id) -> tuple[list[str], list[ProficiencyChoice]]
get_feat_proficiency_tokens(feat_ids: list[str]) -> tuple[...]
get_proficiency_choices(...) -> list[ProficiencyChoice]
build_fixed_proficiencies(...) -> tuple[list[str], list[str], list[str]]
has_weapon_proficiency(proficiencies, weapon_id) -> bool
has_armor_proficiency(proficiencies, armor_id) -> bool
has_tool_proficiency(proficiencies, tool_id) -> bool
get_class_saving_throws(class_id: str) -> list[str]
apply_subclass_proficiencies_to_character(character) -> Character
```

Импорт из `core.proficiencies` (не re-export в `core.character`).

---

### Формат saves/characters/{save_slug}.json

```json
{
  "schema_version": 1,
  "save_slug": "aragorn",
  "name": "Арагорн",
  "race": "human",
  "subrace": "variant_human",
  "class_id": "fighter",
  "subclass": "champion",
  "background": "folk_hero",
  "languages": ["common", "elvish"],
  "skills": ["survival", "animal_handling", "athletics", "intimidation"],
  "weapon_proficiencies": ["simple", "martial"],
  "armor_proficiencies": ["light", "medium", "heavy", "shield"],
  "tool_proficiencies": ["land_vehicles", "smith_tools"],
  "feat_ids": [],
  "level": 1,
  "stats": {
    "strength": 16,
    "dexterity": 14,
    "constitution": 13,
    "intelligence": 10,
    "wisdom": 12,
    "charisma": 8
  },
  "current_hp": 13,
  "experience": 0,
  "difficulty": "normal"
}
```

Имя файла — slug из `core/slug.make_save_slug()`; при коллизии — `hero_2.json`, `hero_3.json` и т.д.

> **Legacy:** сейвы до переименования поля могли содержать `"class"` вместо `"class_id"`; `from_dict()` читает оба ключа, `to_dict()` пишет только `class_id`.

---

## core.slug — Slug сохранений

```python
make_save_slug(name: str) -> str
```

Транслитерация кириллицы и нормализация имени персонажа в slug для `saves/characters/{slug}.json`.

---

## core.localization — Локализация

```python
load_strings(language: str) -> dict[str, Any]
resolve_localized_text(
    value: str | dict[str, Any] | None,
    language: str,
    *,
    fallback: str = "",
) -> str
get_string(
    strings: dict[str, Any],
    key: str,
    *,
    default: str | None = None,
    **kwargs: Any,
) -> str
```

- Файлы UI: `database/strings/{ru,en}.yaml`
- Имена рас/классов в YAML: `name: { ru: "...", en: "..." }` — через `resolve_localized_text`
- Ключи UI в dot-notation: `menu.new_game`, `character.stats_confirm`

Шаблон настроек: `database/core/settings.json.example`.

---

## core.settings — Настройки пользователя

```python
SETTINGS_PATH = Path("database/core/settings.json")
load_settings() -> RuntimeSettings
save_settings(language: str) -> None
```

### Формат database/core/settings.json

```json
{
  "schema_version": 1,
  "language": "ru"
}
```

**Семантика полей:**
- `language` — язык интерфейса (`ru` / `en`)

Режим сложности игры хранится в `Character.difficulty`, не в settings.

---

## Режим сложности игры

Единая модель выбора игрока. Подробности: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры).

**Допустимые значения**

| ID | UI (ru) | Статус |
|----|---------|--------|
| `normal` | Нормальная | Реализовано |
| `hardcore` | HardCore | Реализовано |
| `easy` | Лёгкая | Реализовано (старт 3 ур., обязательный подкласс) |

**Где хранится и выбирается**

| Место | Поле / функция | Назначение |
|-------|----------------|------------|
| `Character` | `difficulty: GameDifficulty` | Режим персонажа на всю сессию |
| `ui/menus/settings.py` | `select_difficulty()` | Экран выбора в «Создать персонажа» |

**Влияние на генерацию характеристик** (`show_stats_generation_flow`):

| Режим | Поведение |
|-------|-----------|
| `normal` | 3 метода + экран подтверждения / переквалификация |
| `hardcore` | Авто-4d6×6, без выбора метода и без переквалификации |
| `easy` | Как Normal; стартовый уровень 3, подкласс обязателен |

**Запланированные hook'и (не реализованы)**

- Проверка `requires_game_difficulty` в метаданных мода (overlay каталогов — через `core/mod_loader.py`)
- Параметризация правил в `game_engine` по режиму (HardCore = полная механика D&D 5e)

---

## core.difficulty — Режим сложности и приключения

```python
adventure_requires_hardcore(adventure: Adventure) -> bool
adventure_allows_difficulty(adventure: Adventure, game_difficulty: GameDifficulty) -> bool
adventure_unavailable_reason(adventure: Adventure, character: Character) -> str | None
```

`adventure_unavailable_reason` возвращает ключ локализации (`adventures.unavailable_reason_level` / `adventures.unavailable_reason_hardcore`) или `None`, если приключение доступно. Используется в `_select_adventure()` (`ui/menus/new_game.py`).

---

## core.levels — Потолок уровня

```python
MAX_CHARACTER_LEVEL = 10

def clamp_level(level: int) -> int
```

Уровни выше 10 не применяются в runtime; XP может накапливаться.

---

## core.classes — Классы

```python
get_class_dict(class_id: str) -> dict[str, Any]
load_classes(language: str = "ru") -> list[dict[str, Any]]
load_class_full(class_id: str, language: str = "ru") -> dict[str, Any]
load_subclasses(class_id: str, language: str = "ru") -> list[dict[str, Any]]
get_subclass_choice_level(class_id: str) -> int
get_class_hit_dice(class_id: str) -> int
```

`load_class_full` — полный dict класса с локализованными `name`, `description`, `features`, `skill_choices`, `equipment`, `subclasses`.  
`get_subclass_choice_level` — уровень выбора подкласса из YAML (`subclass_choice_level`; по умолчанию 3).

---

## core.subclasses — Подклассы и режимы

```python
def features_up_to_level(features: list, max_level: int = MAX_CHARACTER_LEVEL) -> list
def start_level_for_difficulty(difficulty: GameDifficulty) -> int
def subclass_offered_at_creation(difficulty: GameDifficulty, class_id: str, start_level: int | None = None) -> bool
def subclass_is_active(character: Character) -> bool
def needs_subclass_npc(character: Character) -> bool
def effective_subclass_id(character: Character) -> str | None
```

---

## core.progression — Опыт и уровни

```python
XP_THRESHOLDS: list[int]  # PHB, уровни 1–10

def level_from_xp(experience: int) -> int
def hp_gain_for_level(
    level: int,
    hit_dice: int,
    con_mod: int,
    difficulty: GameDifficulty = "normal",
) -> int
def max_hp_for_level(
    class_id: str,
    stats: StatMap,
    level: int,
    difficulty: GameDifficulty = "normal",
) -> int
def grant_experience(character: Character, amount: int) -> Character
def has_pending_level_up(character: Character) -> bool
def apply_level_up(character: Character, hp_gain: int) -> Character
def resolve_pending_level_ups(character: Character) -> Character
def process_pending_level_ups(
    character: Character,
    *,
    resolve_asi: Callable[[Character, int], AsiResolution | None] | None = None,
    on_level_up: Callable[[Character, int, HpGainBreakdown, int, int], bool] | None = None,
) -> Character
def apply_experience(character: Character, amount: int) -> Character
```

**HP по режиму:** Normal/Easy — макс. кость на 1 ур., среднее на 2+; HardCore — бросок кости на каждом уровне.

**Левелап:** сценарии и UI начисляют XP через `grant_experience`; повышение — по одному уровню (`apply_level_up` + экран `ui/menus/level_up.py`). `apply_experience` — convenience для тестов (XP + все уровни без UI).

**UI:** `run_pending_level_ups(strings, character, language) -> Character` (`ui/menus/level_up.py`).

**Сценарии:** action `grant_xp` → `ScenarioActionResult.level_up_pending`; runner вызывает `run_pending_level_ups` перед сохранением.

Re-export: `MAX_CHARACTER_LEVEL`, `clamp_level` из `core.levels`.

---

## core.scenario_actions — Логика сценария (без UI)

```python
@dataclass
class ScenarioActionResult:
    character: Character
    level_up_pending: bool = False
    pick_subclass: bool = False
    apply_class_features: bool = False
    message_key: str | None = None

def load_scenario(script_file: str) -> dict[str, Any]
def apply_scenario_action(
    action: str,
    action_data: dict[str, Any],
    character: Character,
) -> ScenarioActionResult
```

Действия: `grant_xp`, `subclass_training`, `text`, `menu`. Источник узлов: `adventures/*.yaml`.

## ui.menus.scenario_flow — Интерактивный runner

```python
def run_scenario(
    adventure: Adventure,
    character: Character,
    strings: StringsDict,
    language: LanguageCode = "ru",
) -> Character
```

Вызывает `apply_scenario_action`, затем UI: левелап (`level_up.py`), подкласс (`subclass_trainer`), особенности класса (`class_features.py`).

## core.adventure — Приключения

```python
load_adventures() -> list[Adventure]
```

Источник: `database/content/adventures.yaml`.  
Отображаемое имя — через `Adventure.get_name(language)`.

---

## core.dice — Броски кубиков

```python
roll(count=1, sides=20, modifier=0) -> int
roll_ability_score() -> int
ability_modifier(score: int) -> int
```

---

## main.py — Точка входа

```python
VERSION = "0.1.0"
main() -> int
```

**Главное меню (реализовано):**

| № | Пункт | Обработчик |
|---|-------|------------|
| 1 | Новая игра | `show_new_game_flow` |
| 2 | Загрузить игру | `show_load_game_flow` (заглушка) |
| 3 | Создать персонажа | `show_create_character_flow` |
| 4 | Настройки | `show_settings` |
| 5 | Languages | `show_languages_menu` |
| 0 | Выход | завершение |

После изменения настроек или языка вызывается `_save_and_reload_settings`.

---

## ui.menus — Публичные flow-функции

```python
show_welcome_screen(version: str, strings: dict) -> None
show_main_menu(strings: dict) -> int
select_difficulty(strings: dict) -> str | None
show_new_game_flow(strings: dict, settings: dict) -> None
show_load_game_flow(strings: dict) -> None
show_create_character_flow(strings: dict, language: str = "ru") -> Character | None  # ui/menus/_creation_steps.py
show_stats_generation_flow(strings: StringsDict, race_id: str, subrace_id: str | None, difficulty: GameDifficulty) -> StatMap | None
show_settings(strings: dict, settings: dict) -> dict
show_languages_menu(strings: dict, settings: dict) -> dict
```

Создание персонажа: сложность → имя → раса → подраса → **характеристики** → **предыстория** → **языки** → класс → подкласс → **владения** → **навыки** → (компетентность?) → сохранение.  
Режимы сложности: `easy`, `normal`, `hardcore`. HardCore — ключевой режим для механики, приключений и модов.  
Подробности: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры), [§3.4](MUD_PRD.md#34-flow-создать-персонажа).

---

## ui.input_handler — Ввод

```python
get_int_input(prompt: str, min_val: int, max_val: int, strings: dict | None = None) -> int
get_str_input(prompt: str, min_length: int = 1, only_letters: bool = False, strings: dict | None = None) -> str
```
