"""Боевая механика: атака, КД, штрафы за невладение."""

from core.constants import proficiency_bonus
from core.dice import ability_modifier
from core.equipment import armor_category, load_armor
from core.models import Character
from core.proficiencies import (
    has_armor_proficiency,
    has_tool_proficiency,
    has_weapon_proficiency,
)


def attack_roll_modifier(
    character: Character,
    weapon_id: str,
    ability_mod: int | None = None,
) -> int:
    """Модификатор броска атаки: ability + PB если владеет оружием."""
    if ability_mod is None:
        ability_mod = ability_modifier(character.stats.get("strength", 10))
    mod = ability_mod
    if has_weapon_proficiency(character.weapon_proficiencies, weapon_id):
        mod += proficiency_bonus(character.level)
    return mod


def armor_wearing_penalty(character: Character, armor_id: str) -> bool:
    """True — помеха на Str/Dex checks/saves/attacks (доспех без владения)."""
    if not armor_id:
        return False
    return not has_armor_proficiency(character.armor_proficiencies, armor_id)


def compute_ac(
    character: Character,
    armor_id: str | None = None,
    *,
    shield: bool = False,
) -> int:
    """Класс доспеха персонажа."""
    dex_mod = ability_modifier(character.stats.get("dexterity", 10))
    if armor_id is None:
        ac = 10 + dex_mod
    else:
        info = load_armor(armor_id)
        base = int(info.get("armor_class", 10))
        cat = armor_category(armor_id)
        max_dex = info.get("max_dex_modifier")
        dex_bonus = dex_mod
        if cat in ("medium",) and max_dex is not None:
            dex_bonus = min(dex_mod, int(max_dex))
        elif cat == "heavy":
            dex_bonus = 0
        modifier_bonus = info.get("modifier_bonus")
        ac = base + dex_bonus if modifier_bonus == "DEX" else base
    if shield and (
        has_armor_proficiency(character.armor_proficiencies, "shield")
        or "shield" in character.armor_proficiencies
    ):
        ac += 2
    return ac


def tool_check_modifier(
    character: Character,
    tool_id: str,
    ability_mod: int,
) -> int:
    """Модификатор проверки с инструментом."""
    mod = ability_mod
    if has_tool_proficiency(character.tool_proficiencies, tool_id):
        mod += proficiency_bonus(character.level)
    return mod
