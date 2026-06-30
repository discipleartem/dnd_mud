"""Навыки: владения при создании персонажа."""

from typing import Any

from core.abilities import skill_ids
from core.classes import (
    _load_classes_yaml,
    get_subclass_choice_level,
    load_class_full,
)
from core.races import (
    collect_race_features,
    get_race_and_subrace,
    grants_as_features,
)

PHB_SKILL_IDS: tuple[str, ...] = skill_ids()

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


def _skill_proficiency_mechanics(
    feat: dict[str, Any],
) -> dict[str, Any] | None:
    """Механика skill_proficiency из feature или grant."""
    is_grant = (
        str(feat.get("type", "")) == "skill_proficiency"
        and "mechanics" not in feat
    )
    if is_grant:
        return feat
    mechanics = feat.get("mechanics", {})
    if not isinstance(mechanics, dict):
        mechanics = {}
    mtype = mechanics.get("type") or feat.get("type")
    if mtype != "skill_proficiency":
        return None
    return mechanics


def _skills_from_proficiency_feature(feat: dict[str, Any]) -> list[str]:
    """Фиксированные навыки из feature skill_proficiency."""
    mechanics = _skill_proficiency_mechanics(feat)
    if mechanics is None:
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
    race_info, subrace_info = get_race_and_subrace(race_id, subrace_id)
    if not race_info:
        return []

    result: list[tuple[str, str]] = []
    seen: set[str] = set()

    if subrace_info:
        from core.grants import grants_from_entity, inherit_flags

        _, inherit_grants = inherit_flags(subrace_info)
        if inherit_grants:
            base_feats = grants_as_features(grants_from_entity(race_info))
            _collect_fixed_from_features(base_feats, "race", seen, result)
        sub_feats = grants_as_features(grants_from_entity(subrace_info))
        _collect_fixed_from_features(sub_feats, "subrace", seen, result)
    else:
        _collect_fixed_from_features(
            collect_race_features(race_id, subrace_id),
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
    from core.grants import grants_from_entity, inherit_flags

    race_info, subrace_info = get_race_and_subrace(race_id, subrace_id)
    if not race_info:
        return []

    result: list[tuple[dict[str, Any], str]] = []

    def scan(features: Any, source: str) -> None:
        if not isinstance(features, list):
            return
        for feat in features:
            if not isinstance(feat, dict):
                continue
            mechanics = _skill_proficiency_mechanics(feat)
            if mechanics is None or not mechanics.get("choice"):
                continue
            result.append((mechanics, source))

    if subrace_info:
        _, inherit_grants = inherit_flags(subrace_info)
        if inherit_grants:
            scan(grants_as_features(grants_from_entity(race_info)), "race")
        scan(grants_as_features(grants_from_entity(subrace_info)), "subrace")
    else:
        scan(collect_race_features(race_id, subrace_id), "race")
    return result


def _subclass_features(
    class_id: str, subclass_id: str | None
) -> list[dict[str, Any]]:
    """Список features выбранного подкласса."""
    if not subclass_id:
        return []
    info = _load_classes_yaml().get(class_id, {})
    if not isinstance(info, dict):
        return []
    raw_subs = info.get("subclasses", [])
    if not isinstance(raw_subs, list):
        return []
    for sub in raw_subs:
        if not isinstance(sub, dict) or sub.get("id") != subclass_id:
            continue
        features = sub.get("features", [])
        if isinstance(features, list):
            return [f for f in features if isinstance(f, dict)]
    return []


def subclass_skills_active(
    class_id: str, subclass_id: str | None, level: int
) -> bool:
    """Подкласс активен на уровне — навыки подкласса можно применять."""
    if not subclass_id:
        return False
    return level >= get_subclass_choice_level(class_id)


def get_subclass_fixed_skills(
    class_id: str, subclass_id: str | None, level: int
) -> list[str]:
    """Фиксированные навыки подкласса с учётом уровня персонажа."""
    if not subclass_skills_active(class_id, subclass_id, level):
        return []
    result: list[str] = []
    for feat in _subclass_features(class_id, subclass_id):
        feat_level = feat.get("level")
        if isinstance(feat_level, int) and feat_level > level:
            continue
        for skill_id in _skills_from_proficiency_feature(feat):
            if skill_id not in result:
                result.append(skill_id)
    return result


def get_subclass_skill_choices(
    class_id: str, subclass_id: str | None, level: int
) -> list[dict[str, Any]]:
    """Выборные навыки подкласса с учётом уровня персонажа."""
    if not subclass_skills_active(class_id, subclass_id, level):
        return []
    result: list[dict[str, Any]] = []
    for feat in _subclass_features(class_id, subclass_id):
        feat_level = feat.get("level")
        if isinstance(feat_level, int) and feat_level > level:
            continue
        mechanics = _skill_proficiency_mechanics(feat)
        if mechanics is None or not mechanics.get("choice"):
            continue
        result.append(mechanics)
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
