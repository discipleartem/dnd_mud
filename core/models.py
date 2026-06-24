"""Типизированные модели данных для персонажей и приключений.

Используем dataclasses для type-safety и удобной сериализации.
"""

from dataclasses import dataclass, field
from typing import Any

from core.localization import resolve_localized_text


@dataclass
class Character:
    """Модель персонажа."""

    name: str
    race: str
    class_name: str
    level: int = 1
    stats: dict[str, int] = field(default_factory=dict)
    current_hp: int = 0
    max_hp: int = 0
    experience: int = 0
    difficulty: str = "normal"
    subrace: str | None = None
    save_slug: str | None = None
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для сохранения в JSON."""
        data: dict[str, Any] = {
            "name": self.name,
            "race": self.race,
            "class": self.class_name,
            "level": self.level,
            "stats": self.stats,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "experience": self.experience,
            "difficulty": self.difficulty,
        }
        if self.subrace is not None:
            data["subrace"] = self.subrace
        if self.save_slug is not None:
            data["save_slug"] = self.save_slug
        if self.created_at is not None:
            data["created_at"] = self.created_at
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Character":
        """Создать из словаря."""
        subrace = data.get("subrace")
        save_slug = data.get("save_slug")
        created_at = data.get("created_at")
        current_hp = int(data.get("current_hp", 0))
        max_hp_raw = data.get("max_hp")
        max_hp = int(max_hp_raw) if max_hp_raw is not None else current_hp
        return cls(
            name=data.get("name", ""),
            race=data.get("race", ""),
            class_name=data.get("class", ""),
            level=data.get("level", 1),
            stats=data.get("stats", {}),
            current_hp=current_hp,
            max_hp=max_hp,
            experience=data.get("experience", 0),
            difficulty=data.get("difficulty", "normal"),
            subrace=str(subrace) if subrace is not None else None,
            save_slug=str(save_slug) if save_slug is not None else None,
            created_at=str(created_at) if created_at is not None else None,
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
    min_level: int = 1

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
            difficulty=data.get("difficulty", "normal"),
            author=data.get("author", ""),
            version=data.get("version", "1.0"),
            allowed_game_difficulties=data.get("allowed_game_difficulties"),
            hardcore_only=bool(data.get("hardcore_only", False)),
            min_level=int(data.get("min_level", 1)),
        )
