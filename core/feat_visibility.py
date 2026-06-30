"""Скрытие черт в меню выбора по происхождению персонажа.

Единственная ответственность: решить, показывать ли черту в списке выбора
с учётом расы, подрасы, класса, подкласса и уже известных владений.
Проверка требований (ability score и т.д.) — в ``core.feats``.
"""

from typing import Any

from core.classes import character_has_spellcasting
from core.feats_loader import FeatRequirementContext, load_feat
from core.grant_mechanics import normalize_armor_token
from core.types import StatMap

__all__ = [
    "build_feat_selection_context",
    "build_feat_selection_context_from_character",
    "creation_known_for_feat_picks",
    "feat_visible_for_selection",
]

_PROFICIENCY_GRANT_TYPES = frozenset(
    {
        "weapon_proficiency",
        "armor_proficiency",
        "skill_proficiency",
        "tool_proficiency",
        "multiple_proficiency",
        "bonus_proficiencies",
    }
)


def creation_known_for_feat_picks(
    race_id: str,
    subrace_id: str | None,
    background_id: str | None,
    class_id: str,
    subclass_id: str | None,
    level: int,
) -> tuple[list[str], list[str], list[str]]:
    """Навыки, инструменты и токены оружия до подвыборов внутри черты."""
    from core.character_builder import resolve_creation_grants

    grants = resolve_creation_grants(
        race_id,
        subrace_id,
        class_id,
        background_id,
        subclass_id,
        level,
        include_feat_languages=False,
    )
    return (
        list(grants.skill_ids),
        list(grants.tool_tokens),
        list(grants.weapon_tokens),
    )


def build_feat_selection_context(
    stats: StatMap,
    race_id: str,
    subrace_id: str | None,
    background_id: str | None,
    class_id: str,
    subclass_id: str | None,
    level: int,
    *,
    skills: list[str] | None = None,
    weapon_tokens: list[str] | None = None,
    tool_tokens: list[str] | None = None,
) -> FeatRequirementContext:
    """Контекст видимости и требований черт на шаге создания (после класса).

    Опциональные ``skills`` / ``weapon_tokens`` / ``tool_tokens`` дополняют
    владения расы, класса и предыстории (например, от уже выбранных черт).
    """
    from core.character_builder import resolve_creation_grants

    grants = resolve_creation_grants(
        race_id,
        subrace_id,
        class_id,
        background_id,
        subclass_id,
        level,
        extra_skills=skills,
        extra_weapon_tokens=weapon_tokens,
        extra_tool_tokens=tool_tokens,
        include_feat_languages=False,
    )
    return FeatRequirementContext(
        stats=stats,
        weapon_tokens=list(grants.weapon_tokens),
        armor_tokens=list(grants.armor_tokens),
        tool_tokens=list(grants.tool_tokens),
        race_id=race_id,
        subrace_id=subrace_id,
        background_id=background_id,
        class_id=class_id,
        subclass_id=subclass_id,
        level=level,
        has_spellcasting=character_has_spellcasting(
            class_id, subclass_id, level
        ),
        skills=list(grants.skill_ids),
    )


def build_feat_selection_context_from_character(
    character: Any,
) -> FeatRequirementContext:
    """Контекст видимости и требований черт при левелапе."""
    return FeatRequirementContext(
        stats=character.stats,
        weapon_tokens=list(character.weapon_proficiencies),
        armor_tokens=list(character.armor_proficiencies),
        tool_tokens=list(character.tool_proficiencies),
        race_id=character.race,
        subrace_id=character.subrace,
        background_id=getattr(character, "background_id", None),
        class_id=character.class_id,
        subclass_id=character.subclass_id,
        level=character.level + 1,
        has_spellcasting=character_has_spellcasting(
            character.class_id,
            character.subclass_id,
            character.level + 1,
        ),
        skills=list(character.skills),
    )


def _armor_tokens_from_grant(grant: dict[str, Any]) -> list[str]:
    raw = grant.get("armor_types", grant.get("armors", []))
    if not isinstance(raw, list):
        return []
    return [normalize_armor_token(str(armor)) for armor in raw]


def _grant_adds_new_proficiency(
    grant: dict[str, Any], ctx: FeatRequirementContext
) -> bool:
    """Даёт ли grant новое владение относительно контекста."""
    from core.equipment import all_tool_ids, all_weapon_ids
    from core.proficiencies import has_tool_proficiency, has_weapon_proficiency
    from core.skills import PHB_SKILL_IDS

    mtype = str(grant.get("type", ""))
    if mtype not in _PROFICIENCY_GRANT_TYPES:
        return True

    if mtype == "bonus_proficiencies":
        weapons_new = False
        armors_new = False
        raw_w = grant.get("weapons", [])
        if grant.get("choice"):
            weapons_new = any(
                not has_weapon_proficiency(ctx.weapon_tokens, weapon_id)
                for weapon_id in all_weapon_ids()
            )
        elif isinstance(raw_w, list) and raw_w:
            weapons_new = any(
                not has_weapon_proficiency(ctx.weapon_tokens, str(weapon_id))
                for weapon_id in raw_w
            )
        armors = _armor_tokens_from_grant(grant)
        if armors:
            armors_new = any(armor not in ctx.armor_tokens for armor in armors)
        if isinstance(raw_w, list) and raw_w or grant.get("choice"):
            if armors:
                return weapons_new or armors_new
            return weapons_new
        if armors:
            return armors_new
        return True

    if mtype == "armor_proficiency":
        armors = _armor_tokens_from_grant(grant)
        if not armors:
            return True
        return any(armor not in ctx.armor_tokens for armor in armors)

    if mtype == "weapon_proficiency":
        if grant.get("choice"):
            return any(
                not has_weapon_proficiency(ctx.weapon_tokens, weapon_id)
                for weapon_id in all_weapon_ids()
            )
        raw = grant.get("weapons", [])
        if not isinstance(raw, list) or not raw:
            return True
        return any(
            not has_weapon_proficiency(ctx.weapon_tokens, str(weapon_id))
            for weapon_id in raw
        )

    if mtype == "skill_proficiency":
        grant_skills: list[str] = []
        raw = grant.get("skills", [])
        if isinstance(raw, list):
            grant_skills.extend(str(skill) for skill in raw)
        skill_one = grant.get("skill")
        if isinstance(skill_one, str) and skill_one:
            grant_skills.append(skill_one)
        if not grant_skills:
            if grant.get("choice"):
                return any(skill not in ctx.skills for skill in PHB_SKILL_IDS)
            return True
        return any(skill not in ctx.skills for skill in grant_skills)

    if mtype == "tool_proficiency":
        if grant.get("choice"):
            return any(
                not has_tool_proficiency(ctx.tool_tokens, tool_id)
                for tool_id in all_tool_ids()
            )
        raw = grant.get("tools", [])
        if not isinstance(raw, list) or not raw:
            return True
        return any(
            not has_tool_proficiency(ctx.tool_tokens, str(tool_id))
            for tool_id in raw
        )

    if mtype == "multiple_proficiency":
        skill_available = any(
            skill not in ctx.skills for skill in PHB_SKILL_IDS
        )
        tool_available = any(
            not has_tool_proficiency(ctx.tool_tokens, tool_id)
            for tool_id in all_tool_ids()
        )
        return skill_available or tool_available

    return True


def feat_visible_for_selection(
    feat_id: str, ctx: FeatRequirementContext
) -> bool:
    """Показывать ли черту в меню выбора (не скрыта по владениям)."""
    feat = load_feat(feat_id)
    raw_grants = feat.get("grants", [])
    if not isinstance(raw_grants, list) or not raw_grants:
        return True
    return any(
        _grant_adds_new_proficiency(grant, ctx)
        for grant in raw_grants
        if isinstance(grant, dict)
    )
