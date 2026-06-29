"""Загрузка рас и расовых бонусов из YAML."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.grants import (
    _ABILITY_INCREASE,
    grants_from_entity,
    grants_of_type,
    inherit_flags,
    merge_entity_grants,
)
from core.hp_bonuses import (
    HpBonusSource,
    hit_point_bonus_sources_from_features,
)
from core.localization import resolve_localized_text
from core.mod_loader import load_merged_catalog
from core.types import StatMap

RACES_FILE = Path("database/races/races.yaml")


def clear_races_cache() -> None:
    """Сбросить кэш рас (для тестов)."""
    _load_races_yaml.cache_clear()


@lru_cache(maxsize=1)
def _load_races_yaml() -> dict[str, Any]:
    """Загрузить и закэшировать данные рас из YAML."""
    return load_merged_catalog(str(RACES_FILE), "races")


def resolve_subrace_id(race_id: str, subrace_id: str | None) -> str | None:
    """Нормализовать id подрасы (fallback human → standard)."""
    race_info = _load_races_yaml().get(race_id, {})
    if not isinstance(race_info, dict):
        return subrace_id
    subraces = race_info.get("subraces", {})
    if not isinstance(subraces, dict) or not subraces:
        return subrace_id
    if subrace_id and subrace_id in subraces:
        return subrace_id
    if subrace_id is None and race_id == "human" and "standard" in subraces:
        return "standard"
    if subrace_id is None and len(subraces) == 1:
        return str(next(iter(subraces)))
    return subrace_id


def get_race_and_subrace(
    race_id: str, subrace_id: str | None = None
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Получить данные расы и подрасы из YAML."""
    races = _load_races_yaml()
    race_info = races.get(race_id, {})
    if not isinstance(race_info, dict):
        return {}, None
    resolved = resolve_subrace_id(race_id, subrace_id)
    if not resolved:
        return race_info, None
    subraces = race_info.get("subraces", {})
    if not isinstance(subraces, dict):
        return race_info, None
    subrace_info = subraces.get(resolved, {})
    if isinstance(subrace_info, dict):
        return race_info, subrace_info
    return race_info, None


def _merge_bonus_dicts(base: StatMap, extra: StatMap) -> StatMap:
    """Сложить два словаря бонусов к характеристикам."""
    result = dict(base)
    for stat, val in extra.items():
        result[stat] = result.get(stat, 0) + val
    return result


def get_race_bonuses(race_id: str, subrace_id: str | None = None) -> StatMap:
    """Получить расовые и подрасовые бонусы к характеристикам."""
    race_info, subrace_info = get_race_and_subrace(race_id, subrace_id)
    if not race_info:
        return {}

    bonuses: StatMap = {}
    if subrace_info:
        inherit_bonuses, _ = inherit_flags(subrace_info)
        if inherit_bonuses:
            base_bonuses = race_info.get("ability_bonuses", {})
            if isinstance(base_bonuses, dict):
                bonuses.update(base_bonuses)
        sub_bonuses = subrace_info.get("ability_bonuses", {})
        if isinstance(sub_bonuses, dict):
            bonuses = _merge_bonus_dicts(bonuses, sub_bonuses)
    else:
        base_bonuses = race_info.get("ability_bonuses", {})
        if isinstance(base_bonuses, dict):
            bonuses.update(base_bonuses)
    return bonuses


def collect_race_grants(
    race_id: str, subrace_id: str | None = None
) -> list[dict[str, Any]]:
    """Grants расы и подрасы с учётом наследования."""
    race_info, subrace_info = get_race_and_subrace(race_id, subrace_id)
    if not race_info:
        return []
    if subrace_info:
        return merge_entity_grants(race_info, subrace_info, use_parent=True)
    return grants_from_entity(race_info)


def grants_as_features(grants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Legacy-вид features для существующих парсеров."""
    result: list[dict[str, Any]] = []
    for grant in grants:
        gtype = str(grant.get("type", ""))
        legacy_type = "ability_bonus" if gtype == _ABILITY_INCREASE else gtype
        mechanics = dict(grant)
        if "type" in mechanics:
            del mechanics["type"]
        if "amount" in mechanics and "value" not in mechanics:
            mechanics["value"] = mechanics["amount"]
        if legacy_type == "feat" and "from" in mechanics:
            mechanics.setdefault("from_list", mechanics["from"])
        entry: dict[str, Any] = {"type": legacy_type, "mechanics": mechanics}
        if grant.get("name"):
            entry["name"] = grant["name"]
        result.append(entry)
    return result


def collect_race_features(
    race_id: str, subrace_id: str | None = None
) -> list[dict[str, Any]]:
    """Особенности расы и подрасы (legacy features из grants)."""
    return grants_as_features(collect_race_grants(race_id, subrace_id))


def get_choice_ability_bonus_mechanics(
    race_id: str, subrace_id: str | None = None
) -> dict[str, Any] | None:
    """Механика выборного бонуса к характеристикам из grants."""
    for grant in grants_of_type(
        collect_race_grants(race_id, subrace_id), _ABILITY_INCREASE
    ):
        if grant.get("choice"):
            mechanics = dict(grant)
            if "amount" in mechanics and "value" not in mechanics:
                mechanics["value"] = mechanics["amount"]
            return mechanics
    return None


def has_choice_ability_bonuses(
    race_id: str, subrace_id: str | None = None
) -> bool:
    """Есть ли у расы/подрасы выборные бонусы к характеристикам."""
    return get_choice_ability_bonus_mechanics(race_id, subrace_id) is not None


def build_bonuses_from_choices(
    chosen_stats: list[str], value: int = 1
) -> StatMap:
    """Собрать словарь бонусов из списка выбранных характеристик."""
    bonuses: StatMap = {}
    for stat in chosen_stats:
        bonuses = _merge_bonus_dicts(bonuses, {stat: value})
    return bonuses


def get_racial_hp_bonus_sources(
    race_id: str, subrace_id: str | None = None
) -> list[HpBonusSource]:
    """Именованные бонусы HP за уровень из особенностей расы/подрасы."""
    return hit_point_bonus_sources_from_features(
        collect_race_features(race_id, subrace_id)
    )


def get_racial_hp_bonus_per_level(
    race_id: str, subrace_id: str | None = None
) -> int:
    """Дополнительные HP за каждый уровень (hit_point_bonus, per_level)."""
    sources = get_racial_hp_bonus_sources(race_id, subrace_id)
    return sum(s.amount for s in sources)


def get_effective_race_bonuses(
    race_id: str,
    subrace_id: str | None = None,
    choice_bonuses: StatMap | None = None,
) -> StatMap:
    """Статические и выборные расовые бонусы для отображения."""
    bonuses = get_race_bonuses(race_id, subrace_id)
    if choice_bonuses:
        bonuses = _merge_bonus_dicts(bonuses, choice_bonuses)
    return bonuses


def _localize_race_info(
    race_info: dict[str, Any], language: str
) -> dict[str, Any]:
    """Резолвить локализованные поля name в данных расы."""
    result = dict(race_info)
    if "name" in result:
        result["name"] = resolve_localized_text(result["name"], language)
    subraces = result.get("subraces")
    if isinstance(subraces, dict):
        localized_subraces: dict[str, Any] = {}
        for subrace_id, subrace_info in subraces.items():
            if isinstance(subrace_info, dict):
                sub = dict(subrace_info)
                if "name" in sub:
                    sub["name"] = resolve_localized_text(
                        sub["name"], language, fallback=subrace_id
                    )
                localized_subraces[subrace_id] = sub
            else:
                localized_subraces[subrace_id] = subrace_info
        result["subraces"] = localized_subraces
    return result


def load_races(language: str = "ru") -> list[dict[str, Any]]:
    """Загрузить список всех доступных рас."""
    result: list[dict[str, Any]] = []
    for race_id, race_info in _load_races_yaml().items():
        if isinstance(race_info, dict):
            result.append(
                {
                    "id": race_id,
                    "name": resolve_localized_text(
                        race_info.get("name", race_id),
                        language,
                        fallback=race_id,
                    ),
                }
            )
    return result


def load_race_full(race_id: str, language: str = "ru") -> dict[str, Any]:
    """Загрузить полные данные расы по ID."""
    race_info, _ = get_race_and_subrace(race_id)
    if race_info:
        return _localize_race_info(race_info, language)
    return {}


def auto_select_subrace_id(race_id: str) -> str | None:
    """Автовыбор подрасы, если в YAML ровно одна."""
    race_info = _load_races_yaml().get(race_id, {})
    if not isinstance(race_info, dict):
        return None
    subraces = race_info.get("subraces", {})
    if isinstance(subraces, dict) and len(subraces) == 1:
        return str(next(iter(subraces)))
    return None
