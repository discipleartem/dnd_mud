"""Расчёт класса доспеха (КД)."""

from core.dice import ability_modifier
from core.equipment import armor_category, load_armor
from core.feat_apply import dual_wielder_ac_bonus_from_feats
from core.inventory._weapons import dual_wielder_ac_bonus_applies
from core.models import Character
from core.stats import ABILITY_SCORE_DEFAULT


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


def _armor_sort_key(armor_id: str) -> tuple[int, int]:
    """Ключ сортировки: тяжелее и выше базовый КД — лучше."""
    info = load_armor(armor_id)
    cat = armor_category(armor_id)
    cat_rank = {"heavy": 3, "medium": 2, "light": 1}.get(cat, 0)
    return (cat_rank, int(info.get("armor_class", 0)))


def compute_ac(character: Character) -> int:
    """Класс доспеха персонажа (PHB + бонусы черт при экипировке)."""
    from core.inventory._equip import default_equipped

    stats = character.stats
    dexterity = int(stats.get("dexterity", ABILITY_SCORE_DEFAULT))
    dex_mod = ability_modifier(dexterity)
    equipped = character.equipped or default_equipped()
    armor_id = equipped.get("armor")
    ac = 10 + dex_mod
    if isinstance(armor_id, str) and armor_id:
        ac = _armor_ac_value(armor_id, dex_mod)
    if equipped.get("shield"):
        ac += 2
    if dual_wielder_ac_bonus_applies(equipped, character.feat_ids):
        ac += dual_wielder_ac_bonus_from_feats(character.feat_ids)
    return ac
