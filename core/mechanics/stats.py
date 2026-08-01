"""Генерация и валидация характеристик персонажа."""

from core.catalogs.abilities import ability_ids
from core.catalogs.races import get_race_bonuses
from core.constants import (
    ABILITY_SCORE_DEFAULT,
    ABILITY_SCORE_MAX,
    ABILITY_SCORE_MIN,
    POINT_BUY_BUDGET,
    POINT_BUY_COSTS,
    STANDARD_ARRAY,
    STANDARD_ARRAY_MAX,
    STANDARD_ARRAY_MIN,
)
from core.types import StatMap

STAT_NAMES: list[str] = list(ability_ids())

__all__ = [
    "ABILITY_SCORE_DEFAULT",
    "ABILITY_SCORE_MAX",
    "ABILITY_SCORE_MIN",
    "POINT_BUY_BUDGET",
    "POINT_BUY_COSTS",
    "STANDARD_ARRAY",
    "STANDARD_ARRAY_MAX",
    "STANDARD_ARRAY_MIN",
    "STAT_NAMES",
    "apply_bonuses_to_stats",
    "apply_racial_bonuses_to_stats",
    "can_assign_point_buy_value",
    "generate_stats_point_buy",
    "generate_stats_random",
    "generate_stats_standard_array",
    "point_buy_cost",
    "point_buy_points_remaining",
    "point_buy_total_cost",
    "validate_final_stats",
    "validate_point_buy_finish",
]


def point_buy_cost(score: int) -> int:
    """Стоимость значения характеристики в point-buy."""
    return POINT_BUY_COSTS.get(score, 0)


def point_buy_total_cost(values: list[int]) -> int:
    """Суммарная стоимость набора характеристик в point-buy."""
    return sum(point_buy_cost(value) for value in values)


def point_buy_points_remaining(values: list[int]) -> int:
    """Оставшиеся очки point-buy (0 — распределение завершено)."""
    return POINT_BUY_BUDGET - point_buy_total_cost(values)


def validate_point_buy_finish(values: list[int]) -> str | None:
    """Проверить завершение распределения point-buy.

    Returns:
        Ключ строки локализации ошибки или None, если распределение корректно
    """
    remaining = point_buy_points_remaining(values)
    if remaining == 0:
        return None
    if remaining > 0:
        return "character.stats_points_unspent"
    return "character.stats_points_overspent"


def validate_final_stats(stats: StatMap) -> tuple[str, int] | None:
    """Проверить потолок характеристик после всех бонусов (PHB: 20).

    Returns:
        (stat_id, value) первого превышения или None
    """
    for stat in STAT_NAMES:
        value = stats.get(stat, 0)
        if value < ABILITY_SCORE_MIN:
            return stat, value
        if value > ABILITY_SCORE_MAX:
            return stat, value
    return None


def can_assign_point_buy_value(
    current: StatMap, stat: str, new_value: int
) -> bool:
    """Проверить, допустимо ли новое значение (8–15, бюджет не превышен)."""
    if new_value not in POINT_BUY_COSTS:
        return False
    updated = dict(current)
    updated[stat] = new_value
    values = [updated[name] for name in STAT_NAMES]
    return point_buy_total_cost(values) <= POINT_BUY_BUDGET


def apply_bonuses_to_stats(stats: StatMap, bonuses: StatMap) -> StatMap:
    """Добавить бонусы к характеристикам."""
    final_stats = stats.copy()
    for stat_name, bonus in bonuses.items():
        if stat_name in final_stats:
            final_stats[stat_name] += bonus
        else:
            final_stats[stat_name] = bonus
    return final_stats


def apply_racial_bonuses_to_stats(
    base_stats: StatMap, race_id: str, subrace_id: str | None = None
) -> StatMap:
    """Применить расовые и подрасовые бонусы к базовым характеристикам."""
    bonuses = get_race_bonuses(race_id, subrace_id)
    return apply_bonuses_to_stats(base_stats, bonuses)


def _build_stats(
    values: list[int], race_id: str, subrace_id: str | None = None
) -> StatMap:
    """Собрать характеристики из шести значений и применить бонусы расы."""
    if len(values) != len(STAT_NAMES):
        raise ValueError(
            f"Expected {len(STAT_NAMES)} values, got {len(values)}"
        )
    base_stats = dict(zip(STAT_NAMES, values, strict=True))
    return apply_racial_bonuses_to_stats(base_stats, race_id, subrace_id)


def generate_stats_standard_array(
    selected_values: list[int],
    race_id: str,
    subrace_id: str | None = None,
) -> StatMap:
    """Сгенерировать характеристики из стандартного массива."""
    return _build_stats(selected_values, race_id, subrace_id)


def generate_stats_point_buy(
    point_buy_values: list[int],
    race_id: str,
    subrace_id: str | None = None,
) -> StatMap:
    """Сгенерировать характеристики методом покупки очков."""
    return _build_stats(point_buy_values, race_id, subrace_id)


def generate_stats_random(
    random_values: list[int],
    race_id: str,
    subrace_id: str | None = None,
) -> StatMap:
    """Сгенерировать характеристики случайным методом."""
    return _build_stats(random_values, race_id, subrace_id)
