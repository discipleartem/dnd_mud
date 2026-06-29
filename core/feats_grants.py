"""Владения и бонусы характеристик из черт."""

from typing import Any

from core.feats_loader import load_feat
from core.types import StatMap


def resolve_feat_ability_bonuses(
    feat_id: str, choices: dict[str, Any] | None = None
) -> StatMap:
    """Бонусы к характеристикам из черты."""
    from core.stats import STAT_NAMES

    feat = load_feat(feat_id)
    choices = choices or {}
    bonuses: StatMap = {}
    fixed = feat.get("ability_bonuses", {})
    if isinstance(fixed, dict):
        for key, val in fixed.items():
            if key in STAT_NAMES:
                bonuses[key] = int(val)

    choice_list = feat.get("ability_bonuses_choice", [])
    amount = int(feat.get("ability_bonuses_amount", 1))
    if isinstance(choice_list, list) and choice_list:
        picked = choices.get("ability")
        if isinstance(picked, str) and picked in choice_list:
            bonuses[picked] = bonuses.get(picked, 0) + amount
    return bonuses


def _grants_from_mechanics(
    mechanics: dict[str, Any],
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Из mechanics feature: weapons, armors, tools, skills."""
    from core.skills import PHB_SKILL_IDS

    choices = choices or {}
    weapons: list[str] = []
    armors: list[str] = []
    tools: list[str] = []
    skills: list[str] = []
    mtype = mechanics.get("type", "")
    if mtype == "weapon_proficiency":
        if mechanics.get("choice"):
            raw = choices.get("weapons", [])
            if isinstance(raw, list):
                weapons.extend(str(w) for w in raw)
        else:
            raw = mechanics.get("weapons", [])
            if isinstance(raw, list):
                weapons.extend(str(w) for w in raw)
    elif mtype == "armor_proficiency":
        raw = mechanics.get("armors", [])
        if isinstance(raw, list):
            armors.extend(str(a) for a in raw)
    elif mtype == "tool_proficiency":
        raw = mechanics.get("tools", [])
        if isinstance(raw, list):
            tools.extend(str(t) for t in raw)
    elif mtype == "skill_proficiency":
        raw = mechanics.get("skills", [])
        if isinstance(raw, list):
            skills.extend(str(s) for s in raw)
    elif mtype == "multiple_proficiency":
        raw = choices.get("skills_tools", [])
        if isinstance(raw, list):
            for entry in raw:
                if not isinstance(entry, dict):
                    continue
                kind = entry.get("type", "skill")
                item_id = str(entry.get("id", ""))
                if kind == "tool":
                    tools.append(item_id)
                elif item_id in PHB_SKILL_IDS:
                    skills.append(item_id)
    elif mtype == "skill_expertise":
        raw = choices.get("expertise", [])
        if isinstance(raw, list):
            for item_id in raw:
                sid = str(item_id)
                if sid in PHB_SKILL_IDS:
                    skills.append(sid)
    # language: обрабатывается в get_feat_language_ids, не владения
    return weapons, armors, tools, skills


def resolve_feat_grants(
    feat_id: str, choices: dict[str, Any] | None = None
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Владения из черты с учётом подвыборов."""
    feat = load_feat(feat_id)
    choices = choices or {}
    weapons: list[str] = []
    armors: list[str] = []
    tools: list[str] = []
    skills: list[str] = []
    raw_features = feat.get("features", [])
    if not isinstance(raw_features, list):
        return weapons, armors, tools, skills
    for feature in raw_features:
        if not isinstance(feature, dict):
            continue
        mechanics = feature.get("mechanics", {})
        if not isinstance(mechanics, dict):
            continue
        w, a, t, s = _grants_from_mechanics(mechanics, choices)
        weapons.extend(w)
        armors.extend(a)
        tools.extend(t)
        skills.extend(s)
    return weapons, armors, tools, skills


def get_feat_skill_ids(
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Навыки из выбранных черт."""
    feat_choices = feat_choices or {}
    skills: list[str] = []
    for feat_id in feat_ids:
        choices = feat_choices.get(feat_id, {})
        _, _, _, s = resolve_feat_grants(feat_id, choices)
        skills.extend(s)
    return skills


def get_feat_language_ids(
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Языки из черт (linguist)."""
    feat_choices = feat_choices or {}
    langs: list[str] = []
    for feat_id in feat_ids:
        choices = feat_choices.get(feat_id, {})
        raw = choices.get("languages", [])
        if isinstance(raw, list):
            langs.extend(str(lang) for lang in raw)
    return langs


def get_feat_expertise_ids(
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Навыки с экспертным владением из черт (skill_expert)."""
    from core.skills import PHB_SKILL_IDS

    feat_choices = feat_choices or {}
    skills: list[str] = []
    for feat_id in feat_ids:
        raw = feat_choices.get(feat_id, {}).get("expertise", [])
        if isinstance(raw, list):
            for item_id in raw:
                sid = str(item_id)
                if sid in PHB_SKILL_IDS and sid not in skills:
                    skills.append(sid)
    return skills


def apply_feats_to_stats(
    stats: StatMap,
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> StatMap:
    """Применить бонусы характеристик от всех черт."""
    from core.stats import (
        ABILITY_SCORE_MAX,
        STAT_NAMES,
        apply_bonuses_to_stats,
    )

    feat_choices = feat_choices or {}
    result = stats.copy()
    for feat_id in feat_ids:
        bonuses = resolve_feat_ability_bonuses(
            feat_id, feat_choices.get(feat_id, {})
        )
        result = apply_bonuses_to_stats(result, bonuses)
    for stat in STAT_NAMES:
        if stat in result and result[stat] > ABILITY_SCORE_MAX:
            result[stat] = ABILITY_SCORE_MAX
    return result


def apply_feat_grants_to_character(
    character: Any,
    feat_id: str,
    choices: dict[str, Any] | None = None,
) -> Any:
    """Добавить на персонажа владения, навыки и языки из одной черты."""
    from dataclasses import replace

    from core.proficiencies import merge_proficiency_tokens
    from core.skills import merge_proficiencies

    choices = choices or {}
    feat_choices = {feat_id: choices}
    weapons, armors, tools, _ = resolve_feat_grants(feat_id, choices)
    skills = get_feat_skill_ids([feat_id], feat_choices)
    languages = get_feat_language_ids([feat_id], feat_choices)
    expertise = get_feat_expertise_ids([feat_id], feat_choices)

    merged_langs = list(character.languages)
    for lang_id in languages:
        if lang_id not in merged_langs:
            merged_langs.append(lang_id)

    return replace(
        character,
        weapon_proficiencies=merge_proficiency_tokens(
            character.weapon_proficiencies, weapons
        ),
        armor_proficiencies=merge_proficiency_tokens(
            character.armor_proficiencies, armors
        ),
        tool_proficiencies=merge_proficiency_tokens(
            character.tool_proficiencies, tools
        ),
        skills=merge_proficiencies(character.skills, skills),
        languages=merged_langs,
        skill_expertise=merge_proficiencies(
            character.skill_expertise, expertise
        ),
    )


def get_feat_proficiency_grants(
    feat_id: str,
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Владения из черты: (weapons, armors, tools, skills)."""
    return resolve_feat_grants(feat_id, choices)
