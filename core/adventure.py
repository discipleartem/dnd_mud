"""Загрузка и работа с приключениями.

Каталог приключений: database/content/adventures.yaml.
"""

from pathlib import Path

from core.io import load_yaml
from core.models import Adventure

ADVENTURES_FILE = Path("database/content/adventures.yaml")


def load_adventures() -> list[Adventure]:
    """Загрузить список приключений из YAML-файла.

    Returns:
        Список объектов Adventure
    """
    data = load_yaml(ADVENTURES_FILE)
    adventures = data.get("adventures", [])
    if not isinstance(adventures, list):
        return []
    return [Adventure.from_dict(a) for a in adventures]
