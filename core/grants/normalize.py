"""Нормализация grants из YAML."""

from collections.abc import Callable
from typing import Any

from core.catalogs.skill_ids import PHB_SKILL_IDS

ABILITY_INCREASE = "ability_increase"

_ProficiencyTokensHandler = Callable[
    [dict[str, Any], dict[str, Any]],
    tuple[list[str], list[str], list[str], list[str]],
]


def _coerce_bool(value: Any, default: bool = True) -> bool:
    """Привести значение к bool."""
    if isinstance(value, bool):
        return value
    return default


def inherit_flags(entity: dict[str, Any]) -> tuple[bool, bool]:
    """Флаги наследования подрасы: ability_bonuses, grants."""
    inherit = entity.get("inherit")
    if isinstance(inherit, dict):
        return (
            _coerce_bool(inherit.get("ability_bonuses"), True),
            _coerce_bool(inherit.get("grants"), True),
        )
    return True, True


def grants_from_entity(entity: dict[str, Any]) -> list[dict[str, Any]]:
    """Grants сущности из ключа grants."""
    raw_grants = entity.get("grants", [])
    if not isinstance(raw_grants, list):
        return []
    return [dict(g) for g in raw_grants if isinstance(g, dict)]


def merge_entity_grants(
    parent: dict[str, Any] | None,
    entity: dict[str, Any],
    *,
    use_parent: bool,
) -> list[dict[str, Any]]:
    """Grants подрасы с учётом наследования от базовой расы."""
    _, inherit_grants = inherit_flags(entity)
    merged: list[dict[str, Any]] = []
    if use_parent and parent and inherit_grants:
        merged.extend(grants_from_entity(parent))
    merged.extend(grants_from_entity(entity))
    return merged


def grant_type(grant: dict[str, Any]) -> str:
    """Тип grant после нормализации."""
    return str(grant.get("type", ""))


def grants_of_type(
    grants: list[dict[str, Any]], type_name: str
) -> list[dict[str, Any]]:
    """Отфильтровать grants по type."""
    return [g for g in grants if grant_type(g) == type_name]


_ARMOR_ALIASES: dict[str, str] = {
    "light_armor": "light",
    "medium_armor": "medium",
    "heavy_armor": "heavy",
}


def normalize_armor_token(token: str) -> str:
    """Привести токен доспеха к light/medium/heavy/shield."""
    return _ARMOR_ALIASES.get(token, token)


def armor_tokens_from_grant(grant: dict[str, Any]) -> list[str]:
    """Нормализованные токены доспехов из grant."""
    raw = grant.get("armor_types", grant.get("armors", []))
    if not isinstance(raw, list):
        return []
    return [normalize_armor_token(str(armor)) for armor in raw]


def mechanics_from_grant_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Плоский grant или mechanics из class feature."""
    if "mechanics" in entry:
        merged = (
            dict(entry["mechanics"])
            if isinstance(entry["mechanics"], dict)
            else {}
        )
        if entry.get("type") and "type" not in merged:
            merged["type"] = entry["type"]
        return merged
    return dict(entry)


def _extend_weapon_tokens(
    grant: dict[str, Any],
    choices: dict[str, Any],
    weapons: list[str],
) -> None:
    """Дополнить список токенов оружия из weapon/bonus grant."""
    if grant.get("choice"):
        raw = choices.get("weapons", [])
        if isinstance(raw, list):
            weapons.extend(str(w) for w in raw)
    else:
        raw = grant.get("weapons", [])
        if isinstance(raw, list):
            weapons.extend(str(w) for w in raw)


def _extend_armor_tokens(grant: dict[str, Any], armors: list[str]) -> None:
    """Дополнить список токенов доспехов из armor/bonus grant."""
    raw = grant.get("armor_types", grant.get("armors", []))
    if isinstance(raw, list):
        armors.extend(normalize_armor_token(str(a)) for a in raw)


def _tokens_from_weapon_proficiency(
    grant: dict[str, Any],
    choices: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Оружие из grant weapon_proficiency."""
    weapons: list[str] = []
    _extend_weapon_tokens(grant, choices, weapons)
    return weapons, [], [], []


def _tokens_from_armor_proficiency(
    grant: dict[str, Any],
    choices: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Доспехи и оружие из grant armor_proficiency."""
    weapons: list[str] = []
    armors: list[str] = []
    _extend_armor_tokens(grant, armors)
    raw_w = grant.get("weapons", [])
    if isinstance(raw_w, list):
        weapons.extend(str(w) for w in raw_w)
    return weapons, armors, [], []


def _tokens_from_bonus_proficiencies(
    grant: dict[str, Any],
    choices: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Оружие и доспехи из grant bonus_proficiencies."""
    weapons: list[str] = []
    armors: list[str] = []
    _extend_weapon_tokens(grant, choices, weapons)
    _extend_armor_tokens(grant, armors)
    return weapons, armors, [], []


def _tokens_from_tool_proficiency(
    grant: dict[str, Any],
    choices: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Инструменты из grant tool_proficiency (без choice)."""
    tools: list[str] = []
    if not grant.get("choice"):
        raw = grant.get("tools", [])
        if isinstance(raw, list):
            tools.extend(str(t) for t in raw)
    return [], [], tools, []


def _tokens_from_skill_proficiency(
    grant: dict[str, Any],
    choices: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Навыки из grant skill_proficiency."""
    skills: list[str] = []
    raw = grant.get("skills", [])
    if isinstance(raw, list):
        skills.extend(str(s) for s in raw)
    skill_one = grant.get("skill")
    if isinstance(skill_one, str) and skill_one:
        skills.append(skill_one)
    return [], [], [], skills


def _tokens_from_multiple_proficiency(
    grant: dict[str, Any],
    choices: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Навыки и инструменты из grant multiple_proficiency."""
    tools: list[str] = []
    skills: list[str] = []
    raw = choices.get("skills_tools", [])
    if isinstance(raw, list):
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            kind = entry.get("type", "skill")
            item_id = str(entry.get("id", ""))
            if kind == "tool":
                tools.append(item_id)
            elif item_id in PHB_SKILL_IDS:
                skills.append(item_id)
    return [], [], tools, skills


def _tokens_from_skill_expertise(
    grant: dict[str, Any],
    choices: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Навыки из grant skill_expertise."""
    skills: list[str] = []
    raw = choices.get("expertise", [])
    if isinstance(raw, list):
        for item_id in raw:
            sid = str(item_id)
            if sid in PHB_SKILL_IDS:
                skills.append(sid)
    return [], [], [], skills


_PROFICIENCY_TOKEN_HANDLERS: dict[str, _ProficiencyTokensHandler] = {
    "weapon_proficiency": _tokens_from_weapon_proficiency,
    "armor_proficiency": _tokens_from_armor_proficiency,
    "bonus_proficiencies": _tokens_from_bonus_proficiencies,
    "tool_proficiency": _tokens_from_tool_proficiency,
    "skill_proficiency": _tokens_from_skill_proficiency,
    "multiple_proficiency": _tokens_from_multiple_proficiency,
    "skill_expertise": _tokens_from_skill_expertise,
}


def proficiency_tokens_and_skills_from_grant(
    grant: dict[str, Any],
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Оружие, доспехи, инструменты и навыки из grant."""
    choices = choices or {}
    mtype = str(grant.get("type", ""))
    handler = _PROFICIENCY_TOKEN_HANDLERS.get(mtype)
    if handler is None:
        return [], [], [], []
    return handler(grant, choices)


def proficiency_tokens_from_grant(
    grant: dict[str, Any],
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Оружие, доспехи и инструменты из grant."""
    w, a, t, _ = proficiency_tokens_and_skills_from_grant(grant, choices)
    return w, a, t
