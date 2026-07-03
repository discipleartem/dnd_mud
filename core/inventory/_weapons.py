"""Свойства оружия и расчёт урона для авто-экипировки."""

import re
from typing import Any

from core.equipment import load_weapon, weapon_category
from core.types import EquippedState


def _parse_dice_average(dice: str) -> float:
    """Средний урон по нотации кости (например ``1d8`` → 4.5)."""
    match = re.fullmatch(r"(\d+)d(\d+)", dice.strip())
    if not match:
        return 0.0
    count, sides = int(match.group(1)), int(match.group(2))
    return count * (sides + 1) / 2


def _weapon_properties(weapon_id: str) -> dict[str, Any]:
    props = load_weapon(weapon_id).get("properties")
    return dict(props) if isinstance(props, dict) else {}


def _weapon_is_two_handed(weapon_id: str) -> bool:
    return bool(_weapon_properties(weapon_id).get("two_handed"))


def _weapon_is_light(weapon_id: str) -> bool:
    return bool(_weapon_properties(weapon_id).get("light"))


def _weapon_is_melee(weapon_id: str) -> bool:
    return weapon_category(weapon_id).endswith("_melee")


def _weapon_is_one_handed_melee(weapon_id: str) -> bool:
    return _weapon_is_melee(weapon_id) and not _weapon_is_two_handed(weapon_id)


def _weapon_base_damage_dice(weapon_id: str) -> str:
    damage = load_weapon(weapon_id).get("damage", {})
    if isinstance(damage, dict):
        return str(damage.get("dice", "1d4"))
    return "1d4"


def _weapon_is_versatile(weapon_id: str) -> bool:
    return bool(_weapon_properties(weapon_id).get("versatile"))


def _weapon_versatile_damage_dice(weapon_id: str) -> str:
    versatile = _weapon_properties(weapon_id).get("versatile")
    if versatile:
        return str(versatile)
    return _weapon_base_damage_dice(weapon_id)


def _weapon_one_handed_damage(weapon_id: str) -> float:
    """Средний урон одной рукой (без versatile в двухручном режиме)."""
    if _weapon_is_two_handed(weapon_id):
        return 0.0
    return _parse_dice_average(_weapon_base_damage_dice(weapon_id))


def _weapon_auto_equip_damage(weapon_id: str) -> tuple[float, bool]:
    """Урон для авто-экипировки и флаг «нативно двуручное»."""
    if _weapon_is_two_handed(weapon_id):
        return _parse_dice_average(_weapon_base_damage_dice(weapon_id)), True
    if _weapon_is_versatile(weapon_id):
        dice = _weapon_versatile_damage_dice(weapon_id)
        return _parse_dice_average(dice), False
    return _weapon_one_handed_damage(weapon_id), False


def weapon_is_two_handed(weapon_id: str) -> bool:
    """Оружие помечено как двуручное (свойство ``two_handed``)."""
    return _weapon_is_two_handed(weapon_id)


def weapon_is_versatile(weapon_id: str) -> bool:
    """Универсальное оружие (свойство ``versatile``)."""
    return _weapon_is_versatile(weapon_id)


def main_hand_uses_both_hands(equipped: EquippedState) -> bool:
    """Основное оружие занимает обе руки (двуручное или универсальное)."""
    main = equipped.get("main_hand")
    if not isinstance(main, str) or not main:
        return False
    if _weapon_is_two_handed(main):
        return True
    if not _weapon_is_versatile(main):
        return False
    grip = equipped.get("main_hand_grip")
    if grip == "two_handed":
        return True
    if grip == "one_handed":
        return False
    return not equipped.get("shield") and not equipped.get("off_hand")


def dual_wielder_ac_bonus_applies(
    equipped: EquippedState, feat_ids: list[str]
) -> bool:
    """+1 КД: в каждой руке одноручное рукопашное (черта dual_wielder)."""
    from core.feats.feat_apply import (
        dual_wielder_ac_bonus_from_feats,
    )

    if not feat_ids or dual_wielder_ac_bonus_from_feats(feat_ids) <= 0:
        return False
    if equipped.get("shield"):
        return False
    main = equipped.get("main_hand")
    off = equipped.get("off_hand")
    if not isinstance(main, str) or not main:
        return False
    if not isinstance(off, str) or not off:
        return False
    if main_hand_uses_both_hands(equipped):
        return False
    return _weapon_is_one_handed_melee(main) and _weapon_is_one_handed_melee(
        off
    )
