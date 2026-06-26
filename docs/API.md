# API Reference — dnd_mud Core

Справочник публичного API модулей `core/` и точки входа `main.py`.  
UI (`ui/`) обращается к данным только через `core/`.

---

## core.types — Псевдонимы типов (PEP 695 / 692)

```python
type StatMap = dict[str, int]
type StringsDict = dict[str, Any]
type GameDifficulty = Literal["normal", "hardcore"]
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
    class_name: str
    level: int = 1
    stats: StatMap = field(default_factory=dict)
    current_hp: int = 0
    max_hp: int = 0
    experience: int = 0
    difficulty: GameDifficulty = "normal"
    subrace: str | None = None
    save_slug: str | None = None
```

**Методы:**
- `to_dict() -> dict[str, Any]` — сериализация для JSON
- `from_dict(data: dict[str, Any]) -> Character` — десериализация

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
starting_max_hp(class_id: str, stats: StatMap) -> int
load_characters() -> list[Character]
load_races(language: str = "ru") -> list[dict[str, Any]]
load_race_full(race_id: str, language: str = "ru") -> dict[str, Any]
load_classes(language: str = "ru") -> list[dict[str, Any]]
get_race_bonuses(race_id: str, subrace_id: str | None = None) -> StatMap
apply_bonuses_to_stats(stats: StatMap, bonuses: StatMap) -> StatMap
apply_racial_bonuses_to_stats(
    base_stats: StatMap, race_id: str, subrace_id: str | None = None
) -> StatMap
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

`save_character` создаёт `Character` (`current_hp` = `max_hp` = `starting_max_hp(...)`) и сохраняет в `saves/characters/{save_slug}.json`.  
`starting_max_hp` — PHB: `max(1, hit_dice + ability_modifier(CON))`.  
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

UX-детали (расовые бонусы до/после, экран подтверждения): [MUD_PRD.md §3.4.5](MUD_PRD.md#345-генерация-характеристик-реализовано).

### Формат saves/characters/{save_slug}.json

```json
{
  "schema_version": 1,
  "save_slug": "aragorn",
  "name": "Арагорн",
  "race": "human",
  "subrace": "variant_human",
  "class": "fighter",
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
| `easy` | Лёгкая | Зарезервировано (не в UI) |

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

**Запланированные hook'и (не реализованы)**

- `mod_loader` и проверка `requires_game_difficulty` в метаданных мода
- Параметризация правил в `game_engine` по режиму (HardCore = полная механика D&D 5e)

---

## core.difficulty — Режим сложности и приключения

```python
adventure_requires_hardcore(adventure: Adventure) -> bool
adventure_allows_difficulty(adventure: Adventure, game_difficulty: GameDifficulty) -> bool
adventure_unavailable_reason(adventure: Adventure, character: Character) -> str | None
```

`adventure_unavailable_reason` возвращает ключ локализации (`adventures.unavailable_reason_level` / `adventures.unavailable_reason_hardcore`) или `None`, если приключение доступно. Используется в `_select_adventure()` (`ui/menus/new_game.py`).

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
show_create_character_flow(strings: dict, language: str = "ru") -> Character | None
show_stats_generation_flow(strings: StringsDict, race_id: str, subrace_id: str | None, difficulty: GameDifficulty) -> StatMap | None
show_settings(strings: dict, settings: dict) -> dict
show_languages_menu(strings: dict, settings: dict) -> dict
```

Создание персонажа: сложность → имя → раса/подраса → **генерация характеристик** → **класс** → сохранение.  
Режимы сложности: `normal`, `hardcore` (в перспективе `easy`). HardCore — ключевой режим для механики, приключений и модов.  
Подробности: [MUD_PRD.md §3.2.1](MUD_PRD.md#321-режимы-сложности-игры), [§3.4](MUD_PRD.md#34-flow-создать-персонажа).

---

## ui.input_handler — Ввод

```python
get_int_input(prompt: str, min_val: int, max_val: int, strings: dict | None = None) -> int
get_str_input(prompt: str, min_length: int = 1, only_letters: bool = False, strings: dict | None = None) -> str
```
