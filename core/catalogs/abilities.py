"""Характеристики и привязка навыков из YAML."""

from typing import Any

from core.platform.catalog_loader import load_catalog
from core.platform.paths import ABILITIES_FILE, SKILLS_FILE

_FALLBACK_ABILITY_IDS: tuple[str, ...] = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)

_FALLBACK_SKILL_IDS: tuple[str, ...] = (
    "acrobatics",
    "animal_handling",
    "arcana",
    "athletics",
    "deception",
    "history",
    "insight",
    "intimidation",
    "investigation",
    "medicine",
    "nature",
    "perception",
    "performance",
    "persuasion",
    "religion",
    "sleight_of_hand",
    "stealth",
    "survival",
)

# PHB skill → ability; используется, если abilities.yaml недоступен
_FALLBACK_SKILL_ABILITY_MAP: dict[str, str] = {
    "athletics": "strength",
    "acrobatics": "dexterity",
    "sleight_of_hand": "dexterity",
    "stealth": "dexterity",
    "arcana": "intelligence",
    "history": "intelligence",
    "investigation": "intelligence",
    "nature": "intelligence",
    "religion": "intelligence",
    "animal_handling": "wisdom",
    "insight": "wisdom",
    "medicine": "wisdom",
    "perception": "wisdom",
    "survival": "wisdom",
    "deception": "charisma",
    "intimidation": "charisma",
    "performance": "charisma",
    "persuasion": "charisma",
}


def _load_abilities_yaml() -> dict[str, Any]:
    """Загрузить abilities из YAML."""
    return load_catalog(ABILITIES_FILE, "abilities")


def _load_skills_yaml() -> dict[str, Any]:
    """Загрузить skills из YAML."""
    return load_catalog(SKILLS_FILE, "skills")


def ability_ids() -> tuple[str, ...]:
    """Id характеристик в порядке PHB."""
    loaded = _load_abilities_yaml()
    if loaded:
        return tuple(loaded.keys())
    return _FALLBACK_ABILITY_IDS


def skill_ids() -> tuple[str, ...]:
    """Id навыков PHB."""
    loaded = _load_skills_yaml()
    if loaded:
        return tuple(loaded.keys())
    return _FALLBACK_SKILL_IDS


def skill_ability_map() -> dict[str, str]:
    """Навык → характеристика."""
    result: dict[str, str] = {}
    for ability_id, info in _load_abilities_yaml().items():
        if not isinstance(info, dict):
            continue
        raw_skills = info.get("skills", {})
        if isinstance(raw_skills, dict):
            for skill_id in raw_skills:
                result[str(skill_id)] = str(ability_id)
    if result:
        return result
    return dict(_FALLBACK_SKILL_ABILITY_MAP)


def ability_for_skill(skill_id: str) -> str | None:
    """Характеристика для навыка или None."""
    return skill_ability_map().get(skill_id)
