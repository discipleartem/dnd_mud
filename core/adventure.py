"""Загрузка и работа с приключениями.

Приключения хранятся в YAML-файле database/adventures.yaml.
"""

from pathlib import Path

import yaml

ADVENTURES_FILE = Path("database/adventures.yaml")

# Названия сложностей на разных языках
DIFFICULTY_NAMES = {
    "ru": {
        "easy": "лёгкая",
        "normal": "нормальная",
        "hardcore": "хардкор",
        "training": "обучение",
    },
    "en": {
        "easy": "easy",
        "normal": "normal",
        "hardcore": "hardcore",
        "training": "training",
    },
}


def load_adventures() -> list[dict]:
    """Загрузить список приключений из YAML-файла.

    Returns:
        Список словарей с данными приключений
    """
    if not ADVENTURES_FILE.exists():
        return []

    try:
        with open(ADVENTURES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("adventures", [])
    except (yaml.YAMLError, OSError):
        return []


def get_adventure_name(adventure: dict, language: str = "ru") -> str:
    """Получить название приключения на нужном языке.

    В YAML название может быть словарём {"ru": "...", "en": "..."}.

    Args:
        adventure: Словарь с данными приключения
        language: Код языка ('ru' или 'en')

    Returns:
        Название приключения
    """
    name = adventure.get("name", "")
    if isinstance(name, dict):
        return name.get(language, name.get("en", str(name)))
    return str(name)


def get_difficulty_name(difficulty: str, language: str = "ru") -> str:
    """Получить название сложности на нужном языке.

    Args:
        difficulty: Код сложности ('easy', 'normal', 'hardcore', 'training')
        language: Код языка ('ru' или 'en')

    Returns:
        Название сложности
    """
    lang_dict = DIFFICULTY_NAMES.get(language, DIFFICULTY_NAMES["en"])
    return lang_dict.get(difficulty, difficulty)