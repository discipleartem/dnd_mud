"""Типизированные модели данных для персонажей и приключений.

Используем dataclasses для type-safety и удобной сериализации.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Character:
    """Модель персонажа."""

    name: str
    race: str
    class_name: str
    level: int = 1
    stats: dict[str, int] = field(default_factory=dict)
    current_hp: int = 0
    experience: int = 0
    difficulty: str = "normal"
    subrace: str | None = None
    save_slug: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для сохранения в JSON."""
        data: dict[str, Any] = {
            "name": self.name,
            "race": self.race,
            "class": self.class_name,
            "level": self.level,
            "stats": self.stats,
            "current_hp": self.current_hp,
            "experience": self.experience,
            "difficulty": self.difficulty,
        }
        if self.subrace is not None:
            data["subrace"] = self.subrace
        if self.save_slug is not None:
            data["save_slug"] = self.save_slug
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Character":
        """Создать из словаря."""
        subrace = data.get("subrace")
        save_slug = data.get("save_slug")
        return cls(
            name=data.get("name", ""),
            race=data.get("race", ""),
            class_name=data.get("class", ""),
            level=data.get("level", 1),
            stats=data.get("stats", {}),
            current_hp=data.get("current_hp", 0),
            experience=data.get("experience", 0),
            difficulty=data.get("difficulty", "normal"),
            subrace=str(subrace) if subrace is not None else None,
            save_slug=str(save_slug) if save_slug is not None else None,
        )


@dataclass
class Adventure:
    """Модель приключения."""

    id: str
    name: dict[str, str] | str = field(default_factory=dict)
    description: str = ""
    difficulty: str = "normal"
    author: str = ""
    version: str = "1.0"
    allowed_game_difficulties: list[str] | None = None
    hardcore_only: bool = False

    def get_name(self, language: str = "ru") -> str:
        """Получить название на нужном языке."""
        if isinstance(self.name, dict):
            return self.name.get(language, self.name.get("en", ""))
        return str(self.name)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Adventure":
        """Создать из словаря."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", {}),
            description=data.get("description", ""),
            difficulty=data.get("difficulty", "normal"),
            author=data.get("author", ""),
            version=data.get("version", "1.0"),
            allowed_game_difficulties=data.get("allowed_game_difficulties"),
            hardcore_only=bool(data.get("hardcore_only", False)),
        )
