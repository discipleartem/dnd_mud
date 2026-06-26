"""Навыки: владения при создании персонажа."""

from typing import Any

from core.classes import load_class_full
from core.races import _get_race_and_subrace

PHB_SKILL_IDS: tuple[str, ...] = (
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

THIEVES_TOOLS_ID = "thieves_tools"


def get_class_skill_config(class_id: str) -> tuple[list[str], int]:
    """Пул навыков класса и число выборов."""
    class_info = load_class_full(class_id)
    raw_choices = class_info.get("skill_choices", [])
    pool: list[str] = []
    if isinstance(raw_choices, list):
        for entry in raw_choices:
            skill_id = str(entry)
            if skill_id in PHB_SKILL_IDS:
                pool.append(skill_id)
    count = int(class_info.get("skill_choices_count", 0))
    return pool, count


def get_merged_race_features(
    race_id: str, subrace_id: str | None = None
) -> list[dict[str, Any]]:
    """Объединить features базовой расы и подрасы."""
    race_info, subrace_info = _get_race_and_subrace(race_id, subrace_id)
    if not race_info:
        return []

    features: list[dict[str, Any]] = []
    if subrace_id and subrace_info:
        inherit_base = subrace_info.get("inherit_base_features", True)
        if inherit_base:
            raw_base = race_info.get("features", [])
            if isinstance(raw_base, list):
                features.extend(
                    feat for feat in raw_base if isinstance(feat, dict)
                )
        raw_sub = subrace_info.get("features", [])
        if isinstance(raw_sub, list):
            features.extend(feat for feat in raw_sub if isinstance(feat, dict))
    else:
        raw = race_info.get("features", [])
        if isinstance(raw, list):
            features.extend(feat for feat in raw if isinstance(feat, dict))
    return features


def _skills_from_proficiency_feature(feat: dict[str, Any]) -> list[str]:
    """Фиксированные навыки из feature skill_proficiency."""
    if feat.get("type") != "skill_proficiency":
        return []
    mechanics = feat.get("mechanics", {})
    if not isinstance(mechanics, dict):
        return []
    if mechanics.get("choice"):
        return []
    raw_skills = mechanics.get("skills", [])
    if not isinstance(raw_skills, list):
        return []
    return [str(s) for s in raw_skills if str(s) in PHB_SKILL_IDS]


def apply_racial_proficiencies(
    race_id: str, subrace_id: str | None = None
) -> list[str]:
    """Автоматические расовые владения навыками (без выбора игрока)."""
    return [
        skill_id
        for skill_id, _source in get_fixed_racial_proficiencies_with_source(
            race_id, subrace_id
        )
    ]


def _collect_fixed_from_features(
    features: Any,
    source: str,
    seen: set[str],
    result: list[tuple[str, str]],
) -> None:
    """Добавить фиксированные навыки из списка features."""
    if not isinstance(features, list):
        return
    for feat in features:
        if not isinstance(feat, dict):
            continue
        for skill_id in _skills_from_proficiency_feature(feat):
            if skill_id not in seen:
                seen.add(skill_id)
                result.append((skill_id, source))


def get_fixed_racial_proficiencies_with_source(
    race_id: str, subrace_id: str | None = None
) -> list[tuple[str, str]]:
    """Фиксированные расовые владения: (skill_id, race|subrace)."""
    race_info, subrace_info = _get_race_and_subrace(race_id, subrace_id)
    if not race_info:
        return []

    result: list[tuple[str, str]] = []
    seen: set[str] = set()

    if subrace_id and subrace_info:
        inherit_base = subrace_info.get("inherit_base_features", True)
        if inherit_base:
            _collect_fixed_from_features(
                race_info.get("features", []),
                "race",
                seen,
                result,
            )
        _collect_fixed_from_features(
            subrace_info.get("features", []),
            "subrace",
            seen,
            result,
        )
    else:
        _collect_fixed_from_features(
            race_info.get("features", []),
            "race",
            seen,
            result,
        )
    return result


def get_race_skill_choices(
    race_id: str, subrace_id: str | None = None
) -> list[dict[str, Any]]:
    """Выборные расовые владения навыками (механика из features)."""
    return [
        _mechanics
        for _mechanics, _source in get_race_skill_choices_with_source(
            race_id, subrace_id
        )
    ]


def get_race_skill_choices_with_source(
    race_id: str, subrace_id: str | None = None
) -> list[tuple[dict[str, Any], str]]:
    """Выборные расовые владения: (mechanics, race|subrace)."""
    race_info, subrace_info = _get_race_and_subrace(race_id, subrace_id)
    if not race_info:
        return []

    result: list[tuple[dict[str, Any], str]] = []

    def scan(features: Any, source: str) -> None:
        if not isinstance(features, list):
            return
        for feat in features:
            if not isinstance(feat, dict):
                continue
            if feat.get("type") != "skill_proficiency":
                continue
            mechanics = feat.get("mechanics", {})
            if not isinstance(mechanics, dict) or not mechanics.get("choice"):
                continue
            result.append((mechanics, source))

    if subrace_id and subrace_info:
        inherit_base = subrace_info.get("inherit_base_features", True)
        if inherit_base:
            scan(race_info.get("features", []), "race")
        scan(subrace_info.get("features", []), "subrace")
    else:
        scan(race_info.get("features", []), "race")
    return result


def resolve_skill_pool(
    from_list: str, class_id: str | None = None
) -> list[str]:
    """Разрешить from_list из YAML в список id навыков."""
    if from_list == "all":
        return list(PHB_SKILL_IDS)
    if class_id is not None:
        pool, _ = get_class_skill_config(class_id)
        return pool
    return list(PHB_SKILL_IDS)


def available_skills(pool: list[str], proficient: list[str]) -> list[str]:
    """Навыки из пула, которыми персонаж ещё не владеет."""
    taken = set(proficient)
    return [skill_id for skill_id in pool if skill_id not in taken]


def merge_proficiencies(*parts: list[str]) -> list[str]:
    """Объединить списки владений без дублей, в порядке появления."""
    result: list[str] = []
    for part in parts:
        for skill_id in part:
            if skill_id not in result:
                result.append(skill_id)
    return result


def is_valid_skill_selection(
    selected: list[str], pool: list[str], count: int
) -> bool:
    """Проверить выбор навыков: ровно count уникальных из pool."""
    if len(selected) != count:
        return False
    if len(set(selected)) != count:
        return False
    pool_set = set(pool)
    return all(skill_id in pool_set for skill_id in selected)
