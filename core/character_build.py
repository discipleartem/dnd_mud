"""Сборка нового персонажа без записи на диск."""

import warnings
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from core.grants_context import CreationContext, ResolvedGrants
from core.io import merge_unique
from core.levels import clamp_level
from core.models import Character, _parse_character_class
from core.progression import max_hp_for_level, xp_for_level
from core.progression.subclasses import start_level_for_difficulty
from core.stats import STANDARD_ARRAY, generate_stats_standard_array
from core.types import CharacterClass, GameDifficulty, InventoryItem, StatMap
from core.types.character_params import CharacterBuildParams


def build_new_character(
    name: str,
    race_id: str,
    class_id: str | CharacterClass,
    difficulty: GameDifficulty = "normal",
    subrace_id: str | None = None,
    stats: StatMap | None = None,
    subclass_id: str | None = None,
    languages: list[str] | None = None,
    background_id: str | None = None,
    skills: list[str] | None = None,
    skill_expertise: list[str] | None = None,
    tool_expertise: list[str] | None = None,
    weapon_proficiencies: list[str] | None = None,
    armor_proficiencies: list[str] | None = None,
    tool_proficiencies: list[str] | None = None,
    background_tool_picks: list[str] | None = None,
    feat_ids: list[str] | None = None,
    feat_choices: dict[str, dict[str, Any]] | None = None,
    asi_choices: dict[str, str] | None = None,
    save_proficiencies: list[str] | None = None,
    inventory: list[InventoryItem] | None = None,
    equipment_choices: dict[str, str] | None = None,
    level: int | None = None,
    class_features_applied: bool = False,
    apply_feat_stat_bonuses: bool = True,
    *,
    unique_save_slug: Callable[[str], str],
) -> Character:
    """Собрать нового персонажа без записи на диск.

    ``apply_feat_stat_bonuses=False`` — если ``stats`` уже содержат бонусы
    черт (flow создания после ``select_creation_feats``).

    ``unique_save_slug`` — фабрика уникального save_slug по имени персонажа.

    .. deprecated:: 0.2.0
        Используйте :func:`build_new_character_from_params`
        с CharacterBuildParams.
    """
    warnings.warn(
        "build_new_character is deprecated. "
        "Use build_new_character_from_params with CharacterBuildParams.",
        DeprecationWarning,
        stacklevel=2,
    )
    params = CharacterBuildParams(
        name=name,
        race_id=race_id,
        class_id=class_id,
        difficulty=difficulty,
        subrace_id=subrace_id,
        stats=stats,
        subclass_id=subclass_id,
        languages=languages,
        background_id=background_id,
        skills=skills,
        skill_expertise=skill_expertise,
        tool_expertise=tool_expertise,
        weapon_proficiencies=weapon_proficiencies,
        armor_proficiencies=armor_proficiencies,
        tool_proficiencies=tool_proficiencies,
        background_tool_picks=background_tool_picks,
        feat_ids=feat_ids,
        feat_choices=feat_choices,
        asi_choices=asi_choices,
        save_proficiencies=save_proficiencies,
        inventory=inventory,
        equipment_choices=equipment_choices,
        level=level,
        class_features_applied=class_features_applied,
        apply_feat_stat_bonuses=apply_feat_stat_bonuses,
        unique_save_slug=unique_save_slug,
    )
    return build_new_character_from_params(params)


def build_new_character_from_params(params: CharacterBuildParams) -> Character:
    """Собрать нового персонажа из параметров без записи на диск.

    Новый API для создания персонажа с использованием CharacterBuildParams.
    Заменяет длинный список параметров в build_new_character.

    Args:
        params: Параметры создания персонажа.

    Returns:
        Модель персонажа.
    """
    stats = params.stats
    if stats is None:
        stats = generate_stats_standard_array(
            list(STANDARD_ARRAY), params.race_id, params.subrace_id
        )
    languages: list[str] | None = params.languages
    skill_expertise: list[str] | None = params.skill_expertise
    if params.feat_ids:
        from core.feats import apply_feats_to_stats

        if params.apply_feat_stat_bonuses:
            stats = apply_feats_to_stats(
                stats, params.feat_ids, params.feat_choices
            )
        languages = merge_languages_with_feats(
            params.languages, params.feat_ids, params.feat_choices
        )
        skill_expertise = merge_expertise_with_feats(
            params.skill_expertise, params.feat_ids, params.feat_choices
        )

    level = params.level
    if level is None:
        level = start_level_for_difficulty(params.difficulty)
    level = clamp_level(level)

    need_grants = (
        params.weapon_proficiencies is None
        or params.armor_proficiencies is None
        or params.tool_proficiencies is None
        or params.skills is None
        or params.save_proficiencies is None
    )
    weapon_proficiencies: list[str]
    armor_proficiencies: list[str]
    tool_proficiencies: list[str]
    skills: list[str]
    save_proficiencies: list[str]
    if need_grants:
        class_id_str = (
            params.class_id.value
            if isinstance(params.class_id, CharacterClass)
            else str(params.class_id)
        )
        ctx = CreationContext(
            race_id=params.race_id,
            subrace_id=params.subrace_id,
            class_id=class_id_str,
            background_id=params.background_id,
            subclass_id=params.subclass_id,
            level=level,
            feat_ids=tuple(params.feat_ids) if params.feat_ids else (),
            feat_choices=params.feat_choices,
        )
        grants = resolve_grants_for_context(ctx, include_feat_languages=False)
        weapon_proficiencies = (
            list(grants.weapon_tokens)
            if params.weapon_proficiencies is None
            else params.weapon_proficiencies
        )
        armor_proficiencies = (
            list(grants.armor_tokens)
            if params.armor_proficiencies is None
            else params.armor_proficiencies
        )
        tool_proficiencies = (
            list(grants.tool_tokens)
            if params.tool_proficiencies is None
            else params.tool_proficiencies
        )
        skills = (
            list(grants.skill_ids) if params.skills is None else params.skills
        )
        save_proficiencies = (
            list(grants.save_ids)
            if params.save_proficiencies is None
            else params.save_proficiencies
        )
    else:
        weapon_proficiencies = params.weapon_proficiencies or []
        armor_proficiencies = params.armor_proficiencies or []
        tool_proficiencies = params.tool_proficiencies or []
        skills = params.skills or []
        save_proficiencies = params.save_proficiencies or []

    inventory = params.inventory
    if inventory is None:
        from core.backgrounds import get_background_equipment_items
        from core.inventory import add_items_to_inventory
        from core.starting_equipment import resolve_starting_items

        raw_inv = resolve_starting_items(
            params.class_id,
            params.equipment_choices or {},
            list(weapon_proficiencies or []),
            list(armor_proficiencies or []),
        )
        resolved: list[InventoryItem] = list(raw_inv)
        if params.background_id:
            resolved = add_items_to_inventory(
                resolved,
                get_background_equipment_items(
                    params.background_id,
                    list(params.background_tool_picks or []),
                ),
            )
        inventory = resolved

    hp = max_hp_for_level(
        params.class_id,
        stats,
        level,
        params.difficulty,
        params.race_id,
        params.subrace_id,
        params.feat_ids,
    )

    character = Character(
        name=params.name,
        race=params.race_id,
        class_id=_parse_character_class(params.class_id),
        level=level,
        stats=stats,
        current_hp=hp,
        max_hp=hp,
        experience=xp_for_level(level),
        difficulty=params.difficulty,
        subrace=params.subrace_id,
        subclass_id=params.subclass_id,
        languages=list(languages) if languages else [],
        background_id=params.background_id,
        skills=list(skills) if skills else [],
        skill_expertise=list(skill_expertise) if skill_expertise else [],
        tool_expertise=(
            list(params.tool_expertise) if params.tool_expertise else []
        ),
        weapon_proficiencies=(
            list(weapon_proficiencies) if weapon_proficiencies else []
        ),
        armor_proficiencies=(
            list(armor_proficiencies) if armor_proficiencies else []
        ),
        tool_proficiencies=(
            list(tool_proficiencies) if tool_proficiencies else []
        ),
        feat_ids=list(params.feat_ids) if params.feat_ids else [],
        feat_choices=(
            dict(params.feat_choices) if params.feat_choices else {}
        ),
        asi_choices=dict(params.asi_choices) if params.asi_choices else {},
        save_proficiencies=(
            list(save_proficiencies) if save_proficiencies else []
        ),
        inventory=list(inventory) if inventory else [],
        equipment_choices=(
            dict(params.equipment_choices) if params.equipment_choices else {}
        ),
        class_features_applied=params.class_features_applied,
        save_slug=params.unique_save_slug(params.name),
        created_at=datetime.now(UTC).isoformat(),
    )
    from core.inventory import equip_defaults

    character.equipped = equip_defaults(character)

    return character


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
    from core.backgrounds import get_background_skills
    from core.proficiencies import (
        get_background_tool_proficiencies,
        get_class_proficiency_tokens,
        get_feat_proficiency_tokens,
        get_racial_proficiency_tokens,
        get_subclass_proficiency_tokens,
        merge_proficiency_tokens,
    )
    from core.proficiencies.proficiency_checks import (
        get_class_saving_throws,
    )
    from core.skills import apply_racial_proficiencies

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
        from core.feats.feat_apply import get_feat_save_proficiencies

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


def merge_languages_with_feats(
    languages: list[str] | None,
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None,
) -> list[str]:
    """Добавить языки из черт к уже выбранным."""
    from core.feats import get_feat_language_ids

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
    from core.feats import get_feat_expertise_ids

    feat_expertise = get_feat_expertise_ids(feat_ids, feat_choices)
    if not feat_expertise:
        return list(skill_expertise) if skill_expertise else []
    return merge_unique(
        list(skill_expertise) if skill_expertise else [],
        feat_expertise,
    )


__all__ = [
    "build_new_character",
    "build_new_character_from_params",
    "CreationContext",
    "ResolvedGrants",
    "merge_expertise_with_feats",
    "merge_languages_with_feats",
    "resolve_creation_grants",
    "resolve_grants_for_context",
]
