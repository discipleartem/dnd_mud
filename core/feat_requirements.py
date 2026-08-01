"""Требования и видимость черт при выборе."""

from dataclasses import dataclass, field
from typing import Any

from core.classes import character_has_spellcasting
from core.equipment import all_tool_ids, all_weapon_ids
from core.feat_catalog import load_feat, load_feats
from core.grants import normalize_armor_token
from core.grants_context import CreationContext
from core.grants_resolve import resolve_grants_for_context
from core.proficiencies import has_tool_proficiency, has_weapon_proficiency
from core.skill_ids import PHB_SKILL_IDS
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
    grants = resolve_grants_for_context(ctx, include_feat_languages=False)
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
    grants = resolve_grants_for_context(ctx, include_feat_languages=False)
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
    armors = _armor_tokens_from_grant(grant)
    if not armors:
        return True
    return any(armor not in ctx.armor_tokens for armor in armors)


def _grant_adds_new_proficiency(
    grant: dict[str, Any], ctx: FeatRequirementContext
) -> bool:
    """Даёт ли grant новое владение относительно контекста."""
    mtype = str(grant.get("type", ""))
    if mtype not in _PROFICIENCY_GRANT_TYPES:
        return True

    match mtype:
        case "bonus_proficiencies":
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
            armors = _armor_tokens_from_grant(grant)
            armors_new = (
                any(armor not in ctx.armor_tokens for armor in armors)
                if armors
                else False
            )
            if weapons_listed or grant.get("choice"):
                return weapons_new or armors_new if armors else weapons_new
            return armors_new if armors else True
        case "armor_proficiency":
            return _any_new_armor(ctx, grant)
        case "weapon_proficiency":
            if grant.get("choice"):
                return _any_new_weapon(ctx, list(all_weapon_ids()))
            raw = grant.get("weapons", [])
            if not isinstance(raw, list) or not raw:
                return True
            return _any_new_weapon(ctx, [str(weapon_id) for weapon_id in raw])
        case "skill_proficiency":
            grant_skills: list[str] = []
            raw = grant.get("skills", [])
            if isinstance(raw, list):
                grant_skills.extend(str(skill) for skill in raw)
            skill_one = grant.get("skill")
            if isinstance(skill_one, str) and skill_one:
                grant_skills.append(skill_one)
            if not grant_skills:
                if grant.get("choice"):
                    return any(
                        skill not in ctx.skills for skill in PHB_SKILL_IDS
                    )
                return True
            return any(skill not in ctx.skills for skill in grant_skills)
        case "tool_proficiency":
            if grant.get("choice"):
                return _any_new_tool(ctx, list(all_tool_ids()))
            raw = grant.get("tools", [])
            if not isinstance(raw, list) or not raw:
                return True
            return _any_new_tool(ctx, [str(tool_id) for tool_id in raw])
        case "multiple_proficiency":
            return any(skill not in ctx.skills for skill in PHB_SKILL_IDS) or (
                _any_new_tool(ctx, list(all_tool_ids()))
            )
        case _:
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


# ============================================================================
# Требования черт
# ============================================================================


def _armor_requirement_met(
    required: list[str], armor_tokens: list[str]
) -> bool:
    """Проверка владения доспехом для требования черты."""
    return any(armor in armor_tokens for armor in required)


def _requirement_met(
    req: dict[str, Any],
    ctx: FeatRequirementContext,
) -> bool:
    """Одно требование черты."""
    rtype = req.get("type", "")
    if rtype == "ability_score":
        target = str(req.get("target", ""))
        value = int(req.get("value", 0))
        if target not in ctx.stats:
            return False
        return int(ctx.stats[target]) >= value
    if rtype == "armor_proficiency":
        raw = req.get("armors", [])
        if isinstance(raw, list):
            return _armor_requirement_met(
                [str(a) for a in raw], ctx.armor_tokens
            )
        return False
    if rtype == "spellcasting":
        return ctx.has_spellcasting
    return True


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


def active_feat_ids(character: Any) -> list[str]:
    """Черты персонажа, проходящие ongoing-проверку требований."""
    ctx = build_feat_selection_context_from_character(character)
    return [
        feat_id
        for feat_id in character.feat_ids
        if feat_is_active(feat_id, character, ctx=ctx)
    ]


def feat_requirement_context_from_character(
    character: Any,
) -> FeatRequirementContext:
    """Контекст требований черт из персонажа (alias для visibility)."""
    return build_feat_selection_context_from_character(character)


def feat_is_active(
    feat_id: str,
    character: Any,
    *,
    ctx: FeatRequirementContext | None = None,
) -> bool:
    """Активна ли черта с учётом текущих требований."""
    if feat_id not in getattr(character, "feat_ids", []):
        return False
    if ctx is None:
        ctx = feat_requirement_context_from_character(character)
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
