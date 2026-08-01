"""Сборка владений по CreationContext — leaf без feats."""

from core.catalogs.backgrounds import get_background_skills
from core.catalogs.skills import apply_racial_proficiencies
from core.grants.context import CreationContext, ResolvedGrants
from core.mechanics.proficiency_collect import (
    get_background_tool_proficiencies,
    get_class_proficiency_tokens,
    get_class_saving_throws,
    get_racial_proficiency_tokens,
    get_subclass_proficiency_tokens,
)
from core.platform.io import merge_unique


def resolve_creation_grants(
    race_id: str,
    subrace_id: str | None,
    class_id: str,
    background_id: str | None,
    subclass_id: str | None,
    level: int,
    *,
    extra_skills: list[str] | None = None,
    extra_weapon_tokens: list[str] | None = None,
    extra_armor_tokens: list[str] | None = None,
    extra_tool_tokens: list[str] | None = None,
    extra_languages: list[str] | None = None,
    extra_save_ids: list[str] | None = None,
) -> ResolvedGrants:
    """Собрать владения из расы, класса, предыстории и подкласса.

    Бонусы черт передаются через ``extra_*`` (оркестрация — выше leaf).
    """
    skills = list(apply_racial_proficiencies(race_id, subrace_id))
    if background_id:
        for skill_id in get_background_skills(background_id):
            if skill_id not in skills:
                skills.append(skill_id)
    if extra_skills:
        skills = merge_unique(skills, extra_skills)

    cw, ca, ct = get_class_proficiency_tokens(class_id)
    rw, ra, rt, _ = get_racial_proficiency_tokens(race_id, subrace_id)
    sw, sa, st, _ = get_subclass_proficiency_tokens(
        class_id, subclass_id, level
    )
    bg_tools: list[str] = []
    if background_id:
        bg_tools, _ = get_background_tool_proficiencies(background_id)
    weapons = merge_unique(cw, rw, sw)
    armors = merge_unique(ca, ra, sa)
    tools = merge_unique(ct, rt, st, bg_tools)
    if extra_weapon_tokens:
        weapons = merge_unique(weapons, extra_weapon_tokens)
    if extra_armor_tokens:
        armors = merge_unique(armors, extra_armor_tokens)
    if extra_tool_tokens:
        tools = merge_unique(tools, extra_tool_tokens)

    languages = list(extra_languages) if extra_languages else []
    save_ids = list(get_class_saving_throws(class_id))
    if extra_save_ids:
        for save_id in extra_save_ids:
            if save_id not in save_ids:
                save_ids.append(save_id)

    return ResolvedGrants(
        weapon_tokens=tuple(weapons),
        armor_tokens=tuple(armors),
        tool_tokens=tuple(tools),
        skill_ids=tuple(skills),
        language_ids=tuple(languages),
        save_ids=tuple(save_ids),
    )


def resolve_grants_for_context(ctx: CreationContext) -> ResolvedGrants:
    """Собрать владения по контексту (без оркестрации черт)."""
    return resolve_creation_grants(
        ctx.race_id,
        ctx.subrace_id,
        ctx.class_id,
        ctx.background_id,
        ctx.subclass_id,
        ctx.level,
        extra_skills=list(ctx.extra_skills) if ctx.extra_skills else None,
        extra_weapon_tokens=(
            list(ctx.extra_weapon_tokens) if ctx.extra_weapon_tokens else None
        ),
        extra_tool_tokens=(
            list(ctx.extra_tool_tokens) if ctx.extra_tool_tokens else None
        ),
        extra_languages=(
            list(ctx.extra_languages) if ctx.extra_languages else None
        ),
    )


def build_fixed_proficiencies(
    race_id: str,
    subrace_id: str | None,
    class_id: str,
    background_id: str | None,
    subclass_id: str | None,
    level: int,
) -> tuple[list[str], list[str], list[str]]:
    """Собрать фиксированные владения без игровых выборов и черт."""
    grants = resolve_creation_grants(
        race_id,
        subrace_id,
        class_id,
        background_id,
        subclass_id,
        level,
    )
    return (
        list(grants.weapon_tokens),
        list(grants.armor_tokens),
        list(grants.tool_tokens),
    )
