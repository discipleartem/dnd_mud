"""Загрузка рас и расовых бонусов из YAML."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.io import load_yaml

RACES_FILE = Path("database/races/races.yaml")


@lru_cache(maxsize=1)
def _load_races_yaml() -> dict[str, Any]:
    """Загрузить и закэшировать данные рас из YAML."""
    data = load_yaml(RACES_FILE)
    races = data.get("races", {})
    if isinstance(races, dict):
        return races
    return {}


def get_race_bonuses(
    race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Получить расовые и подрасовые бонусы к характеристикам."""
    bonuses: dict[str, int] = {}
    races = _load_races_yaml()
    race_info = races.get(race_id, {})
    if subrace_id:
        subraces = race_info.get("subraces", {})
        subrace_info = subraces.get(subrace_id, {})
        inherit_base = subrace_info.get("inherit_base_bonuses", True)
    else:
        subrace_info = {}
        inherit_base = True

    if inherit_base:
        base_bonuses = race_info.get("ability_bonuses", {})
        if isinstance(base_bonuses, dict):
            bonuses.update(base_bonuses)

    if subrace_id:
        sub_bonuses = subrace_info.get("ability_bonuses", {})
        if isinstance(sub_bonuses, dict):
            for stat, val in sub_bonuses.items():
                bonuses[stat] = bonuses.get(stat, 0) + val
    return bonuses


def _race_info_for_features(
    race_id: str, subrace_id: str | None = None
) -> dict[str, Any]:
    """Данные расы/подрасы для чтения features."""
    races = _load_races_yaml()
    race_info = races.get(race_id, {})
    if not isinstance(race_info, dict):
        return {}
    if subrace_id:
        subraces = race_info.get("subraces", {})
        subrace_info = subraces.get(subrace_id, {})
        if isinstance(subrace_info, dict):
            return subrace_info
    return race_info


def get_choice_ability_bonus_mechanics(
    race_id: str, subrace_id: str | None = None
) -> dict[str, Any] | None:
    """Механика выборного бонуса к характеристикам из features."""
    info = _race_info_for_features(race_id, subrace_id)
    for feat in info.get("features", []):
        if not isinstance(feat, dict):
            continue
        if feat.get("type") != "ability_bonus":
            continue
        mechanics = feat.get("mechanics", {})
        if isinstance(mechanics, dict) and mechanics.get("choice"):
            return mechanics
    return None


def has_choice_ability_bonuses(
    race_id: str, subrace_id: str | None = None
) -> bool:
    """Есть ли у расы/подрасы выборные бонусы к характеристикам."""
    return get_choice_ability_bonus_mechanics(race_id, subrace_id) is not None


def build_bonuses_from_choices(
    chosen_stats: list[str], value: int = 1
) -> dict[str, int]:
    """Собрать словарь бонусов из списка выбранных характеристик."""
    bonuses: dict[str, int] = {}
    for stat in chosen_stats:
        bonuses[stat] = bonuses.get(stat, 0) + value
    return bonuses


def get_effective_race_bonuses(
    race_id: str,
    subrace_id: str | None = None,
    choice_bonuses: dict[str, int] | None = None,
) -> dict[str, int]:
    """Статические и выборные расовые бонусы для отображения."""
    bonuses = get_race_bonuses(race_id, subrace_id)
    if choice_bonuses:
        for stat, val in choice_bonuses.items():
            bonuses[stat] = bonuses.get(stat, 0) + val
    return bonuses


def load_races() -> list[dict[str, Any]]:
    """Загрузить список всех доступных рас."""
    result: list[dict[str, Any]] = []
    for race_id, race_info in _load_races_yaml().items():
        if isinstance(race_info, dict):
            result.append(
                {
                    "id": race_id,
                    "name": race_info.get("name", race_id),
                }
            )
    return result


def load_race_full(race_id: str) -> dict[str, Any]:
    """Загрузить полные данные расы по ID."""
    race_info = _load_races_yaml().get(race_id, {})
    if isinstance(race_info, dict):
        return race_info
    return {}
