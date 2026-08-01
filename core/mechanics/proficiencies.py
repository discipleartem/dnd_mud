"""Проверки владения оружием, доспехами и инструментами."""

from core.catalogs.equipment import (
    armor_category,
    resolve_tool_pool,
    tool_category,
    weapon_matches_category,
)
from core.grants.normalize import normalize_armor_token
from core.mechanics.proficiency_collect import (
    ProficiencyChoice,
    get_background_tool_proficiencies,
    get_class_proficiency_tokens,
    get_class_saving_throws,
    get_class_tool_choices,
    get_proficiency_choices,
    get_racial_proficiency_tokens,
    get_subclass_proficiency_tokens,
    merge_proficiency_tokens,
    subclass_proficiencies_active,
)

__all__ = [
    "ProficiencyChoice",
    "get_background_tool_proficiencies",
    "get_class_proficiency_tokens",
    "get_class_saving_throws",
    "get_class_tool_choices",
    "get_proficiency_choices",
    "get_racial_proficiency_tokens",
    "get_subclass_proficiency_tokens",
    "has_armor_proficiency",
    "has_save_proficiency",
    "has_tool_proficiency",
    "has_weapon_pool_proficiency",
    "has_weapon_proficiency",
    "is_valid_tool_selection",
    "merge_proficiency_tokens",
    "subclass_proficiencies_active",
]


def has_weapon_proficiency(proficiencies: list[str], weapon_id: str) -> bool:
    """Владение оружием по токенам."""
    if weapon_id in proficiencies:
        return True
    for token in proficiencies:
        if weapon_matches_category(token, weapon_id):
            return True
    return False


def has_weapon_pool_proficiency(
    pool: str, weapon_proficiencies: list[str]
) -> bool:
    """Владение категорией оружия (simple, martial), не отдельным видом."""
    if pool in weapon_proficiencies:
        return True
    if pool == "martial":
        return any(
            token in weapon_proficiencies
            for token in ("martial_melee", "martial_ranged")
        )
    if pool == "simple":
        return any(
            token in weapon_proficiencies
            for token in ("simple_melee", "simple_ranged")
        )
    return False


def has_armor_proficiency(proficiencies: list[str], armor_id: str) -> bool:
    """Владение доспехом или щитом."""
    cat = armor_category(armor_id)
    if not cat:
        return False
    normalized = normalize_armor_token(cat)
    return normalized in proficiencies or cat in proficiencies


def has_tool_proficiency(proficiencies: list[str], tool_id: str) -> bool:
    """Владение инструментом или категорией."""
    if tool_id in proficiencies:
        return True
    cat = tool_category(tool_id)
    if cat and cat in proficiencies:
        return True
    for token in proficiencies:
        if token in ("artisans_tools", "gaming_sets", "musical_instruments"):
            pool = resolve_tool_pool(token)
            if tool_id in pool:
                return True
    return False


def is_valid_tool_selection(
    selected: list[str], pool: list[str], count: int
) -> bool:
    """Проверить выбор инструментов."""
    if len(selected) != count:
        return False
    if len(set(selected)) != count:
        return False
    pool_set = set(pool)
    return all(t in pool_set for t in selected)


def has_save_proficiency(proficiencies: list[str], ability_id: str) -> bool:
    """Владение спасброском по характеристике."""
    return ability_id in proficiencies
