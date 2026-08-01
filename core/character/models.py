"""Типизированные модели данных для персонажей.

Используем dataclasses для type-safety и удобной сериализации.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, cast

from core.constants import clamp_level
from core.types import (
    CharacterClass,
    EquippedState,
    GameDifficulty,
    InventoryItem,
    StatMap,
)


def parse_character_class(raw: object) -> CharacterClass:
    """Идентификатор класса из JSON или кода."""
    if isinstance(raw, CharacterClass):
        return raw
    if raw is None or raw == "":
        raise ValueError("class_id is required")
    return CharacterClass(str(raw))


def _parse_difficulty(raw: object) -> GameDifficulty:
    """Режим сложности из JSON."""
    if raw == "hardcore":
        return "hardcore"
    if raw == "easy":
        return "easy"
    return "normal"


def _json_list[T](
    raw: object,
    convert: Callable[[object], T | None] | None = None,
) -> list[T]:
    """Список из JSON: по умолчанию str, иначе convert (None — пропуск)."""
    if not isinstance(raw, list):
        return []
    if convert is None:
        return [cast(T, str(item)) for item in raw]
    result: list[T] = []
    for item in raw:
        mapped = convert(item)
        if mapped is not None:
            result.append(mapped)
    return result


def _json_dict[V](
    raw: object,
    convert: Callable[[object], V | None] | None = None,
) -> dict[str, V]:
    """Словарь str→V из JSON (convert=None → str; None — пропуск)."""
    if not isinstance(raw, dict):
        return {}
    result: dict[str, V] = {}
    for key, value in raw.items():
        if convert is None:
            result[str(key)] = cast(V, str(value))
            continue
        mapped = convert(value)
        if mapped is not None:
            result[str(key)] = mapped
    return result


def _inventory_item(raw: object) -> InventoryItem | None:
    """Один предмет инвентаря из JSON или None."""
    if not isinstance(raw, dict):
        return None
    kind = raw.get("kind")
    item_id = raw.get("id")
    if not isinstance(kind, str) or not isinstance(item_id, str):
        return None
    entry: InventoryItem = {"kind": kind, "id": item_id}
    qty = raw.get("qty")
    if isinstance(qty, int):
        entry["qty"] = qty
    return entry


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
            self, "class_id", parse_character_class(self.class_id)
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
            "class_features_applied",
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
        equipped_raw = data.get("equipped", {})
        return cls(
            name=str(data.get("name", "")),
            race=str(data.get("race", "")),
            class_id=parse_character_class(data.get("class_id")),
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
            languages=_json_list(data.get("languages", [])),
            background_id=(
                str(background_raw) if background_raw is not None else None
            ),
            skills=_json_list(data.get("skills", [])),
            skill_expertise=_json_list(data.get("skill_expertise", [])),
            tool_expertise=_json_list(data.get("tool_expertise", [])),
            weapon_proficiencies=_json_list(
                data.get("weapon_proficiencies", [])
            ),
            armor_proficiencies=_json_list(
                data.get("armor_proficiencies", [])
            ),
            tool_proficiencies=_json_list(data.get("tool_proficiencies", [])),
            feat_ids=_json_list(data.get("feat_ids", [])),
            feat_choices=_json_dict(
                data.get("feat_choices", {}),
                convert=lambda v: v if isinstance(v, dict) else None,
            ),
            asi_choices=_json_dict(data.get("asi_choices", {})),
            save_proficiencies=_json_list(data.get("save_proficiencies", [])),
            inventory=_json_list(
                data.get("inventory", []), convert=_inventory_item
            ),
            equipped=(
                cast(EquippedState, dict(equipped_raw))
                if isinstance(equipped_raw, dict)
                else _empty_equipped()
            ),
            equipment_choices=_json_dict(data.get("equipment_choices", {})),
            class_features_applied=bool(
                data.get("class_features_applied", False)
            ),
            save_slug=str(save_slug) if save_slug is not None else None,
            created_at=str(created_at) if created_at is not None else None,
        )
