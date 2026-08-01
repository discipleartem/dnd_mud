"""Побочные эффекты выбора черты при создании (накопление владений)."""

from typing import Any

from core.feats.catalog import get_feat_skill_ids, load_feat
from core.grants.normalize import proficiency_tokens_and_skills_from_grant


def accumulate_feat_proficiency_knowledge(
    feat_id: str,
    subchoices: dict[str, Any],
    *,
    weapon_profs: list[str],
    known_skills: list[str],
    known_tools: list[str],
) -> None:
    """Добавить владения и навыки из grants черты и subchoices (in-place)."""
    for grant in load_feat(feat_id).get("grants", []):
        if not isinstance(grant, dict):
            continue
        weapons, _armor, tools, skills = (
            proficiency_tokens_and_skills_from_grant(grant, subchoices)
        )
        for weapon_id in weapons:
            token = str(weapon_id)
            if token not in weapon_profs:
                weapon_profs.append(token)
        for skill_id in skills:
            if skill_id not in known_skills:
                known_skills.append(skill_id)
        for tool_id in tools:
            if tool_id not in known_tools:
                known_tools.append(tool_id)
    for skill_id in get_feat_skill_ids([feat_id], {feat_id: subchoices}):
        if skill_id not in known_skills:
            known_skills.append(skill_id)
    for weapon_id in subchoices.get("weapons", []):
        token = str(weapon_id)
        if token not in weapon_profs:
            weapon_profs.append(token)
