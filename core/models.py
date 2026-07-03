"""Типизированные модели данных для персонажей и приключений.

Используем dataclasses для type-safety и удобной сериализации.
"""

from dataclasses import dataclass, field
from typing import Any, cast

from core.levels import clamp_level
from core.localization import resolve_localized_text
from core.types import (
    CharacterClass,
    EquippedState,
    GameDifficulty,
    InventoryItem,
    StatMap,
)


def _parse_character_class(raw: object) -> CharacterClass:
    """Идентификатор класса из JSON или кода."""
    if isinstance(raw, CharacterClass):
        return raw
    if raw is None or raw == "":
        raise ValueError("class_id is required")
    return CharacterClass(str(raw))


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


def _coerce_inventory(raw: object) -> list[InventoryItem]:
    """Инвентарь из JSON."""
    if not isinstance(raw, list):
        return []
    items: list[InventoryItem] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        item_id = item.get("id")
        if not isinstance(kind, str) or not isinstance(item_id, str):
            continue
        entry: InventoryItem = {"kind": kind, "id": item_id}
        qty = item.get("qty")
        if isinstance(qty, int):
            entry["qty"] = qty
        items.append(entry)
    return items


def _coerce_equipped(raw: object) -> EquippedState:
    """Экипировка из JSON."""
    if isinstance(raw, dict):
        return cast(EquippedState, dict(raw))
    return {}


def _empty_equipped() -> EquippedState:
    return cast(EquippedState, {})


@dataclass
class Character:
    """Модель персонажа."""

    name: str
    race: str
    class_id: CharacterClass
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
    inventory: list[InventoryItem] = field(default_factory=list)
    equipped: EquippedState = field(default_factory=_empty_equipped)
    equipment_choices: dict[str, str] = field(default_factory=dict)
    class_features_applied: bool = False
    save_slug: str | None = None
    created_at: str | None = None

    def __post_init__(self) -> None:
        """Привести class_id к enum при создании из str."""
        object.__setattr__(
            self, "class_id", _parse_character_class(self.class_id)
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализовать в словарь для сохранения в JSON.

        Использует dataclass.asdict() с фильтрацией None/пустых значений
        для уменьшения дублирования кода.
        """
        from dataclasses import asdict

        base = asdict(self)
        # Преобразовать class_id в строку для совместимости с JSON
        base["class_id"] = str(self.class_id)

        # Убрать поля с None/пустыми значениями по умолчанию
        # Исключаем обязательные поля и специфические значения
        optional_fields = {
            "subrace",
            "subclass_id",
            "languages",
            "background_id",
            "skills",
            "skill_expertise",
            "tool_expertise",
            "weapon_proficiencies",
            "armor_proficiencies",
            "tool_proficiencies",
            "feat_ids",
            "feat_choices",
            "asi_choices",
            "save_proficiencies",
            "inventory",
            "equipped",
            "equipment_choices",
            "save_slug",
            "created_at",
        }

        result: dict[str, Any] = {}
        for key, value in base.items():
            if key in optional_fields:
                if value is None or value == [] or value == {}:
                    continue
                # class_features_applied — False по умолчанию, не сериализуем
                if key == "class_features_applied" and not value:
                    continue
            result[key] = value

        return result

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
            class_id=_parse_character_class(data.get("class_id")),
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
