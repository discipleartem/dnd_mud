"""Сборка нового персонажа без записи на диск."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from core.grants_context import CreationContext
from core.levels import clamp_level
from core.models import Character, _parse_character_class
from core.progression import max_hp_for_level, xp_for_level
from core.progression.subclasses import start_level_for_difficulty
from core.stats import STANDARD_ARRAY, generate_stats_standard_array
from core.types import (
    CharacterClass,
    GameDifficulty,
    InventoryItem,
    StatMap,
)


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
    """
    if stats is None:
        stats = generate_stats_standard_array(
            list(STANDARD_ARRAY), race_id, subrace_id
        )
    if feat_ids:
        from core.character_builder import (
            merge_expertise_with_feats,
            merge_languages_with_feats,
        )
        from core.feats import apply_feats_to_stats

        if apply_feat_stat_bonuses:
            stats = apply_feats_to_stats(stats, feat_ids, feat_choices)
        languages = merge_languages_with_feats(
            languages, feat_ids, feat_choices
        )
        skill_expertise = merge_expertise_with_feats(
            skill_expertise, feat_ids, feat_choices
        )

    if level is None:
        level = start_level_for_difficulty(difficulty)
    level = clamp_level(level)

    need_grants = (
        weapon_proficiencies is None
        or armor_proficiencies is None
        or tool_proficiencies is None
        or skills is None
        or save_proficiencies is None
    )
    if need_grants:
        from core.character_builder import resolve_grants_for_context

        class_id_str = (
            class_id.value
            if isinstance(class_id, CharacterClass)
            else str(class_id)
        )
        ctx = CreationContext(
            race_id=race_id,
            subrace_id=subrace_id,
            class_id=class_id_str,
            background_id=background_id,
            subclass_id=subclass_id,
            level=level,
            feat_ids=tuple(feat_ids) if feat_ids else (),
            feat_choices=feat_choices,
        )
        grants = resolve_grants_for_context(ctx, include_feat_languages=False)
        if weapon_proficiencies is None:
            weapon_proficiencies = list(grants.weapon_tokens)
        if armor_proficiencies is None:
            armor_proficiencies = list(grants.armor_tokens)
        if tool_proficiencies is None:
            tool_proficiencies = list(grants.tool_tokens)
        if skills is None:
            skills = list(grants.skill_ids)
        if save_proficiencies is None:
            save_proficiencies = list(grants.save_ids)

    if inventory is None:
        from core.backgrounds import get_background_equipment_items
        from core.inventory import add_items_to_inventory
        from core.starting_equipment import resolve_starting_items

        raw_inv = resolve_starting_items(
            class_id,
            equipment_choices or {},
            list(weapon_proficiencies or []),
            list(armor_proficiencies or []),
        )
        resolved: list[InventoryItem] = list(raw_inv)
        if background_id:
            resolved = add_items_to_inventory(
                resolved,
                get_background_equipment_items(
                    background_id, list(background_tool_picks or [])
                ),
            )
        inventory = resolved

    hp = max_hp_for_level(
        class_id,
        stats,
        level,
        difficulty,
        race_id,
        subrace_id,
        feat_ids,
    )

    character = Character(
        name=name,
        race=race_id,
        class_id=_parse_character_class(class_id),
        level=level,
        stats=stats,
        current_hp=hp,
        max_hp=hp,
        experience=xp_for_level(level),
        difficulty=difficulty,
        subrace=subrace_id,
        subclass_id=subclass_id,
        languages=list(languages) if languages else [],
        background_id=background_id,
        skills=list(skills) if skills else [],
        skill_expertise=list(skill_expertise) if skill_expertise else [],
        tool_expertise=list(tool_expertise) if tool_expertise else [],
        weapon_proficiencies=(
            list(weapon_proficiencies) if weapon_proficiencies else []
        ),
        armor_proficiencies=(
            list(armor_proficiencies) if armor_proficiencies else []
        ),
        tool_proficiencies=(
            list(tool_proficiencies) if tool_proficiencies else []
        ),
        feat_ids=list(feat_ids) if feat_ids else [],
        feat_choices=dict(feat_choices) if feat_choices else {},
        asi_choices=dict(asi_choices) if asi_choices else {},
        save_proficiencies=(
            list(save_proficiencies) if save_proficiencies else []
        ),
        inventory=list(inventory) if inventory else [],
        equipment_choices=dict(equipment_choices) if equipment_choices else {},
        class_features_applied=class_features_applied,
        save_slug=unique_save_slug(name),
        created_at=datetime.now(UTC).isoformat(),
    )
    from core.inventory import equip_defaults

    character.equipped = equip_defaults(character)

    return character


__all__ = ["build_new_character"]
