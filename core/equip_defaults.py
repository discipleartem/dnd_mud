"""Авто-экипировка и свойства оружия для выбора слотов."""

import re
from typing import Any

from core.classes import character_has_spellcasting
from core.equipment import (
    armor_category,
    load_armor,
    load_weapon,
    meets_armor_strength_requirement,
    weapon_category,
)
from core.feats import has_non_light_dual_wield
from core.models import Character
from core.proficiencies import has_armor_proficiency, has_weapon_proficiency
from core.stats import ABILITY_SCORE_DEFAULT
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


def default_equipped() -> EquippedState:
    """Пустая экипировка."""
    return {
        "armor": None,
        "shield": False,
        "main_hand": None,
        "off_hand": None,
    }


def _armor_sort_key(armor_id: str) -> tuple[int, int]:
    """Ключ сортировки: тяжелее и выше базовый КД — лучше."""
    info = load_armor(armor_id)
    cat = armor_category(armor_id)
    cat_rank = {"heavy": 3, "medium": 2, "light": 1}.get(cat, 0)
    return (cat_rank, int(info.get("armor_class", 0)))


def _inventory_weapon_ids(character: Character) -> list[str]:
    """Уникальные id оружия в инвентаре."""
    seen: set[str] = set()
    result: list[str] = []
    for item in character.inventory:
        if item.get("kind") != "weapon":
            continue
        weapon_id = str(item.get("id", ""))
        if not weapon_id or weapon_id in seen:
            continue
        seen.add(weapon_id)
        result.append(weapon_id)
    return result


def _proficient_inventory_weapons(character: Character) -> list[str]:
    """Оружие из инвентаря, которым владеет персонаж."""
    profs = character.weapon_proficiencies
    return [
        weapon_id
        for weapon_id in _inventory_weapon_ids(character)
        if has_weapon_proficiency(profs, weapon_id)
    ]


def _off_hand_weapon_allowed(weapon_id: str, *, allow_non_light: bool) -> bool:
    """Одноручное рукопашное для второй руки (лёгкое или dual_wielder)."""
    if not _weapon_is_one_handed_melee(weapon_id):
        return False
    if allow_non_light:
        return True
    return _weapon_is_light(weapon_id)


def _pick_main_weapon(weapons: list[str]) -> tuple[str | None, bool]:
    """Основное оружие с наибольшим уроном (с учётом владения)."""
    if not weapons:
        return None, False
    best_id = weapons[0]
    best_damage = -1.0
    best_two_handed = False
    for weapon_id in weapons:
        damage, two_handed = _weapon_auto_equip_damage(weapon_id)
        if damage > best_damage:
            best_damage = damage
            best_id = weapon_id
            best_two_handed = two_handed
    return best_id, best_two_handed


def _pick_off_hand_weapon(
    weapons: list[str],
    main_hand: str,
    *,
    allow_non_light: bool = False,
) -> str | None:
    """Одноручное оружие для второй руки (кроме основного)."""
    candidates: list[tuple[float, str]] = []
    for weapon_id in weapons:
        if weapon_id == main_hand:
            continue
        if not _off_hand_weapon_allowed(
            weapon_id, allow_non_light=allow_non_light
        ):
            continue
        candidates.append((_weapon_one_handed_damage(weapon_id), weapon_id))
    if not candidates:
        return None
    return max(candidates)[1]


def equip_defaults(character: Character) -> EquippedState:
    """Авто-экипировка: лучший доспех, щит и оружие из инвентаря."""
    equipped = default_equipped()
    armor_profs = character.armor_proficiencies
    strength = int(character.stats.get("strength", ABILITY_SCORE_DEFAULT))

    armor_ids = [
        str(item["id"])
        for item in character.inventory
        if item.get("kind") == "armor"
        and armor_category(str(item["id"])) in ("light", "medium", "heavy")
        and has_armor_proficiency(armor_profs, str(item["id"]))
        and meets_armor_strength_requirement(str(item["id"]), strength)
    ]
    if armor_ids:
        equipped["armor"] = max(armor_ids, key=_armor_sort_key)

    has_shield_item = any(
        item.get("kind") == "armor" and item.get("id") == "shield"
        for item in character.inventory
    )
    shield_proficient = has_armor_proficiency(armor_profs, "shield")
    can_use_shield = has_shield_item and shield_proficient

    weapons = _proficient_inventory_weapons(character)
    main_hand, main_two_handed = _pick_main_weapon(weapons)
    if main_hand:
        equipped["main_hand"] = main_hand

    if main_hand and main_two_handed:
        equipped["shield"] = False
        return equipped

    if can_use_shield:
        equipped["shield"] = True
        if main_hand and _weapon_is_versatile(main_hand):
            equipped["main_hand_grip"] = "one_handed"
        return equipped

    if character_has_spellcasting(
        character.class_id, character.subclass_id, character.level
    ):
        return equipped

    allow_non_light = has_non_light_dual_wield(character.feat_ids)
    off_hand = _pick_off_hand_weapon(
        weapons,
        main_hand or "",
        allow_non_light=allow_non_light,
    )
    if off_hand:
        equipped["off_hand"] = off_hand
        if main_hand and _weapon_is_versatile(main_hand):
            equipped["main_hand_grip"] = "one_handed"
        return equipped

    if main_hand and _weapon_is_versatile(main_hand):
        equipped["main_hand_grip"] = "two_handed"
    return equipped
