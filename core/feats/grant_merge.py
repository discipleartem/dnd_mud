"""Слияние grants черт с ResolvedGrants (оркестрация над leaf resolve)."""

from typing import Any

from core.feats.catalog import (
    get_feat_expertise_ids,
    get_feat_language_ids,
    get_feat_proficiency_tokens,
    get_feat_save_proficiencies,
    get_feat_skill_ids,
)
from core.grants.context import CreationContext, ResolvedGrants
from core.grants.resolve import (
    resolve_creation_grants,
    resolve_grants_for_context,
)
from core.platform.io import merge_unique

__all__ = [
    "merge_expertise_with_feats",
    "merge_feat_extras_into_grants",
    "merge_languages_with_feats",
    "resolve_creation_grants_with_feats",
    "resolve_grants_for_context_with_feats",
]


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


def merge_feat_extras_into_grants(
    base: ResolvedGrants,
    *,
    feat_ids: list[str] | None,
    feat_choices: dict[str, dict[str, Any]] | None,
    include_feat_languages: bool = True,
) -> ResolvedGrants:
    """Добавить владения/языки/сейвы из черт к уже собранным grants."""
    if not feat_ids:
        return base

    fw, fa, ft = get_feat_proficiency_tokens(feat_ids, feat_choices)
    feat_skills = get_feat_skill_ids(feat_ids, feat_choices)
    languages = list(base.language_ids)
    if include_feat_languages:
        languages = merge_unique(
            languages, get_feat_language_ids(feat_ids, feat_choices)
        )
    save_ids = list(base.save_ids)
    for save_id in get_feat_save_proficiencies(feat_ids, feat_choices):
        if save_id not in save_ids:
            save_ids.append(save_id)
    return ResolvedGrants(
        weapon_tokens=tuple(merge_unique(list(base.weapon_tokens), fw)),
        armor_tokens=tuple(merge_unique(list(base.armor_tokens), fa)),
        tool_tokens=tuple(merge_unique(list(base.tool_tokens), ft)),
        skill_ids=tuple(merge_unique(list(base.skill_ids), feat_skills)),
        language_ids=tuple(languages),
        save_ids=tuple(save_ids),
    )


def resolve_creation_grants_with_feats(
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
    """Leaf resolve + слияние черт (публичный API для тестов/сборки)."""
    base = resolve_creation_grants(
        race_id,
        subrace_id,
        class_id,
        background_id,
        subclass_id,
        level,
        extra_skills=extra_skills,
        extra_weapon_tokens=extra_weapon_tokens,
        extra_tool_tokens=extra_tool_tokens,
        extra_languages=extra_languages,
    )
    return merge_feat_extras_into_grants(
        base,
        feat_ids=feat_ids,
        feat_choices=feat_choices,
        include_feat_languages=include_feat_languages,
    )


def resolve_grants_for_context_with_feats(
    ctx: CreationContext,
    *,
    include_feat_languages: bool = True,
) -> ResolvedGrants:
    """Контекст создания с учётом черт."""
    base = resolve_grants_for_context(ctx)
    return merge_feat_extras_into_grants(
        base,
        feat_ids=list(ctx.feat_ids) if ctx.feat_ids else None,
        feat_choices=ctx.feat_choices,
        include_feat_languages=include_feat_languages,
    )
