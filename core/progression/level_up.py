"""Применение повышений уровня и прогрессионных grants."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any

from core.catalogs.classes import (
    get_class_dict,
    get_subclass_dict,
    grants_at_level,
)
from core.character.models import Character
from core.feats.apply import (
    apply_feat_grants_to_character,
    resolve_feat_ability_bonuses,
    tough_hp_adjustment_on_acquire,
)
from core.grants.normalize import proficiency_tokens_and_skills_from_grant
from core.mechanics.stats import apply_bonuses_to_stats
from core.platform.io import merge_unique
from core.progression.asi import (
    apply_asi_two_one,
    auto_asi_bonus,
    cap_stats,
    con_hp_bonus_from_asi,
    feat_id_from_asi_choice,
    pending_asi_at_level,
)
from core.progression.hp import HpGainBreakdown, hp_gain_breakdown_for_level_up
from core.progression.xp_levels import has_pending_level_up


def apply_level_up(character: Character, hp_gain: int) -> Character:
    """Повысить персонажа на один уровень с заданным приростом HP.

    Поле ``experience`` не меняется — избыток над порогом уровня сохраняется.
    """
    if not has_pending_level_up(character):
        return character
    new_level = character.level + 1
    updated = replace(
        character,
        level=new_level,
        max_hp=character.max_hp + hp_gain,
        current_hp=character.current_hp + hp_gain,
    )
    return apply_progression_grants_at_level(updated, new_level)


def _apply_progression_grant(
    character: Character, grant: dict[str, Any]
) -> Character:
    """Применить один grant progression без UI-подвыборов."""
    if grant.get("choice"):
        return character

    weapons, armors, tools, skills = proficiency_tokens_and_skills_from_grant(
        grant
    )
    updated = replace(
        character,
        weapon_proficiencies=merge_unique(
            character.weapon_proficiencies, weapons
        ),
        armor_proficiencies=merge_unique(
            character.armor_proficiencies, armors
        ),
        tool_proficiencies=merge_unique(character.tool_proficiencies, tools),
        skills=merge_unique(character.skills, skills),
    )
    if grant.get("type") == "save_proficiency":
        ability = grant.get("ability")
        if isinstance(ability, str):
            updated = replace(
                updated,
                save_proficiencies=merge_unique(
                    updated.save_proficiencies, [ability]
                ),
            )
    return updated


def apply_progression_grants_at_level(
    character: Character, level: int
) -> Character:
    """Авто-применение grants класса/подкласса на уровне."""
    char = character
    class_info = get_class_dict(char.class_id)
    for grant in grants_at_level(class_info, level):
        char = _apply_progression_grant(char, grant)
    if char.subclass_id:
        subclass_info = get_subclass_dict(char.class_id, char.subclass_id)
        if subclass_info:
            for grant in grants_at_level(subclass_info, level):
                char = _apply_progression_grant(char, grant)
    return char


@dataclass
class AsiResolution:
    """Результат выбора ASI/черты на уровне."""

    character: Character
    con_bonus: int = 0
    tough_bonus: int = 0


def _headless_asi_resolution(
    character: Character, new_level: int
) -> AsiResolution:
    """Авто-ASI или сохранённый выбор (без UI)."""
    char = character
    old_stats = char.stats.copy()
    con_bonus = 0
    tough_bonus = 0
    asi_key = str(new_level)
    had_tough = "tough" in char.feat_ids
    asi_value = ""

    if pending_asi_at_level(char, new_level):
        prime = next(iter(auto_asi_bonus(char.class_id)))
        stats = cap_stats(apply_asi_two_one(char.stats, prime))
        con_bonus = con_hp_bonus_from_asi(old_stats, stats, new_level)
        asi_choices = dict(char.asi_choices)
        asi_value = "asi"
        asi_choices[asi_key] = asi_value
        char = replace(char, stats=stats, asi_choices=asi_choices)
    elif asi_key in char.asi_choices:
        asi_value = char.asi_choices[asi_key]
        stats = old_stats.copy()
        feat_ids = list(char.feat_ids)
        feat_choices = dict(char.feat_choices)
        feat_id = feat_id_from_asi_choice(asi_value)
        sub: dict[str, Any] = {}
        if feat_id and feat_id not in feat_ids:
            sub = feat_choices.get(feat_id, {})
            feat_ids.append(feat_id)
            bonuses = resolve_feat_ability_bonuses(feat_id, sub)
            stats = cap_stats(apply_bonuses_to_stats(stats, bonuses))
        con_bonus = con_hp_bonus_from_asi(old_stats, stats, new_level)
        char = replace(
            char,
            stats=stats,
            feat_ids=feat_ids,
            feat_choices=feat_choices,
        )
        if feat_id:
            char = apply_feat_grants_to_character(char, feat_id, sub)

    if feat_id_from_asi_choice(asi_value) == "tough" and not had_tough:
        tough_bonus = tough_hp_adjustment_on_acquire(new_level)

    return AsiResolution(
        character=char, con_bonus=con_bonus, tough_bonus=tough_bonus
    )


def process_pending_level_ups(
    character: Character,
    *,
    resolve_asi: (
        Callable[[Character, int], AsiResolution | None] | None
    ) = None,
    on_level_up: (
        Callable[[Character, int, HpGainBreakdown, int, int], bool] | None
    ) = None,
) -> Character:
    """Применить все ожидающие повышения; resolve_asi — UI или headless."""
    char = character
    while has_pending_level_up(char):
        new_level = char.level + 1
        con_bonus = 0
        tough_bonus = 0

        if pending_asi_at_level(char, new_level):
            resolution: AsiResolution | None
            if resolve_asi is None:
                resolution = _headless_asi_resolution(char, new_level)
            else:
                resolution = resolve_asi(char, new_level)
            if resolution is None:
                break
            char = resolution.character
            con_bonus = resolution.con_bonus
            tough_bonus = resolution.tough_bonus
        elif str(new_level) in char.asi_choices:
            resolution = _headless_asi_resolution(char, new_level)
            char = resolution.character
            con_bonus = resolution.con_bonus
            tough_bonus = resolution.tough_bonus

        roll_feat_ids = list(char.feat_ids)
        if tough_bonus > 0:
            roll_feat_ids = [
                feat_id for feat_id in roll_feat_ids if feat_id != "tough"
            ]

        breakdown = hp_gain_breakdown_for_level_up(
            char.class_id,
            char.stats,
            new_level,
            char.difficulty,
            char.race,
            char.subrace,
            roll_feat_ids,
        )
        if on_level_up is not None and not on_level_up(
            char, new_level, breakdown, con_bonus, tough_bonus
        ):
            break
        char = apply_level_up(char, breakdown.total + con_bonus + tough_bonus)
    return char
