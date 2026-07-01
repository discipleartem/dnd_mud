"""Проверки владений и спасбросков."""

from core.classes import get_class_dict, get_subclass_choice_level
from core.equipment import (
    armor_category,
    resolve_tool_pool,
    tool_category,
    weapon_matches_category,
)
from core.grant_mechanics import normalize_armor_token


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


def get_class_saving_throws(class_id: str) -> list[str]:
    """Спасброски класса."""
    info = get_class_dict(class_id)
    if not info:
        return []
    raw = info.get("saving_throws", [])
    if isinstance(raw, list):
        return [str(s) for s in raw]
    return []


def has_save_proficiency(proficiencies: list[str], ability_id: str) -> bool:
    """Владение спасброском по характеристике."""
    return ability_id in proficiencies


def subclass_proficiencies_active(
    class_id: str, subclass_id: str | None, level: int
) -> bool:
    """Подкласс даёт владения на текущем уровне."""
    if not subclass_id:
        return False
    return level >= get_subclass_choice_level(class_id)
