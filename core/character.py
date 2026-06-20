"""Создание, сохранение и загрузка персонажей.

Персонажи хранятся в отдельных JSON-файлах saves/characters/{save_slug}.json.
Расы и классы — в database/races/races.yaml и database/classes/classes.yaml.
"""

import json
import re
from pathlib import Path
from typing import Any

import yaml

from core.dice import ability_modifier
from core.models import Character

STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
STANDARD_ARRAY_MIN = min(STANDARD_ARRAY)
STANDARD_ARRAY_MAX = max(STANDARD_ARRAY)

STAT_NAMES = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]

POINT_BUY_BUDGET = 27
POINT_BUY_COSTS: dict[int, int] = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9,
}
POINT_BUY_MIN = min(POINT_BUY_COSTS)
POINT_BUY_MAX = max(POINT_BUY_COSTS)

SAVES_DIR = Path("saves")
CHARACTERS_DIR = SAVES_DIR / "characters"
CHARACTERS_SCHEMA_VERSION = 1
RACES_FILE = Path("database/races/races.yaml")
CLASSES_FILE = Path("database/classes/classes.yaml")

_CYRILLIC_TO_LATIN: dict[str, str] = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def point_buy_cost(score: int) -> int:
    """Стоимость значения характеристики в point-buy."""
    return POINT_BUY_COSTS.get(score, 0)


def remaining_standard_array_pool(used: list[int]) -> list[int]:
    """Остаток стандартного массива после уже назначенных значений."""
    pool = list(STANDARD_ARRAY)
    for value in used:
        if value in pool:
            pool.remove(value)
    return sorted(pool, reverse=True)


def point_buy_total_cost(values: list[int]) -> int:
    """Суммарная стоимость набора характеристик в point-buy."""
    return sum(point_buy_cost(value) for value in values)


def can_assign_point_buy_value(
    current: dict[str, int], stat: str, new_value: int
) -> bool:
    """Проверить, допустимо ли новое значение (8–15, бюджет не превышен)."""
    if new_value not in POINT_BUY_COSTS:
        return False
    updated = dict(current)
    updated[stat] = new_value
    values = [updated[name] for name in STAT_NAMES]
    return point_buy_total_cost(values) <= POINT_BUY_BUDGET


def save_character(
    name: str,
    race_id: str,
    class_id: str,
    difficulty: str = "normal",
    subrace_id: str | None = None,
    stats: dict[str, int] | None = None,
) -> Character:
    """Создать нового персонажа и сохранить в JSON."""
    if stats is None:
        stats = dict(zip(STAT_NAMES, STANDARD_ARRAY, strict=False))
        stats = _apply_racial_bonuses_to_stats(stats, race_id, subrace_id)

    hit_dice = _get_class_hit_dice(class_id)
    con_mod = ability_modifier(stats.get("constitution", 10))
    hp = hit_dice + con_mod

    character = Character(
        name=name,
        race=race_id,
        class_name=class_id,
        level=1,
        stats=stats,
        current_hp=hp,
        experience=0,
        difficulty=difficulty,
        subrace=subrace_id,
        save_slug=_unique_save_slug(name),
    )

    _save_character_file(character)

    return character


def apply_bonuses_to_stats(
    stats: dict[str, int], bonuses: dict[str, int]
) -> dict[str, int]:
    """Добавить бонусы к характеристикам."""
    final_stats = stats.copy()
    for stat_name, bonus in bonuses.items():
        if stat_name in final_stats:
            final_stats[stat_name] += bonus
        else:
            final_stats[stat_name] = bonus
    return final_stats


def _apply_racial_bonuses_to_stats(
    base_stats: dict[str, int], race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Применить расовые и подрасовые бонусы к базовым характеристикам."""
    bonuses = get_race_bonuses(race_id, subrace_id)
    return apply_bonuses_to_stats(base_stats, bonuses)


def _load_races_yaml() -> dict[str, Any]:
    """Загрузить данные рас из YAML."""
    if not RACES_FILE.exists():
        return {}
    try:
        with open(RACES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        races = data.get("races", {})
        if isinstance(races, dict):
            return races
    except (yaml.YAMLError, OSError):
        pass
    return {}


def get_race_bonuses(
    race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Получить расовые и подрасовые бонусы к характеристикам."""
    bonuses: dict[str, int] = {}
    races = _load_races_yaml()
    race_info = races.get(race_id, {})
    if subrace_id:
        subraces = race_info.get("subraces", {})
        subrace_info = subraces.get(subrace_id, {})
        inherit_base = subrace_info.get("inherit_base_bonuses", True)
    else:
        subrace_info = {}
        inherit_base = True

    if inherit_base:
        base_bonuses = race_info.get("ability_bonuses", {})
        if isinstance(base_bonuses, dict):
            bonuses.update(base_bonuses)

    if subrace_id:
        sub_bonuses = subrace_info.get("ability_bonuses", {})
        if isinstance(sub_bonuses, dict):
            for stat, val in sub_bonuses.items():
                bonuses[stat] = bonuses.get(stat, 0) + val
    return bonuses


def _race_info_for_features(
    race_id: str, subrace_id: str | None = None
) -> dict[str, Any]:
    """Данные расы/подрасы для чтения features."""
    races = _load_races_yaml()
    race_info = races.get(race_id, {})
    if not isinstance(race_info, dict):
        return {}
    if subrace_id:
        subraces = race_info.get("subraces", {})
        subrace_info = subraces.get(subrace_id, {})
        if isinstance(subrace_info, dict):
            return subrace_info
    return race_info


def get_choice_ability_bonus_mechanics(
    race_id: str, subrace_id: str | None = None
) -> dict[str, Any] | None:
    """Механика выборного бонуса к характеристикам из features."""
    info = _race_info_for_features(race_id, subrace_id)
    for feat in info.get("features", []):
        if not isinstance(feat, dict):
            continue
        if feat.get("type") != "ability_bonus":
            continue
        mechanics = feat.get("mechanics", {})
        if isinstance(mechanics, dict) and mechanics.get("choice"):
            return mechanics
    return None


def has_choice_ability_bonuses(
    race_id: str, subrace_id: str | None = None
) -> bool:
    """Есть ли у расы/подрасы выборные бонусы к характеристикам."""
    return get_choice_ability_bonus_mechanics(race_id, subrace_id) is not None


def build_bonuses_from_choices(
    chosen_stats: list[str], value: int = 1
) -> dict[str, int]:
    """Собрать словарь бонусов из списка выбранных характеристик."""
    bonuses: dict[str, int] = {}
    for stat in chosen_stats:
        bonuses[stat] = bonuses.get(stat, 0) + value
    return bonuses


def get_effective_race_bonuses(
    race_id: str,
    subrace_id: str | None = None,
    choice_bonuses: dict[str, int] | None = None,
) -> dict[str, int]:
    """Статические и выборные расовые бонусы для отображения."""
    bonuses = get_race_bonuses(race_id, subrace_id)
    if choice_bonuses:
        for stat, val in choice_bonuses.items():
            bonuses[stat] = bonuses.get(stat, 0) + val
    return bonuses


def _build_stats(
    values: list[int], race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Собрать характеристики из шести значений и применить бонусы расы."""
    if len(values) != len(STAT_NAMES):
        raise ValueError(
            f"Expected {len(STAT_NAMES)} values, got {len(values)}"
        )
    base_stats = dict(zip(STAT_NAMES, values, strict=True))
    return _apply_racial_bonuses_to_stats(base_stats, race_id, subrace_id)


def generate_stats_standard_array(
    selected_values: list[int],
    race_id: str,
    subrace_id: str | None = None,
) -> dict[str, int]:
    """Сгенерировать характеристики из стандартного массива."""
    return _build_stats(selected_values, race_id, subrace_id)


def generate_stats_point_buy(
    point_buy_values: list[int],
    race_id: str,
    subrace_id: str | None = None,
) -> dict[str, int]:
    """Сгенерировать характеристики методом покупки очков."""
    return _build_stats(point_buy_values, race_id, subrace_id)


def generate_stats_random(
    random_values: list[int],
    race_id: str,
    subrace_id: str | None = None,
) -> dict[str, int]:
    """Сгенерировать характеристики случайным методом."""
    return _build_stats(random_values, race_id, subrace_id)


def _get_class_hit_dice(class_id: str) -> int:
    """Получить кость здоровья класса."""
    if not CLASSES_FILE.exists():
        return 8
    try:
        with open(CLASSES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        classes = data.get("classes", {})
        class_info = classes.get(class_id, {})
        hit_dice = class_info.get("hit_dice", 8)
        if isinstance(hit_dice, int):
            return hit_dice
    except (yaml.YAMLError, OSError):
        pass
    return 8


def _transliterate(text: str) -> str:
    """Транслитерировать кириллицу в латиницу."""
    result: list[str] = []
    for char in text:
        lower = char.lower()
        if lower in _CYRILLIC_TO_LATIN:
            mapped = _CYRILLIC_TO_LATIN[lower]
            if char.isupper() and mapped:
                mapped = mapped[0].upper() + mapped[1:]
            result.append(mapped)
        else:
            result.append(char)
    return "".join(result)


def _slug_from_name(name: str) -> str:
    """Построить slug из имени персонажа."""
    transliterated = _transliterate(name).lower()
    slug = re.sub(r"[^a-z0-9]+", "_", transliterated)
    slug = slug.strip("_")
    return slug or "character"


def _existing_save_slugs() -> set[str]:
    """Собрать save_slug из имён файлов и содержимого JSON."""
    slugs: set[str] = set()
    if not CHARACTERS_DIR.exists():
        return slugs

    for path in CHARACTERS_DIR.glob("*.json"):
        slugs.add(path.stem)
        character = _load_character_file(path)
        if character is not None and character.save_slug:
            slugs.add(character.save_slug)
    return slugs


def _unique_save_slug(name: str) -> str:
    """Уникальный save_slug для нового персонажа."""
    base = _slug_from_name(name)
    existing = _existing_save_slugs()
    if base not in existing:
        return base

    counter = 2
    while f"{base}_{counter}" in existing:
        counter += 1
    return f"{base}_{counter}"


def _character_file_path(save_slug: str) -> Path:
    """Путь к JSON-файлу персонажа."""
    return CHARACTERS_DIR / f"{save_slug}.json"


def _save_character_file(character: Character) -> None:
    """Сохранить одного персонажа в отдельный JSON-файл."""
    if not character.save_slug:
        raise ValueError("У персонажа должен быть save_slug")

    CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": CHARACTERS_SCHEMA_VERSION,
        **character.to_dict(),
    }
    path = _character_file_path(character.save_slug)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_character_file(path: Path) -> Character | None:
    """Загрузить одного персонажа из JSON-файла."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or not data.get("name"):
            return None

        character = Character.from_dict(data)
        if not character.save_slug:
            character.save_slug = path.stem
        return character
    except (json.JSONDecodeError, OSError):
        return None


def load_characters() -> list[Character]:
    """Загрузить список всех сохранённых персонажей."""
    if not CHARACTERS_DIR.exists():
        return []

    characters: list[Character] = []
    for path in sorted(CHARACTERS_DIR.glob("*.json")):
        character = _load_character_file(path)
        if character is not None:
            characters.append(character)

    characters.sort(key=lambda c: c.name.lower())
    return characters


def load_races() -> list[dict[str, Any]]:
    """Загрузить список всех доступных рас."""
    races = _load_races_yaml()
    result = []
    for race_id, race_info in races.items():
        if isinstance(race_info, dict):
            result.append(
                {
                    "id": race_id,
                    "name": race_info.get("name", race_id),
                }
            )
    return result


def load_race_full(race_id: str) -> dict[str, Any]:
    """Загрузить полные данные расы по ID."""
    races = _load_races_yaml()
    race_info = races.get(race_id, {})
    if isinstance(race_info, dict):
        return race_info
    return {}


def load_classes() -> list[dict[str, Any]]:
    """Загрузить список всех доступных классов."""
    if not CLASSES_FILE.exists():
        return []

    try:
        with open(CLASSES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        classes = data.get("classes", {})
        result = []
        for class_id, class_info in classes.items():
            if isinstance(class_info, dict):
                result.append(
                    {
                        "id": class_id,
                        "name": class_info.get("name", class_id),
                        "description": class_info.get("description", ""),
                        "hit_dice": class_info.get("hit_dice", 8),
                        "prime_ability": class_info.get(
                            "prime_ability", "strength"
                        ),
                    }
                )
        return result
    except (yaml.YAMLError, OSError):
        return []
