"""Сборка нового персонажа без записи на диск."""

from datetime import UTC, datetime

from core.constants import clamp_level
from core.grants_context import CreationContext, ResolvedGrants
from core.grants_resolve import (
    merge_expertise_with_feats,
    merge_languages_with_feats,
    resolve_creation_grants,
    resolve_grants_for_context,
)
from core.models import Character, parse_character_class
from core.progression import (
    max_hp_for_level,
    start_level_for_difficulty,
    xp_for_level,
)
from core.stats import STANDARD_ARRAY, generate_stats_standard_array
from core.types import (
    CharacterBuildParams,
    CharacterClass,
    InventoryItem,
    StatMap,
)


def _resolve_stats_and_feat_lists(
    params: CharacterBuildParams,
) -> tuple[StatMap, list[str] | None, list[str] | None]:
    """Характеристики и списки языков/expertise с учётом черт."""
    stats = params.stats
    if stats is None:
        stats = generate_stats_standard_array(
            list(STANDARD_ARRAY), params.race_id, params.subrace_id
        )
    languages: list[str] | None = params.languages
    skill_expertise: list[str] | None = params.skill_expertise
    if not params.feat_ids:
        return stats, languages, skill_expertise

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
    return stats, languages, skill_expertise


def _resolve_proficiency_fields(
    params: CharacterBuildParams, level: int
) -> tuple[list[str], list[str], list[str], list[str], list[str]]:
    """Владения, навыки и спасброски из params или grants."""
    need_grants = (
        params.weapon_proficiencies is None
        or params.armor_proficiencies is None
        or params.tool_proficiencies is None
        or params.skills is None
        or params.save_proficiencies is None
    )
    if not need_grants:
        return (
            params.weapon_proficiencies or [],
            params.armor_proficiencies or [],
            params.tool_proficiencies or [],
            params.skills or [],
            params.save_proficiencies or [],
        )

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
    return (
        (
            list(grants.weapon_tokens)
            if params.weapon_proficiencies is None
            else params.weapon_proficiencies
        ),
        (
            list(grants.armor_tokens)
            if params.armor_proficiencies is None
            else params.armor_proficiencies
        ),
        (
            list(grants.tool_tokens)
            if params.tool_proficiencies is None
            else params.tool_proficiencies
        ),
        list(grants.skill_ids) if params.skills is None else params.skills,
        (
            list(grants.save_ids)
            if params.save_proficiencies is None
            else params.save_proficiencies
        ),
    )


def _seed_inventory(
    params: CharacterBuildParams,
    weapon_proficiencies: list[str],
    armor_proficiencies: list[str],
) -> list[InventoryItem]:
    """Стартовый инвентарь класса и предыстории."""
    if params.inventory is not None:
        return list(params.inventory)

    from core.backgrounds import get_background_equipment_items
    from core.inventory import add_items_to_inventory
    from core.starting_equipment import resolve_starting_items

    resolved: list[InventoryItem] = list(
        resolve_starting_items(
            params.class_id,
            params.equipment_choices or {},
            list(weapon_proficiencies),
            list(armor_proficiencies),
        )
    )
    if params.background_id:
        resolved = add_items_to_inventory(
            resolved,
            get_background_equipment_items(
                params.background_id,
                list(params.background_tool_picks or []),
            ),
        )
    return resolved


def build_new_character(params: CharacterBuildParams) -> Character:
    """Собрать нового персонажа из параметров без записи на диск.

    ``apply_feat_stat_bonuses=False`` — если ``stats`` уже содержат бонусы
    черт (flow создания после ``select_creation_feats``).

    ``unique_save_slug`` — фабрика уникального save_slug по имени персонажа.
    """
    stats, languages, skill_expertise = _resolve_stats_and_feat_lists(params)

    level = params.level
    if level is None:
        level = start_level_for_difficulty(params.difficulty)
    level = clamp_level(level)

    (
        weapon_proficiencies,
        armor_proficiencies,
        tool_proficiencies,
        skills,
        save_proficiencies,
    ) = _resolve_proficiency_fields(params, level)

    inventory = _seed_inventory(
        params, weapon_proficiencies, armor_proficiencies
    )

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
        class_id=parse_character_class(params.class_id),
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
        weapon_proficiencies=list(weapon_proficiencies),
        armor_proficiencies=list(armor_proficiencies),
        tool_proficiencies=list(tool_proficiencies),
        feat_ids=list(params.feat_ids) if params.feat_ids else [],
        feat_choices=(
            dict(params.feat_choices) if params.feat_choices else {}
        ),
        asi_choices=dict(params.asi_choices) if params.asi_choices else {},
        save_proficiencies=list(save_proficiencies),
        inventory=list(inventory),
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


__all__ = [
    "build_new_character",
    "CreationContext",
    "ResolvedGrants",
    "merge_expertise_with_feats",
    "merge_languages_with_feats",
    "resolve_creation_grants",
    "resolve_grants_for_context",
]
