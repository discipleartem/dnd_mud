"""Загрузка и модель приключений.

Каталог приключений: database/content/adventures.yaml.
"""

from dataclasses import dataclass, field
from typing import Any

from core.platform.io import load_yaml
from core.platform.localization import resolve_localized_text
from core.platform.paths import ADVENTURES_FILE


@dataclass
class Adventure:
    """Модель приключения."""

    id: str
    name: dict[str, str] | str = field(default_factory=dict)
    description: str = ""
    content_tier: str = "normal"
    author: str = ""
    version: str = "1.0"
    allowed_game_difficulties: list[str] | None = None
    hardcore_only: bool = False
    min_level: int = 1
    script_file: str = ""

    def get_name(self, language: str = "ru") -> str:
        """Получить название на нужном языке."""
        return resolve_localized_text(self.name, language)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Adventure":
        """Создать из словаря."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", {}),
            description=data.get("description", ""),
            content_tier=data.get("content_tier", "normal"),
            author=data.get("author", ""),
            version=data.get("version", "1.0"),
            allowed_game_difficulties=data.get("allowed_game_difficulties"),
            hardcore_only=bool(data.get("hardcore_only", False)),
            min_level=int(data.get("min_level", 1)),
            script_file=str(data.get("script_file", "")),
        )


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
