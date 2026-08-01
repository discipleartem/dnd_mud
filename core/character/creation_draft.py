"""Черновик незавершённого создания персонажа."""

from __future__ import annotations

import contextlib
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

from core.platform.io import load_json, save_json
from core.types import GameDifficulty, StatMap

logger = logging.getLogger(__name__)

CREATION_DRAFT_SCHEMA_VERSION = 1
CREATION_DRAFT_PATH = Path("saves") / "creation_draft.json"

CreationStep = Literal[
    "race",
    "subrace",
    "languages",
    "stats",
    "background",
    "feats",
    "class",
    "subclass",
    "proficiencies",
    "skills",
    "expertise",
    "equipment",
]

_VALID_STEPS: frozenset[str] = frozenset(
    {
        "race",
        "subrace",
        "languages",
        "stats",
        "background",
        "feats",
        "class",
        "subclass",
        "proficiencies",
        "skills",
        "expertise",
        "equipment",
    }
)


@dataclass
class CreationDraft:
    """Снимок незавершённого создания персонажа для JSON."""

    current_step: CreationStep
    name: str
    difficulty: GameDifficulty
    race_id: str | None = None
    subrace_id: str | None = None
    languages: list[str] | None = None
    stats: StatMap | None = None
    background_id: str | None = None
    background_skills: list[str] = field(default_factory=list)
    class_id: str | None = None
    subclass_id: str | None = None
    skills: list[str] | None = None
    skill_expertise: list[str] | None = None
    tool_expertise: list[str] | None = None
    weapon_proficiencies: list[str] | None = None
    armor_proficiencies: list[str] | None = None
    tool_proficiencies: list[str] | None = None
    background_tool_picks: list[str] = field(default_factory=list)
    equipment_choices: dict[str, str] = field(default_factory=dict)
    feat_ids: list[str] = field(default_factory=list)
    feat_choices: dict[str, dict[str, Any]] = field(default_factory=dict)
    hardcore_rolls: list[int] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Сериализация в JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreationDraft | None:
        """Десериализация; ``None`` при невалидных обязательных полях."""
        step_raw = data.get("current_step")
        name = data.get("name")
        if not isinstance(step_raw, str) or step_raw not in _VALID_STEPS:
            return None
        if not isinstance(name, str) or not name.strip():
            return None
        difficulty = _parse_difficulty(data.get("difficulty", "normal"))
        stats = _parse_stats(data.get("stats"))
        return cls(
            current_step=cast(CreationStep, step_raw),
            name=name.strip(),
            difficulty=difficulty,
            race_id=_optional_str(data.get("race_id")),
            subrace_id=_optional_str(data.get("subrace_id")),
            languages=_optional_str_list(data.get("languages")),
            stats=stats,
            background_id=_optional_str(data.get("background_id")),
            background_skills=_str_list(data.get("background_skills")),
            class_id=_optional_str(data.get("class_id")),
            subclass_id=_optional_str(data.get("subclass_id")),
            skills=_optional_str_list(data.get("skills")),
            skill_expertise=_optional_str_list(data.get("skill_expertise")),
            tool_expertise=_optional_str_list(data.get("tool_expertise")),
            weapon_proficiencies=_optional_str_list(
                data.get("weapon_proficiencies")
            ),
            armor_proficiencies=_optional_str_list(
                data.get("armor_proficiencies")
            ),
            tool_proficiencies=_optional_str_list(
                data.get("tool_proficiencies")
            ),
            background_tool_picks=_str_list(data.get("background_tool_picks")),
            equipment_choices=_str_str_dict(data.get("equipment_choices")),
            feat_ids=_str_list(data.get("feat_ids")),
            feat_choices=_feat_choices(data.get("feat_choices")),
            hardcore_rolls=_int_list(data.get("hardcore_rolls")),
        )


def _parse_difficulty(raw: object) -> GameDifficulty:
    if raw == "hardcore":
        return "hardcore"
    if raw == "easy":
        return "easy"
    return "normal"


def _optional_str(raw: object) -> str | None:
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw
    return str(raw)


def _optional_str_list(raw: object) -> list[str] | None:
    if raw is None:
        return None
    return _str_list(raw)


def _str_list(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw]


def _int_list(raw: object) -> list[int]:
    if not isinstance(raw, list):
        return []
    result: list[int] = []
    for item in raw:
        try:
            result.append(int(item))
        except (TypeError, ValueError):
            continue
    return result


def _str_str_dict(raw: object) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    return {str(key): str(value) for key, value in raw.items()}


def _feat_choices(raw: object) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, dict):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        if isinstance(value, dict):
            result[str(key)] = dict(value)
    return result


def _parse_stats(raw: object) -> StatMap | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return None
    required = ("str", "dex", "con", "int", "wis", "cha")
    try:
        return {key: int(raw[key]) for key in required}
    except (KeyError, TypeError, ValueError):
        return None


def has_creation_draft(path: Path | None = None) -> bool:
    """Есть ли валидный черновик создания на диске."""
    return load_creation_draft(path) is not None


def load_creation_draft(path: Path | None = None) -> CreationDraft | None:
    """Загрузить черновик; битый файл удаляется."""
    draft_path = path if path is not None else CREATION_DRAFT_PATH
    if not draft_path.exists():
        return None
    try:
        data = load_json(draft_path)
        draft = CreationDraft.from_dict(data)
        if draft is None:
            logger.warning("Невалидный черновик создания: %s", draft_path)
            clear_creation_draft(draft_path)
            return None
        return draft
    except (OSError, ValueError, TypeError) as exc:
        logger.warning("Не удалось прочитать черновик %s: %s", draft_path, exc)
        clear_creation_draft(draft_path)
        return None


def save_creation_draft(
    draft: CreationDraft, path: Path | None = None
) -> None:
    """Сохранить черновик создания."""
    draft_path = path if path is not None else CREATION_DRAFT_PATH
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    payload = draft.to_dict()
    payload["schema_version"] = CREATION_DRAFT_SCHEMA_VERSION
    save_json(draft_path, payload)


def clear_creation_draft(path: Path | None = None) -> None:
    """Удалить файл черновика, если он есть."""
    draft_path = path if path is not None else CREATION_DRAFT_PATH
    with contextlib.suppress(OSError):
        if draft_path.exists():
            draft_path.unlink()
