"""Увеличение характеристик (ASI) при повышении уровня."""

from core.classes import get_class_dict
from core.dice import ability_modifier
from core.models import Character
from core.stats import ABILITY_SCORE_MAX, STAT_NAMES, apply_bonuses_to_stats
from core.types import StatMap

ASI_FEATURE_ID = "ability_score_improvement"


def feat_id_from_asi_choice(asi_value: str) -> str | None:
    """ID черты из сохранённого выбора ASI (``feat:<id>``) или None."""
    if not asi_value.startswith("feat:"):
        return None
    feat_id = asi_value.split(":", 1)[1]
    if not feat_id:
        return None
    return feat_id


def class_grants_asi_at_level(class_id: str, level: int) -> bool:
    """Есть ли у класса умение ASI на указанном уровне."""
    class_info = get_class_dict(class_id)
    if not class_info:
        return False
    raw_features = class_info.get("class_features", [])
    if not isinstance(raw_features, list):
        return False
    for feat in raw_features:
        if not isinstance(feat, dict):
            continue
        if feat.get("id") != ASI_FEATURE_ID:
            continue
        if feat.get("level") == level:
            return True
    return False


def pending_asi_at_level(character: Character, new_level: int) -> bool:
    """На этом уровне ожидается выбор ASI или черты."""
    if not class_grants_asi_at_level(character.class_id, new_level):
        return False
    return str(new_level) not in character.asi_choices


def apply_asi_two_one(stats: StatMap, stat: str) -> StatMap:
    """+2 к одной характеристике (макс. 20)."""
    if stat not in STAT_NAMES:
        return stats.copy()
    bonuses: StatMap = {stat: 2}
    return apply_bonuses_to_stats(stats, bonuses)


def apply_asi_one_two(stats: StatMap, stat_a: str, stat_b: str) -> StatMap:
    """+1 к двум разным характеристикам (макс. 20)."""
    if stat_a not in STAT_NAMES or stat_b not in STAT_NAMES:
        return stats.copy()
    if stat_a == stat_b:
        return stats.copy()
    return apply_bonuses_to_stats(stats, {stat_a: 1, stat_b: 1})


def cap_stats(stats: StatMap) -> StatMap:
    """Ограничить характеристики максимумом 20."""
    result = stats.copy()
    for stat in STAT_NAMES:
        if stat in result and result[stat] > ABILITY_SCORE_MAX:
            result[stat] = ABILITY_SCORE_MAX
    return result


def con_hp_bonus_from_asi(
    old_stats: StatMap, new_stats: StatMap, level: int
) -> int:
    """При росте модификатора CON — +1 max HP за каждый достигнутый уровень."""
    old_mod = ability_modifier(old_stats.get("constitution", 10))
    new_mod = ability_modifier(new_stats.get("constitution", 10))
    if new_mod <= old_mod:
        return 0
    return level * (new_mod - old_mod)


def auto_asi_bonus(class_id: str) -> StatMap:
    """Авто-ASI для тестов: +2 к ключевой характеристике класса."""
    class_info = get_class_dict(class_id)
    prime = "strength"
    if isinstance(class_info, dict):
        raw = class_info.get("prime_ability", "strength")
        if isinstance(raw, str) and raw in STAT_NAMES:
            prime = raw
    return {prime: 2}
