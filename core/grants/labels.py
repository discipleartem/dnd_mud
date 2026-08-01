"""Ключи локализации для отображения grants (без UI I/O)."""


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
