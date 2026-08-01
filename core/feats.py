"""Черты персонажа — фасад публичного API.

Реализация: ``feat_catalog``, ``feat_text``, ``feat_apply``,
``feat_requirements``.
"""

from core.feat_apply import (
    apply_feat_grants_to_character,
    apply_feats_to_stats,
    dual_wielder_ac_bonus_from_feats,
    get_feat_hp_bonus_sources,
    has_non_light_dual_wield,
    resolve_feat_ability_bonuses,
    tough_hp_adjustment_on_acquire,
)
from core.feat_catalog import (
    FeatGrant,
    get_feat_expertise_ids,
    get_feat_language_ids,
    get_feat_proficiency_grants,
    get_feat_save_proficiencies,
    get_feat_skill_ids,
    get_race_feat_grants,
    load_feat,
    load_feats,
    race_feat_step_required,
    resolve_feat_grants,
)
from core.feat_requirements import (
    FeatRequirementContext,
    active_feat_ids,
    build_feat_selection_context,
    build_feat_selection_context_from_character,
    can_take_feat,
    creation_known_for_feat_picks,
    feat_has_requirements,
    feat_is_active,
    feat_meets_requirements,
    feat_requirement_context_from_character,
    feat_visible_for_selection,
    list_feats_for_selection,
    requirement_met,
)
from core.feat_text import (
    feat_full_description_lines,
    feat_summary_description,
)

__all__ = [
    "FeatGrant",
    "FeatRequirementContext",
    "load_feat",
    "load_feats",
    "feat_full_description_lines",
    "feat_summary_description",
    "apply_feat_grants_to_character",
    "apply_feats_to_stats",
    "get_feat_expertise_ids",
    "get_feat_hp_bonus_sources",
    "get_feat_language_ids",
    "get_feat_proficiency_grants",
    "get_feat_save_proficiencies",
    "get_feat_skill_ids",
    "resolve_feat_ability_bonuses",
    "resolve_feat_grants",
    "tough_hp_adjustment_on_acquire",
    "dual_wielder_ac_bonus_from_feats",
    "has_non_light_dual_wield",
    "build_feat_selection_context",
    "build_feat_selection_context_from_character",
    "creation_known_for_feat_picks",
    "feat_visible_for_selection",
    "active_feat_ids",
    "can_take_feat",
    "feat_has_requirements",
    "feat_is_active",
    "feat_meets_requirements",
    "feat_requirement_context_from_character",
    "get_race_feat_grants",
    "list_feats_for_selection",
    "race_feat_step_required",
    "requirement_met",
]
