"""Загрузка классов персонажей из YAML."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.io import load_yaml

CLASSES_FILE = Path("database/classes/classes.yaml")


@lru_cache(maxsize=1)
def _load_classes_yaml() -> dict[str, Any]:
    """Загрузить и закэшировать данные классов из YAML."""
    data = load_yaml(CLASSES_FILE)
    classes = data.get("classes", {})
    if isinstance(classes, dict):
        return classes
    return {}


def get_class_hit_dice(class_id: str) -> int:
    """Получить кость здоровья класса."""
    class_info = _load_classes_yaml().get(class_id, {})
    if not isinstance(class_info, dict):
        return 8
    hit_dice = class_info.get("hit_dice", 8)
    if isinstance(hit_dice, int):
        return hit_dice
    return 8


def load_classes() -> list[dict[str, Any]]:
    """Загрузить список всех доступных классов."""
    result: list[dict[str, Any]] = []
    for class_id, class_info in _load_classes_yaml().items():
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
