"""Создание, сохранение и загрузка персонажей.

Персонажи хранятся в JSON-файле saves/characters.json.
Расы и классы — в database/races/races.yaml и database/classes/classes.yaml.
"""

import json
from pathlib import Path
from typing import Any

import yaml

from core.dice import ability_modifier, roll_ability_score
from core.models import Character

STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

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

SAVES_DIR = Path("saves")
CHARACTERS_FILE = SAVES_DIR / "characters.json"
CHARACTERS_SCHEMA_VERSION = 1
RACES_FILE = Path("database/races/races.yaml")
CLASSES_FILE = Path("database/classes/classes.yaml")


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
    )

    characters = load_characters()
    characters.append(character)
    _save_characters(characters)

    return character


def _apply_racial_bonuses_to_stats(
    base_stats: dict[str, int], race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Применить расовые и подрасовые бонусы к базовым характеристикам."""
    final_stats = base_stats.copy()
    bonuses = get_race_bonuses(race_id, subrace_id)
    for stat_name, bonus in bonuses.items():
        if stat_name in final_stats:
            final_stats[stat_name] += bonus
        else:
            final_stats[stat_name] = bonus
    return final_stats


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


def generate_stats_hardcore(
    race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Сгенерировать характеристики для сложности HardCore."""
    rolled_values = [roll_ability_score() for _ in range(len(STAT_NAMES))]
    return _build_stats(rolled_values, race_id, subrace_id)


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


def load_characters() -> list[Character]:
    """Загрузить список всех сохранённых персонажей."""
    if not CHARACTERS_FILE.exists():
        return []

    try:
        with open(CHARACTERS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        result = data.get("characters", [])
        if not isinstance(result, list):
            return []
        characters: list[Character] = []
        for item in result:
            if isinstance(item, dict) and item.get("name"):
                characters.append(Character.from_dict(item))
        return characters
    except (json.JSONDecodeError, OSError):
        return []


def _save_characters(characters: list[Character]) -> None:
    """Сохранить список персонажей в JSON-файл."""
    CHARACTERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": CHARACTERS_SCHEMA_VERSION,
        "characters": [c.to_dict() for c in characters],
    }
    with open(CHARACTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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
