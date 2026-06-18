"""Создание, сохранение и загрузка персонажей.

Персонажи хранятся в YAML-файле database/characters.yaml.
Расы и классы — в database/races.yaml и database/classes.yaml.
"""

from pathlib import Path
from typing import Any

import yaml

from core.dice import ability_modifier

# Стандартный набор характеристик D&D 5e (массив)
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

# Названия всех шести характеристик по порядку
STAT_NAMES = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]

CHARACTERS_FILE = Path("database/progression/characters.yaml")
RACES_FILE = Path("database/races/races.yaml")
CLASSES_FILE = Path("database/classes/classes.yaml")


def save_character(
    name: str,
    race_id: str,
    class_id: str,
    difficulty: str = "normal",
    subrace_id: str | None = None,
) -> dict[str, Any]:
    """Создать нового персонажа и сохранить в YAML.

    Персонаж получает:
    - характеристики из стандартного массива + расовые бонусы
    - хиты 1-го уровня (кость здоровья класса + модификатор Телосложения)

    Args:
        name: Имя персонажа
        race_id: ID расы (например, 'human', 'elf')
        class_id: ID класса (например, 'fighter', 'wizard')
        difficulty: Сложность игры
        subrace_id: ID подрасы (опционально)

    Returns:
        Словарь с данными нового персонажа
    """
    stats = _generate_stats(race_id, subrace_id)
    hit_dice = _get_class_hit_dice(class_id)
    con_mod = ability_modifier(stats.get("constitution", 10))
    hp = hit_dice + con_mod

    character = {
        "name": name,
        "race": race_id,
        "subrace": subrace_id,
        "class": class_id,
        "level": 1,
        "stats": stats,
        "current_hp": hp,
        "experience": 0,
        "difficulty": difficulty,
    }

    # Сохраняем
    characters = load_characters()
    characters.append(character)
    _save_characters(characters)

    return character


def _generate_stats(
    race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Сгенерировать характеристики: массив + расовые бонусы.

    Берём стандартный массив [15, 14, 13, 12, 10, 8],
    сортируем по убыванию, назначаем всем шести характеристикам,
    потом добавляем расовые и подрасовые бонусы.

    Args:
        race_id: ID расы
        subrace_id: ID подрасы (опционально)

    Returns:
        Словарь {название_характеристики: значение}
    """
    sorted_array = sorted(STANDARD_ARRAY, reverse=True)
    stats = dict(zip(STAT_NAMES, sorted_array, strict=True))

    bonuses = _get_race_bonuses(race_id, subrace_id)
    for stat_name, bonus in bonuses.items():
        if stat_name in stats:
            stats[stat_name] += bonus

    return stats


def _get_race_bonuses(
    race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Получить расовые и подрасовые бонусы к характеристикам.

    Например, для дварфа: +2 к Телосложению.

    Args:
        race_id: ID расы
        subrace_id: ID подрасы (опционально)

    Returns:
        Словарь {название_характеристики: бонус}
    """
    bonuses: dict[str, int] = {}
    try:
        with open(RACES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        races = data.get("races", {})
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
    except (yaml.YAMLError, OSError):
        pass
    return bonuses


def _get_class_hit_dice(class_id: str) -> int:
    """Получить кость здоровья класса (например, для воина — 10).

    Args:
        class_id: ID класса

    Returns:
        Количество граней кости здоровья (по умолчанию 8)
    """
    try:
        with open(CLASSES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        classes = data.get("classes", {})
        class_info = classes.get(class_id, {})
        hit_dice = class_info.get("hit_dice", 8)
        if isinstance(hit_dice, int):
            return hit_dice
        return 8
    except (yaml.YAMLError, OSError):
        return 8


def load_characters() -> list[dict[str, Any]]:
    """Загрузить список всех сохранённых персонажей.

    Returns:
        Список словарей с данными персонажей
    """
    if not CHARACTERS_FILE.exists():
        return []

    try:
        with open(CHARACTERS_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        result = data.get("characters", [])
        if isinstance(result, list):
            return result
        return []
    except (yaml.YAMLError, OSError):
        return []


def _save_characters(characters: list[dict[str, Any]]) -> None:
    """Сохранить список персонажей в YAML-файл.

    Args:
        characters: Список словарей с данными персонажей
    """
    CHARACTERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"characters": characters}
    with open(CHARACTERS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


def load_races() -> list[dict[str, Any]]:
    """Загрузить список всех доступных рас.

    Returns:
        Список словарей с полями "id" и "name"
    """
    if not RACES_FILE.exists():
        return []

    try:
        with open(RACES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        races = data.get("races", {})
        result = []
        for race_id, race_info in races.items():
            result.append(
                {
                    "id": race_id,
                    "name": race_info.get("name", race_id),
                }
            )
        return result
    except (yaml.YAMLError, OSError):
        return []


def load_race_full(race_id: str) -> dict[str, Any]:
    """Загрузить полные данные расы по ID.

    Args:
        race_id: Идентификатор расы

    Returns:
        Словарь с полными данными расы или пустой словарь
    """
    if not RACES_FILE.exists():
        return {}

    try:
        with open(RACES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        races = data.get("races", {})
        race_info = races.get(race_id, {})
        if isinstance(race_info, dict):
            return race_info
        return {}
    except (yaml.YAMLError, OSError):
        return {}


def load_classes() -> list[dict[str, Any]]:
    """Загрузить список всех доступных классов.

    Returns:
        Список словарей с полями "id", "name", "description",
        "hit_dice", "prime_ability"
    """
    if not CLASSES_FILE.exists():
        return []

    try:
        with open(CLASSES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        classes = data.get("classes", {})
        result = []
        for class_id, class_info in classes.items():
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
