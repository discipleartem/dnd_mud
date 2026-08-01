"""Расчёт класса доспеха (КД)."""

from core.catalogs.equipment import load_armor
from core.character.models import Character
from core.feats.apply import dual_wielder_ac_bonus_from_feats
from core.inventory.equip_defaults import (
    _weapon_is_one_handed_melee,
    main_hand_uses_both_hands,
)
from core.mechanics.dice import ability_modifier
from core.mechanics.stats import ABILITY_SCORE_DEFAULT
from core.types import EquippedState


def dual_wielder_ac_bonus_applies(
    equipped: EquippedState, feat_ids: list[str]
) -> bool:
    """+1 КД: в каждой руке одноручное рукопашное (черта dual_wielder)."""
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


def _armor_ac_value(armor_id: str, dex_mod: int) -> int:
    """Базовый КД от доспеха по PHB."""
    info = load_armor(armor_id)
    base = int(info.get("armor_class", 10))
    bonus_type = str(info.get("modifier_bonus", ""))
    max_dex = info.get("max_dex_modifier")
    dex_part = 0
    if bonus_type == "DEX":
        if isinstance(max_dex, int):
            dex_part = min(dex_mod, max_dex)
        else:
            dex_part = dex_mod
    return base + dex_part


def compute_ac(character: Character) -> int:
    """Класс доспеха персонажа (PHB + бонусы черт при экипировке)."""
    stats = character.stats
    dexterity = int(stats.get("dexterity", ABILITY_SCORE_DEFAULT))
    dex_mod = ability_modifier(dexterity)
    equipped = character.equipped or {
        "armor": None,
        "shield": False,
        "main_hand": None,
        "off_hand": None,
    }
    armor_id = equipped.get("armor")
    ac = 10 + dex_mod
    if isinstance(armor_id, str) and armor_id:
        ac = _armor_ac_value(armor_id, dex_mod)
    if equipped.get("shield"):
        ac += 2
    if dual_wielder_ac_bonus_applies(equipped, character.feat_ids):
        ac += dual_wielder_ac_bonus_from_feats(character.feat_ids)
    return ac
