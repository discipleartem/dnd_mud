"""Загрузка и работа с приключениями.

Приключения хранятся в YAML-файле database/adventures.yaml.
"""

from pathlib import Path

import yaml

from core.models import Adventure

ADVENTURES_FILE = Path("database/content/adventures.yaml")


def load_adventures() -> list[Adventure]:
    """Загрузить список приключений из YAML-файла.

    Returns:
        Список объектов Adventure
    """
    if not ADVENTURES_FILE.exists():
        return []

    try:
        with open(ADVENTURES_FILE, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        adventures = data.get("adventures", [])
        return [Adventure.from_dict(a) for a in adventures]
    except (yaml.YAMLError, OSError):
        return []
