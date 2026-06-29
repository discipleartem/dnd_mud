"""Характеристики и привязка навыков из YAML."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.io import load_yaml

ABILITIES_FILE = Path("database/core/abilities.yaml")
SKILLS_FILE = Path("database/core/skills.yaml")

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


@lru_cache(maxsize=1)
def _load_abilities_yaml() -> dict[str, Any]:
    """Загрузить abilities из YAML."""
    data = load_yaml(ABILITIES_FILE)
    abilities = data.get("abilities", {})
    if isinstance(abilities, dict):
        return abilities
    return {}


@lru_cache(maxsize=1)
def _load_skills_yaml() -> dict[str, Any]:
    """Загрузить skills из YAML."""
    data = load_yaml(SKILLS_FILE)
    skills = data.get("skills", {})
    if isinstance(skills, dict):
        return skills
    return {}


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
    return {
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


def ability_for_skill(skill_id: str) -> str | None:
    """Характеристика для навыка или None."""
    return skill_ability_map().get(skill_id)


def load_skill_info(skill_id: str) -> dict[str, Any]:
    """Метаданные навыка из skills.yaml."""
    info = _load_skills_yaml().get(skill_id, {})
    if isinstance(info, dict):
        return info
    return {}
