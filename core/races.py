"""Загрузка рас и расовых бонусов из YAML."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.io import load_yaml
from core.localization import resolve_localized_text

RACES_FILE = Path("database/races/races.yaml")


@lru_cache(maxsize=1)
def _load_races_yaml() -> dict[str, Any]:
    """Загрузить и закэшировать данные рас из YAML."""
    data = load_yaml(RACES_FILE)
    races = data.get("races", {})
    if isinstance(races, dict):
        return races
    return {}


def _get_race_and_subrace(
    race_id: str, subrace_id: str | None = None
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Получить данные расы и подрасы из YAML."""
    races = _load_races_yaml()
    race_info = races.get(race_id, {})
    if not isinstance(race_info, dict):
        return {}, None
    if not subrace_id:
        return race_info, None
    subraces = race_info.get("subraces", {})
    if not isinstance(subraces, dict):
        return race_info, None
    subrace_info = subraces.get(subrace_id, {})
    if isinstance(subrace_info, dict):
        return race_info, subrace_info
    return race_info, None


def _merge_bonus_dicts(
    base: dict[str, int], extra: dict[str, int]
) -> dict[str, int]:
    """Сложить два словаря бонусов к характеристикам."""
    result = dict(base)
    for stat, val in extra.items():
        result[stat] = result.get(stat, 0) + val
    return result


def get_race_bonuses(
    race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Получить расовые и подрасовые бонусы к характеристикам."""
    race_info, subrace_info = _get_race_and_subrace(race_id, subrace_id)
    if not race_info:
        return {}

    if subrace_id and subrace_info:
        inherit_base = subrace_info.get("inherit_base_bonuses", True)
    else:
        inherit_base = True

    bonuses: dict[str, int] = {}
    if inherit_base:
        base_bonuses = race_info.get("ability_bonuses", {})
        if isinstance(base_bonuses, dict):
            bonuses.update(base_bonuses)

    if subrace_id and subrace_info:
        sub_bonuses = subrace_info.get("ability_bonuses", {})
        if isinstance(sub_bonuses, dict):
            bonuses = _merge_bonus_dicts(bonuses, sub_bonuses)
    return bonuses


def _race_info_for_features(
    race_id: str, subrace_id: str | None = None
) -> dict[str, Any]:
    """Данные расы/подрасы для чтения features."""
    race_info, subrace_info = _get_race_and_subrace(race_id, subrace_id)
    if subrace_id and subrace_info:
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
        bonuses = _merge_bonus_dicts(bonuses, {stat: value})
    return bonuses


def get_effective_race_bonuses(
    race_id: str,
    subrace_id: str | None = None,
    choice_bonuses: dict[str, int] | None = None,
) -> dict[str, int]:
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
    if "base_choice_name" in result:
        result["base_choice_name"] = resolve_localized_text(
            result["base_choice_name"],
            language,
            fallback=str(result.get("name", "")),
        )
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
    race_info, _ = _get_race_and_subrace(race_id)
    if race_info:
        return _localize_race_info(race_info, language)
    return {}
