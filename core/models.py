"""Типизированные модели данных для персонажей и приключений.

Используем dataclasses для type-safety и удобной сериализации.
"""

from dataclasses import dataclass, field
from typing import Any

from core.levels import clamp_level
from core.localization import resolve_localized_text
from core.types import GameDifficulty, StatMap


def _coerce_str_list(raw: object) -> list[str]:
    """Список строк из JSON."""
    if isinstance(raw, list):
        return [str(item) for item in raw]
    return []


def _coerce_str_dict(raw: object) -> dict[str, str]:
    """Словарь str→str из JSON."""
    if isinstance(raw, dict):
        return {str(key): str(value) for key, value in raw.items()}
    return {}


def _coerce_feat_choices(raw: object) -> dict[str, dict[str, Any]]:
    """feat_choices из JSON."""
    if not isinstance(raw, dict):
        return {}
    return {
        str(key): value
        for key, value in raw.items()
        if isinstance(value, dict)
    }


def _parse_difficulty(raw: object) -> GameDifficulty:
    """Режим сложности из JSON."""
    if raw == "hardcore":
        return "hardcore"
    if raw == "easy":
        return "easy"
    return "normal"


def _coerce_inventory(raw: object) -> list[dict[str, Any]]:
    """Инвентарь из JSON."""
    if not isinstance(raw, list):
        return []
    return [dict(item) for item in raw if isinstance(item, dict)]


def _coerce_equipped(raw: object) -> dict[str, Any]:
    """Экипировка из JSON."""
    if isinstance(raw, dict):
        return dict(raw)
    return {}


@dataclass
class Character:
    """Модель персонажа."""

    name: str
    race: str
    class_id: str
    level: int = 1
    stats: StatMap = field(default_factory=dict)
    current_hp: int = 0
    max_hp: int = 0
    experience: int = 0
    difficulty: GameDifficulty = "normal"
    subrace: str | None = None
    subclass_id: str | None = None
    languages: list[str] = field(default_factory=list)
    background_id: str | None = None
    skills: list[str] = field(default_factory=list)
    skill_expertise: list[str] = field(default_factory=list)
    tool_expertise: list[str] = field(default_factory=list)
    weapon_proficiencies: list[str] = field(default_factory=list)
    armor_proficiencies: list[str] = field(default_factory=list)
    tool_proficiencies: list[str] = field(default_factory=list)
    feat_ids: list[str] = field(default_factory=list)
    feat_choices: dict[str, dict[str, Any]] = field(default_factory=dict)
    asi_choices: dict[str, str] = field(default_factory=dict)
    save_proficiencies: list[str] = field(default_factory=list)
    inventory: list[dict[str, Any]] = field(default_factory=list)
    equipped: dict[str, Any] = field(default_factory=dict)
    equipment_choices: dict[str, str] = field(default_factory=dict)
    class_features_applied: bool = False
    save_slug: str | None = None
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для сохранения в JSON."""
        data: dict[str, Any] = {
            "name": self.name,
            "race": self.race,
            "class_id": self.class_id,
            "level": self.level,
            "stats": self.stats,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "experience": self.experience,
            "difficulty": self.difficulty,
        }
        if self.subrace is not None:
            data["subrace"] = self.subrace
        if self.subclass_id is not None:
            data["subclass_id"] = self.subclass_id
        if self.languages:
            data["languages"] = self.languages
        if self.background_id is not None:
            data["background_id"] = self.background_id
        if self.skills:
            data["skills"] = self.skills
        if self.skill_expertise:
            data["skill_expertise"] = self.skill_expertise
        if self.tool_expertise:
            data["tool_expertise"] = self.tool_expertise
        if self.weapon_proficiencies:
            data["weapon_proficiencies"] = self.weapon_proficiencies
        if self.armor_proficiencies:
            data["armor_proficiencies"] = self.armor_proficiencies
        if self.tool_proficiencies:
            data["tool_proficiencies"] = self.tool_proficiencies
        if self.feat_ids:
            data["feat_ids"] = self.feat_ids
        if self.feat_choices:
            data["feat_choices"] = self.feat_choices
        if self.asi_choices:
            data["asi_choices"] = self.asi_choices
        if self.save_proficiencies:
            data["save_proficiencies"] = self.save_proficiencies
        if self.inventory:
            data["inventory"] = self.inventory
        if self.equipped:
            data["equipped"] = self.equipped
        if self.equipment_choices:
            data["equipment_choices"] = self.equipment_choices
        if self.class_features_applied:
            data["class_features_applied"] = True
        if self.save_slug is not None:
            data["save_slug"] = self.save_slug
        if self.created_at is not None:
            data["created_at"] = self.created_at
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Character":
        """Создать из словаря."""
        subrace = data.get("subrace")
        current_hp = int(data.get("current_hp", 0))
        max_hp_raw = data.get("max_hp")
        max_hp = int(max_hp_raw) if max_hp_raw is not None else current_hp
        save_slug = data.get("save_slug")
        created_at = data.get("created_at")
        subclass_raw = data.get("subclass_id")
        background_raw = data.get("background_id")
        return cls(
            name=str(data.get("name", "")),
            race=str(data.get("race", "")),
            class_id=str(data.get("class_id") or ""),
            level=clamp_level(int(data.get("level", 1))),
            stats=data.get("stats", {}),
            current_hp=current_hp,
            max_hp=max_hp,
            experience=int(data.get("experience", 0)),
            difficulty=_parse_difficulty(data.get("difficulty", "normal")),
            subrace=str(subrace) if subrace is not None else None,
            subclass_id=(
                str(subclass_raw) if subclass_raw is not None else None
            ),
            languages=_coerce_str_list(data.get("languages", [])),
            background_id=(
                str(background_raw) if background_raw is not None else None
            ),
            skills=_coerce_str_list(data.get("skills", [])),
            skill_expertise=_coerce_str_list(data.get("skill_expertise", [])),
            tool_expertise=_coerce_str_list(data.get("tool_expertise", [])),
            weapon_proficiencies=_coerce_str_list(
                data.get("weapon_proficiencies", [])
            ),
            armor_proficiencies=_coerce_str_list(
                data.get("armor_proficiencies", [])
            ),
            tool_proficiencies=_coerce_str_list(
                data.get("tool_proficiencies", [])
            ),
            feat_ids=_coerce_str_list(data.get("feat_ids", [])),
            feat_choices=_coerce_feat_choices(data.get("feat_choices", {})),
            asi_choices=_coerce_str_dict(data.get("asi_choices", {})),
            save_proficiencies=_coerce_str_list(
                data.get("save_proficiencies", [])
            ),
            inventory=_coerce_inventory(data.get("inventory", [])),
            equipped=_coerce_equipped(data.get("equipped", {})),
            equipment_choices=_coerce_str_dict(
                data.get("equipment_choices", {})
            ),
            class_features_applied=bool(
                data.get("class_features_applied", False)
            ),
            save_slug=str(save_slug) if save_slug is not None else None,
            created_at=str(created_at) if created_at is not None else None,
        )


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
