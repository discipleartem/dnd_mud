"""Применение черт: бонусы, grants, dual wield, HP."""

from dataclasses import replace
from typing import Any

from core.catalogs.skills import merge_proficiencies
from core.feats.catalog import (
    get_feat_expertise_ids,
    get_feat_language_ids,
    get_feat_skill_ids,
    iter_feat_grants,
    load_feat,
    resolve_feat_grants,
)
from core.mechanics.hp_bonus import HpBonusSource, hit_point_bonus_amount
from core.mechanics.proficiencies import merge_proficiency_tokens
from core.mechanics.stats import (
    ABILITY_SCORE_MAX,
    STAT_NAMES,
    apply_bonuses_to_stats,
)
from core.progression.asi import cap_stats
from core.types import StatMap


def tough_hp_adjustment_on_acquire(level: int) -> int:
    """Дополнительные HP при взятии черты Крепкий: 2 × уровень."""
    return 2 * level


def get_feat_hp_bonus_sources(feat_ids: list[str]) -> list[HpBonusSource]:
    """Бонусы HP за уровень из выбранных черт (имя — название черты)."""
    sources: list[HpBonusSource] = []
    for feat_id in feat_ids:
        feat = load_feat(feat_id)
        feat_name = str(feat.get("name", feat_id)).strip() or feat_id
        raw_grants = feat.get("grants", [])
        if not isinstance(raw_grants, list):
            continue
        for grant in raw_grants:
            if not isinstance(grant, dict):
                continue
            amount = hit_point_bonus_amount(grant)
            if amount <= 0:
                continue
            name = str(grant.get("name", "")).strip() or feat_name
            sources.append(HpBonusSource(name=name, amount=amount))
    return sources


def apply_feat_pick(
    stats: StatMap,
    feat_id: str,
    subchoices: dict[str, Any] | None = None,
) -> StatMap:
    """Применить бонусы выбранной черты к характеристикам с учётом потолка."""
    bonuses = resolve_feat_ability_bonuses(feat_id, subchoices)
    return cap_stats(apply_bonuses_to_stats(stats, bonuses))


def resolve_feat_ability_bonuses(
    feat_id: str, choices: dict[str, Any] | None = None
) -> StatMap:
    """Бонусы к характеристикам из черты."""
    feat = load_feat(feat_id)
    choices = choices or {}
    bonuses: StatMap = {}
    fixed = feat.get("ability_bonuses", {})
    if isinstance(fixed, dict):
        for key, val in fixed.items():
            if key in STAT_NAMES:
                bonuses[key] = int(val)

    choice_list = feat.get("ability_bonuses_choice", [])
    amount = int(feat.get("ability_bonuses_amount", 1))
    if isinstance(choice_list, list) and choice_list:
        picked = choices.get("ability")
        if isinstance(picked, str) and picked in choice_list:
            bonuses[picked] = bonuses.get(picked, 0) + amount
    return bonuses


def apply_feats_to_stats(
    stats: StatMap,
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> StatMap:
    """Применить бонусы характеристик от всех черт."""
    feat_choices = feat_choices or {}
    result = stats.copy()
    for feat_id in feat_ids:
        bonuses = resolve_feat_ability_bonuses(
            feat_id, feat_choices.get(feat_id, {})
        )
        result = apply_bonuses_to_stats(result, bonuses)
    for stat in STAT_NAMES:
        if stat in result and result[stat] > ABILITY_SCORE_MAX:
            result[stat] = ABILITY_SCORE_MAX
    return result


def apply_feat_grants_to_character(
    character: Any,
    feat_id: str,
    choices: dict[str, Any] | None = None,
) -> Any:
    """Добавить на персонажа владения, навыки и языки из одной черты."""
    choices = choices or {}
    feat_choices = {feat_id: choices}
    weapons, armors, tools, _ = resolve_feat_grants(feat_id, choices)
    skills = get_feat_skill_ids([feat_id], feat_choices)
    languages = get_feat_language_ids([feat_id], feat_choices)
    expertise = get_feat_expertise_ids([feat_id], feat_choices)

    merged_langs = list(character.languages)
    for lang_id in languages:
        if lang_id not in merged_langs:
            merged_langs.append(lang_id)

    return replace(
        character,
        weapon_proficiencies=merge_proficiency_tokens(
            character.weapon_proficiencies, weapons
        ),
        armor_proficiencies=merge_proficiency_tokens(
            character.armor_proficiencies, armors
        ),
        tool_proficiencies=merge_proficiency_tokens(
            character.tool_proficiencies, tools
        ),
        skills=merge_proficiencies(character.skills, skills),
        languages=merged_langs,
        skill_expertise=merge_proficiencies(
            character.skill_expertise, expertise
        ),
    )


def has_non_light_dual_wield(feat_ids: list[str]) -> bool:
    """Черта «Использование двух оружий» — сражение без свойства «лёгкое»."""
    return any(
        grant.get("type") == "dual_wielder"
        and grant.get("non_light_dual_wield")
        for grant in iter_feat_grants(feat_ids)
    )


def dual_wielder_ac_bonus_from_feats(feat_ids: list[str]) -> int:
    """Бонус КД из grant dual_wielder (обычно +1)."""
    bonus = 0
    for grant in iter_feat_grants(feat_ids):
        if grant.get("type") != "dual_wielder":
            continue
        amount = grant.get("ac_bonus", 0)
        if isinstance(amount, int) and amount > 0:
            bonus += amount
    return bonus
