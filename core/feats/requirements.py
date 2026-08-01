"""Требования и видимость черт при выборе."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from core.catalogs.classes import character_has_spellcasting
from core.catalogs.equipment import all_tool_ids, all_weapon_ids
from core.catalogs.skill_ids import PHB_SKILL_IDS
from core.character.models import Character
from core.feats.catalog import load_feat, load_feats
from core.grants.context import CreationContext
from core.grants.normalize import proficiency_tokens_and_skills_from_grant
from core.grants.resolve import resolve_grants_for_context
from core.mechanics.proficiencies import (
    has_tool_proficiency,
    has_weapon_proficiency,
)
from core.types import StatMap

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


@dataclass(frozen=True)
class FeatRequirementContext:
    """Контекст для проверки требований черты."""

    stats: StatMap
    weapon_tokens: list[str]
    armor_tokens: list[str]
    tool_tokens: list[str]
    race_id: str | None = None
    subrace_id: str | None = None
    background_id: str | None = None
    class_id: str | None = None
    subclass_id: str | None = None
    level: int = 1
    has_spellcasting: bool = False
    skills: list[str] = field(default_factory=list)


def _creation_context(
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
) -> CreationContext:
    return CreationContext(
        race_id=race_id,
        subrace_id=subrace_id,
        class_id=class_id,
        background_id=background_id,
        subclass_id=subclass_id,
        level=level,
        extra_skills=tuple(skills) if skills else (),
        extra_weapon_tokens=tuple(weapon_tokens) if weapon_tokens else (),
        extra_tool_tokens=tuple(tool_tokens) if tool_tokens else (),
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
    ctx = _creation_context(
        race_id, subrace_id, background_id, class_id, subclass_id, level
    )
    grants = resolve_grants_for_context(ctx)
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
    ctx = _creation_context(
        race_id,
        subrace_id,
        background_id,
        class_id,
        subclass_id,
        level,
        skills=skills,
        weapon_tokens=weapon_tokens,
        tool_tokens=tool_tokens,
    )
    grants = resolve_grants_for_context(ctx)
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
    character: Character,
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


def _any_new_weapon(
    ctx: FeatRequirementContext, weapon_ids: list[str]
) -> bool:
    return any(
        not has_weapon_proficiency(ctx.weapon_tokens, weapon_id)
        for weapon_id in weapon_ids
    )


def _any_new_tool(ctx: FeatRequirementContext, tool_ids: list[str]) -> bool:
    return any(
        not has_tool_proficiency(ctx.tool_tokens, tool_id)
        for tool_id in tool_ids
    )


def _any_new_armor(ctx: FeatRequirementContext, grant: dict[str, Any]) -> bool:
    _, armors, _, _ = proficiency_tokens_and_skills_from_grant(grant)
    if not armors:
        return True
    return any(armor not in ctx.armor_tokens for armor in armors)


def _grant_adds_new_bonus_proficiencies(
    grant: dict[str, Any], ctx: FeatRequirementContext
) -> bool:
    """Новое владение из grant bonus_proficiencies."""
    raw_w = grant.get("weapons", [])
    weapons_listed = isinstance(raw_w, list) and bool(raw_w)
    if grant.get("choice"):
        weapons_new = _any_new_weapon(ctx, list(all_weapon_ids()))
    elif weapons_listed:
        weapons_new = _any_new_weapon(
            ctx, [str(weapon_id) for weapon_id in raw_w]
        )
    else:
        weapons_new = False
    _, armors, _, _ = proficiency_tokens_and_skills_from_grant(grant)
    armors_new = (
        any(armor not in ctx.armor_tokens for armor in armors)
        if armors
        else False
    )
    if weapons_listed or grant.get("choice"):
        return weapons_new or armors_new if armors else weapons_new
    return armors_new if armors else True


def _grant_adds_new_weapon_proficiency(
    grant: dict[str, Any], ctx: FeatRequirementContext
) -> bool:
    """Новое владение из grant weapon_proficiency."""
    if grant.get("choice"):
        return _any_new_weapon(ctx, list(all_weapon_ids()))
    weapons, _, _, _ = proficiency_tokens_and_skills_from_grant(grant)
    if not weapons:
        return True
    return _any_new_weapon(ctx, weapons)


def _grant_adds_new_skill_proficiency(
    grant: dict[str, Any], ctx: FeatRequirementContext
) -> bool:
    """Новое владение из grant skill_proficiency."""
    _, _, _, grant_skills = proficiency_tokens_and_skills_from_grant(grant)
    if not grant_skills:
        if grant.get("choice"):
            return any(skill not in ctx.skills for skill in PHB_SKILL_IDS)
        return True
    return any(skill not in ctx.skills for skill in grant_skills)


def _grant_adds_new_tool_proficiency(
    grant: dict[str, Any], ctx: FeatRequirementContext
) -> bool:
    """Новое владение из grant tool_proficiency."""
    if grant.get("choice"):
        return _any_new_tool(ctx, list(all_tool_ids()))
    _, _, tools, _ = proficiency_tokens_and_skills_from_grant(grant)
    if not tools:
        return True
    return _any_new_tool(ctx, tools)


def _grant_adds_new_multiple_proficiency(
    grant: dict[str, Any], ctx: FeatRequirementContext
) -> bool:
    """Новое владение из grant multiple_proficiency."""
    return any(skill not in ctx.skills for skill in PHB_SKILL_IDS) or (
        _any_new_tool(ctx, list(all_tool_ids()))
    )


_GRANT_ADDS_NEW_PROFICIENCY_HANDLERS: dict[
    str, Callable[[dict[str, Any], FeatRequirementContext], bool]
] = {
    "bonus_proficiencies": _grant_adds_new_bonus_proficiencies,
    "armor_proficiency": lambda grant, ctx: _any_new_armor(ctx, grant),
    "weapon_proficiency": _grant_adds_new_weapon_proficiency,
    "skill_proficiency": _grant_adds_new_skill_proficiency,
    "tool_proficiency": _grant_adds_new_tool_proficiency,
    "multiple_proficiency": _grant_adds_new_multiple_proficiency,
}


def _grant_adds_new_proficiency(
    grant: dict[str, Any], ctx: FeatRequirementContext
) -> bool:
    """Даёт ли grant новое владение относительно контекста."""
    mtype = str(grant.get("type", ""))
    if mtype not in _PROFICIENCY_GRANT_TYPES:
        return True
    handler = _GRANT_ADDS_NEW_PROFICIENCY_HANDLERS.get(mtype)
    if handler is None:
        return True
    return handler(grant, ctx)


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


# ============================================================================
# Требования черт
# ============================================================================


def _requirement_met(
    req: dict[str, Any],
    ctx: FeatRequirementContext,
) -> bool:
    """Одно требование черты."""
    from core.feats.requirement_handlers import check_requirement

    return check_requirement(req, ctx)


def requirement_met(req: dict[str, Any], ctx: FeatRequirementContext) -> bool:
    """Выполнено ли одно требование черты."""
    return _requirement_met(req, ctx)


def feat_meets_requirements(feat_id: str, ctx: FeatRequirementContext) -> bool:
    """Выполнены ли требования черты."""
    feat = load_feat(feat_id)
    raw_reqs = feat.get("requirements", [])
    if not isinstance(raw_reqs, list) or not raw_reqs:
        return True

    or_reqs: list[dict[str, Any]] = []
    and_reqs: list[dict[str, Any]] = []
    for req in raw_reqs:
        if not isinstance(req, dict):
            continue
        if req.get("alternative"):
            or_reqs.append(req)
        else:
            and_reqs.append(req)

    for req in and_reqs:
        if not _requirement_met(req, ctx):
            return False
    if or_reqs:
        return any(_requirement_met(req, ctx) for req in or_reqs)
    return True


def active_feat_ids(character: Character) -> list[str]:
    """Черты персонажа, проходящие ongoing-проверку требований."""
    ctx = build_feat_selection_context_from_character(character)
    return [
        feat_id
        for feat_id in character.feat_ids
        if feat_is_active(feat_id, character, ctx=ctx)
    ]


def feat_is_active(
    feat_id: str,
    character: Character,
    *,
    ctx: FeatRequirementContext | None = None,
) -> bool:
    """Активна ли черта с учётом текущих требований."""
    if feat_id not in getattr(character, "feat_ids", []):
        return False
    if ctx is None:
        ctx = build_feat_selection_context_from_character(character)
    return feat_meets_requirements(feat_id, ctx)


def can_take_feat(
    feat_id: str,
    existing_ids: list[str],
    *,
    repeatable: bool | None = None,
) -> bool:
    """Можно ли взять черту (уникальность)."""
    feat = load_feat(feat_id)
    is_repeatable = bool(feat.get("repeatable", False))
    if repeatable is not None:
        is_repeatable = repeatable
    if is_repeatable:
        return True
    return feat_id not in existing_ids


def feat_has_requirements(feat_id: str) -> bool:
    """Есть ли у черты явные требования в YAML."""
    feat = load_feat(feat_id)
    raw_reqs = feat.get("requirements", [])
    return isinstance(raw_reqs, list) and bool(raw_reqs)


def list_feats_for_selection(
    ctx: FeatRequirementContext,
    existing_ids: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Черты для меню: (доступные, требования не выполнены, скрытые)."""
    eligible: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    hidden: list[dict[str, Any]] = []
    for feat in load_feats():
        feat_id = str(feat.get("id", ""))
        if not feat_id or not can_take_feat(feat_id, existing_ids):
            continue
        if not feat_visible_for_selection(feat_id, ctx):
            hidden.append(feat)
            continue
        if feat_meets_requirements(feat_id, ctx):
            eligible.append(feat)
        elif feat_has_requirements(feat_id):
            blocked.append(feat)
    return eligible, blocked, hidden
