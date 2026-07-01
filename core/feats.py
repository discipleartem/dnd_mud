"""Загрузка черт из YAML — публичный фасад."""

from core.feat_apply import (
    apply_feat_grants_to_character,
    apply_feats_to_stats,
    get_feat_expertise_ids,
    get_feat_hp_bonus_sources,
    get_feat_language_ids,
    get_feat_proficiency_grants,
    get_feat_skill_ids,
    resolve_feat_ability_bonuses,
    resolve_feat_grants,
    tough_hp_adjustment_on_acquire,
)
from core.feat_descriptions import (
    feat_full_description_lines,
    feat_summary_description,
)
from core.feat_requirements import (
    can_take_feat,
    character_has_spellcasting,
    feat_has_requirements,
    feat_meets_requirements,
    get_race_feat_grants,
    list_feats_for_selection,
    race_feat_step_required,
    requirement_met,
)
from core.feat_visibility import feat_visible_for_selection
from core.feats_loader import (
    FeatGrant,
    FeatRequirementContext,
    load_feat,
    load_feats,
)

__all__ = [
    "FeatGrant",
    "FeatRequirementContext",
    "apply_feat_grants_to_character",
    "apply_feats_to_stats",
    "can_take_feat",
    "character_has_spellcasting",
    "feat_visible_for_selection",
    "feat_full_description_lines",
    "feat_has_requirements",
    "feat_meets_requirements",
    "feat_summary_description",
    "get_feat_expertise_ids",
    "get_feat_hp_bonus_sources",
    "get_feat_language_ids",
    "get_feat_proficiency_grants",
    "get_feat_skill_ids",
    "get_race_feat_grants",
    "list_feats_for_selection",
    "load_feat",
    "load_feats",
    "race_feat_step_required",
    "requirement_met",
    "resolve_feat_ability_bonuses",
    "resolve_feat_grants",
    "tough_hp_adjustment_on_acquire",
]
