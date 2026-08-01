"""Сборка владений по CreationContext — leaf без character_build/feats."""

from typing import Any

from core.backgrounds import get_background_skills
from core.feat_catalog import (
    get_feat_expertise_ids,
    get_feat_language_ids,
    get_feat_save_proficiencies,
)
from core.grants_context import CreationContext, ResolvedGrants
from core.io import merge_unique
from core.proficiencies import (
    get_background_tool_proficiencies,
    get_class_proficiency_tokens,
    get_class_saving_throws,
    get_feat_proficiency_tokens,
    get_racial_proficiency_tokens,
    get_subclass_proficiency_tokens,
    merge_proficiency_tokens,
)
from core.skills import apply_racial_proficiencies


def merge_languages_with_feats(
    languages: list[str] | None,
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None,
) -> list[str]:
    """Добавить языки из черт к уже выбранным."""
    feat_langs = get_feat_language_ids(feat_ids, feat_choices)
    if not feat_langs:
        return list(languages) if languages else []
    return merge_unique(list(languages) if languages else [], feat_langs)


def merge_expertise_with_feats(
    skill_expertise: list[str] | None,
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None,
) -> list[str]:
    """Добавить компетентность из черт."""
    feat_expertise = get_feat_expertise_ids(feat_ids, feat_choices)
    if not feat_expertise:
        return list(skill_expertise) if skill_expertise else []
    return merge_unique(
        list(skill_expertise) if skill_expertise else [],
        feat_expertise,
    )


def resolve_creation_grants(
    race_id: str,
    subrace_id: str | None,
    class_id: str,
    background_id: str | None,
    subclass_id: str | None,
    level: int,
    *,
    feat_ids: list[str] | None = None,
    feat_choices: dict[str, dict[str, Any]] | None = None,
    extra_skills: list[str] | None = None,
    extra_weapon_tokens: list[str] | None = None,
    extra_tool_tokens: list[str] | None = None,
    extra_languages: list[str] | None = None,
    include_feat_languages: bool = True,
) -> ResolvedGrants:
    """Собрать владения из расы, класса, предыстории, подкласса и черт."""
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
    fw, fa, ft = get_feat_proficiency_tokens(feat_ids or [], feat_choices)
    weapons = merge_proficiency_tokens(cw, rw, sw, fw)
    armors = merge_proficiency_tokens(ca, ra, sa, fa)
    tools = merge_proficiency_tokens(ct, rt, st, bg_tools, ft)
    if extra_weapon_tokens:
        weapons = merge_proficiency_tokens(weapons, extra_weapon_tokens)
    if extra_tool_tokens:
        tools = merge_proficiency_tokens(tools, extra_tool_tokens)

    languages = list(extra_languages) if extra_languages else []
    if include_feat_languages and feat_ids:
        languages = merge_languages_with_feats(
            languages, feat_ids, feat_choices
        )

    save_ids = list(get_class_saving_throws(class_id))
    if feat_ids:
        for save_id in get_feat_save_proficiencies(feat_ids, feat_choices):
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


def resolve_grants_for_context(
    ctx: CreationContext,
    *,
    include_feat_languages: bool = True,
) -> ResolvedGrants:
    """Собрать владения по контексту создания персонажа."""
    return resolve_creation_grants(
        ctx.race_id,
        ctx.subrace_id,
        ctx.class_id,
        ctx.background_id,
        ctx.subclass_id,
        ctx.level,
        feat_ids=list(ctx.feat_ids) if ctx.feat_ids else None,
        feat_choices=ctx.feat_choices,
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
        include_feat_languages=include_feat_languages,
    )


def build_fixed_proficiencies(
    race_id: str,
    subrace_id: str | None,
    class_id: str,
    background_id: str | None,
    subclass_id: str | None,
    level: int,
    feat_ids: list[str] | None = None,
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Собрать фиксированные владения без игровых выборов."""
    ctx = CreationContext(
        race_id=race_id,
        subrace_id=subrace_id,
        class_id=class_id,
        background_id=background_id,
        subclass_id=subclass_id,
        level=level,
        feat_ids=tuple(feat_ids) if feat_ids else (),
        feat_choices=feat_choices,
    )
    grants = resolve_grants_for_context(ctx, include_feat_languages=False)
    return (
        list(grants.weapon_tokens),
        list(grants.armor_tokens),
        list(grants.tool_tokens),
    )
