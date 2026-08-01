"""Ключи локализации для отображения grants (без UI I/O)."""

from core.platform.localization import get_string
from core.types import StringsDict


def ability_name(strings: StringsDict, stat_key: str) -> str:
    """Локализованное имя характеристики."""
    return get_string(strings, f"stats.{stat_key}")


def skill_name(strings: StringsDict, skill_key: str) -> str:
    """Локализованное имя навыка."""
    return get_string(strings, f"skills.{skill_key}")


def grant_type_string_key(gtype: str) -> str:
    """Ключ strings для типа grant."""
    return f"character.grant_type_{gtype}"


def grant_pool_string_key(pool: str, *, gtype: str = "") -> str:
    """Ключ strings для пула выбора grant."""
    if pool == "all" and gtype == "skill_proficiency":
        return "character.grant_pool_all_skills"
    if pool == "all" and gtype == "feat":
        return "character.grant_pool_all_feats"
    return f"character.grant_pool_{pool}"


def grant_damage_string_key(damage_type: str) -> str:
    """Ключ strings для типа урона в grant."""
    return f"character.grant_damage_{damage_type}"


def spell_string_key(spell_id: str) -> str:
    """Ключ strings для заклинания."""
    return f"spells.{spell_id}"
