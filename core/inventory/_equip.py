"""Экипировка персонажа и авто-подбор из инвентаря."""

from core.classes import character_has_spellcasting
from core.equipment import (
    armor_category,
    meets_armor_strength_requirement,
)
from core.feats.feat_apply import has_non_light_dual_wield
from core.inventory._ac import _armor_sort_key
from core.inventory._weapons import (
    _weapon_auto_equip_damage,
    _weapon_is_light,
    _weapon_is_one_handed_melee,
    _weapon_is_versatile,
    _weapon_one_handed_damage,
)
from core.models import Character
from core.proficiencies.proficiency_checks import (
    has_armor_proficiency,
    has_weapon_proficiency,
)
from core.stats import ABILITY_SCORE_DEFAULT
from core.types import EquippedState


def default_equipped() -> EquippedState:
    """Пустая экипировка."""
    return {
        "armor": None,
        "shield": False,
        "main_hand": None,
        "off_hand": None,
    }


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
