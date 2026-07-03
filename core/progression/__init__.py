"""Прогрессия персонажа: опыт и уровни (PHB, макс. 10 уровень)."""

from core.dice import roll
from core.progression.hp_gain import (
    HpGainBreakdown,
    extra_hp_bonus_sources,
    extra_hp_per_level,
    hp_gain_breakdown_for_level_up,
    hp_gain_for_level,
    max_hp_for_level,
    roll_hp_gain_for_level_up,
)
from core.progression.level_up import (
    AsiResolution,
    apply_experience,
    apply_level_up,
    apply_progression_grants_at_level,
    process_pending_level_ups,
    resolve_pending_level_ups,
)
from core.progression.xp import (
    XP_THRESHOLDS,
    grant_experience,
    has_pending_level_up,
    level_from_xp,
    xp_covers_level,
    xp_for_level,
)

__all__ = [
    "AsiResolution",
    "HpGainBreakdown",
    "XP_THRESHOLDS",
    "apply_experience",
    "apply_level_up",
    "apply_progression_grants_at_level",
    "extra_hp_bonus_sources",
    "extra_hp_per_level",
    "grant_experience",
    "has_pending_level_up",
    "hp_gain_breakdown_for_level_up",
    "hp_gain_for_level",
    "level_from_xp",
    "max_hp_for_level",
    "process_pending_level_ups",
    "resolve_pending_level_ups",
    "roll",
    "roll_hp_gain_for_level_up",
    "xp_covers_level",
    "xp_for_level",
]
