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

# Русские названия характеристик (если нет локализации)
STAT_NAMES_RU = {
    "strength": "Сила",
    "dexterity": "Ловкость",
    "constitution": "Телосложение",
    "intelligence": "Интеллект",
    "wisdom": "Мудрость",
    "charisma": "Харизма",
}


def create_character(name: str, race_id: str, class_id: str) -> dict[str, Any]:
    """Создать нового персонажа и сохранить в YAML.

    Персонаж получает:
    - характеристики из стандартного массива + расовые бонусы
    - хиты 1-го уровня (кость здоровья класса + модификатор Телосложения)

    Args:
        name: Имя персонажа
        race_id: ID расы (например, 'human', 'elf')
        class_id: ID класса (например, 'fighter', 'wizard')

    Returns:
        Словарь с данными нового персонажа
    """
    stats = _generate_stats(race_id)
    hit_dice = _get_class_hit_dice(class_id)
    con_mod = ability_modifier(stats.get("constitution", 10))
    hp = hit_dice + con_mod

    character = {
        "name": name,
        "race": race_id,
        "class": class_id,
        "level": 1,
        "stats": stats,
        "current_hp": hp,
        "experience": 0,
    }

    # Сохраняем
    characters = load_characters()
    characters.append(character)
    _save_characters(characters)

    return character


def _generate_stats(race_id: str) -> dict[str, int]:
    """Сгенерировать характеристики: массив + расовые бонусы.

    Берём стандартный массив [15, 14, 13, 12, 10, 8],
    сортируем по убыванию, назначаем всем шести характеристикам,
    потом добавляем расовые бонусы.

    Args:
        race_id: ID расы

    Returns:
        Словарь {название_характеристики: значение}
    """
    sorted_array = sorted(STANDARD_ARRAY, reverse=True)
    stats = dict(zip(STAT_NAMES, sorted_array, strict=True))

    bonuses = _get_race_bonuses(race_id)
    for stat_name, bonus in bonuses.items():
        if stat_name in stats:
            stats[stat_name] += bonus

    return stats


def _get_race_bonuses(race_id: str) -> dict[str, int]:
    """Получить расовые бонусы к характеристикам.

    Например, для дварфа: +2 к Телосложению.

    Args:
        race_id: ID расы

    Returns:
        Словарь {название_характеристики: бонус}
    """
    try:
        with open(RACES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        races = data.get("races", {})
        race_info = races.get(race_id, {})
        bonuses = race_info.get("ability_bonuses", {})
        if isinstance(bonuses, dict):
            return bonuses
        return {}
    except (yaml.YAMLError, OSError):
        return {}


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


def character_exists(name: str) -> bool:
    """Проверить, существует ли персонаж с таким именем.

    Args:
        name: Имя персонажа

    Returns:
        True если персонаж с таким именем уже есть
    """
    characters = load_characters()
    return any(c.get("name", "").lower() == name.lower() for c in characters)


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


def get_stat_name(stat_key: str, language: str = "ru") -> str:
    """Получить название характеристики на нужном языке.

    Args:
        stat_key: Ключ характеристики ('strength', 'dexterity' и т.д.)
        language: Код языка ('ru', 'en')

    Returns:
        Название характеристики
    """
    if language == "en":
        english_names = {
            "strength": "Strength",
            "dexterity": "Dexterity",
            "constitution": "Constitution",
            "intelligence": "Intelligence",
            "wisdom": "Wisdom",
            "charisma": "Charisma",
        }
        return english_names.get(stat_key, stat_key)
    return STAT_NAMES_RU.get(stat_key, stat_key)
