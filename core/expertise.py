"""Экспертиза (компетентность): выбор при создании персонажа."""

from dataclasses import dataclass, field
from typing import Any

from core.classes import load_class_full
from core.models import Character
from core.skills import THIEVES_TOOLS_ID


@dataclass
class ExpertiseAlternative:
    """Альтернативный вариант экспертизы (плут: навык + инструмент)."""

    pick: int
    pool: str
    options: list[str] = field(default_factory=list)


@dataclass
class ExpertiseGrant:
    """Один grant компетентности на уровне класса."""

    feature_id: str
    feature_name: str
    level: int
    pick: int
    pool: str
    alternatives: list[ExpertiseAlternative] = field(default_factory=list)


def _parse_alternatives(
    raw: Any,
) -> list[ExpertiseAlternative]:
    """Разобрать alternatives из YAML."""
    if not isinstance(raw, list):
        return []
    result: list[ExpertiseAlternative] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        pick = int(entry.get("pick", 0))
        pool = str(entry.get("pool", ""))
        options_raw = entry.get("options", [])
        options: list[str] = []
        if isinstance(options_raw, list):
            options = [str(o) for o in options_raw]
        if pick > 0 and pool:
            result.append(
                ExpertiseAlternative(pick=pick, pool=pool, options=options)
            )
    return result


def _grants_from_feature(feat: dict[str, Any]) -> list[ExpertiseGrant]:
    """Извлечь grants из одного class feature."""
    mechanics = feat.get("expertise_mechanics", {})
    if not isinstance(mechanics, dict):
        return []
    raw_grants = mechanics.get("grants", [])
    if not isinstance(raw_grants, list):
        return []

    feature_id = str(feat.get("id", ""))
    feature_name = str(feat.get("name", feature_id))
    result: list[ExpertiseGrant] = []
    for grant in raw_grants:
        if not isinstance(grant, dict):
            continue
        level = int(grant.get("level", 0))
        pick = int(grant.get("pick", 0))
        pool = str(grant.get("pool", ""))
        if level < 1 or pick < 1 or not pool:
            continue
        result.append(
            ExpertiseGrant(
                feature_id=feature_id,
                feature_name=feature_name,
                level=level,
                pick=pick,
                pool=pool,
                alternatives=_parse_alternatives(grant.get("alternatives")),
            )
        )
    return result


def get_expertise_grants(
    class_id: str, character_level: int
) -> list[ExpertiseGrant]:
    """Grants компетентности, доступные на текущем уровне при создании."""
    class_info = load_class_full(class_id)
    features = class_info.get("features", [])
    if not isinstance(features, list):
        return []

    grants: list[ExpertiseGrant] = []
    for feat in features:
        if not isinstance(feat, dict):
            continue
        for grant in _grants_from_feature(feat):
            if grant.level <= character_level:
                grants.append(grant)
    grants.sort(key=lambda g: g.level)
    return grants


def expertise_step_required(class_id: str, character_level: int) -> bool:
    """Нужен ли экран выбора экспертизы при создании."""
    return bool(get_expertise_grants(class_id, character_level))


def _prior_expertise_picks(
    class_id: str, character_level: int, before_level: int
) -> int:
    """Сумма pick по grants с level < before_level (без альтернатив)."""
    return sum(
        g.pick
        for g in get_expertise_grants(class_id, character_level)
        if not g.alternatives and g.level < before_level
    )


def grant_expertise_satisfied(
    character: Character, grant: ExpertiseGrant
) -> bool:
    """Компетентность по grant уже выбрана на персонаже."""
    if grant.alternatives:
        return bool(character.skill_expertise or character.tool_expertise)
    prior = _prior_expertise_picks(
        character.class_id, character.level, grant.level
    )
    return len(character.skill_expertise) >= prior + grant.pick


def pending_expertise_grants(character: Character) -> list[ExpertiseGrant]:
    """Grants компетентности, ещё не выбранные на текущем уровне."""
    grants = get_expertise_grants(character.class_id, character.level)
    return [g for g in grants if not grant_expertise_satisfied(character, g)]


def validate_expertise_selection(
    grant: ExpertiseGrant,
    proficiencies: list[str],
    selected_skills: list[str],
    selected_tools: list[str],
    *,
    used_alternative: bool = False,
) -> bool:
    """Проверить корректность выбора компетентности."""
    if used_alternative:
        if not grant.alternatives:
            return False
        skill_alt = next(
            (a for a in grant.alternatives if a.pool == "proficient_skills"),
            None,
        )
        tool_alt = next(
            (a for a in grant.alternatives if a.pool == "tools"), None
        )
        if skill_alt is None or tool_alt is None:
            return False
        if len(selected_skills) != skill_alt.pick:
            return False
        if len(selected_tools) != tool_alt.pick:
            return False
        prof_set = set(proficiencies)
        return all(s in prof_set for s in selected_skills) and all(
            t in tool_alt.options for t in selected_tools
        )

    if len(selected_skills) != grant.pick:
        return False
    if selected_tools:
        return False
    if len(set(selected_skills)) != grant.pick:
        return False
    prof_set = set(proficiencies)
    return all(s in prof_set for s in selected_skills)


def default_rogue_tool_expertise() -> list[str]:
    """ID воровских инструментов для альтернативы плута."""
    return [THIEVES_TOOLS_ID]
