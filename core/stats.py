"""Генерация и валидация характеристик персонажа."""

from core.races import get_race_bonuses

STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
STANDARD_ARRAY_MIN = min(STANDARD_ARRAY)
STANDARD_ARRAY_MAX = max(STANDARD_ARRAY)

STAT_NAMES = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]

POINT_BUY_BUDGET = 27
POINT_BUY_COSTS: dict[int, int] = {
    8: 0,
    9: 1,
    10: 2,
    11: 3,
    12: 4,
    13: 5,
    14: 7,
    15: 9,
}
POINT_BUY_MIN = min(POINT_BUY_COSTS)
POINT_BUY_MAX = max(POINT_BUY_COSTS)


def point_buy_cost(score: int) -> int:
    """Стоимость значения характеристики в point-buy."""
    return POINT_BUY_COSTS.get(score, 0)


def remaining_standard_array_pool(used: list[int]) -> list[int]:
    """Остаток стандартного массива после уже назначенных значений."""
    pool = list(STANDARD_ARRAY)
    for value in used:
        if value in pool:
            pool.remove(value)
    return sorted(pool, reverse=True)


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


def can_assign_point_buy_value(
    current: dict[str, int], stat: str, new_value: int
) -> bool:
    """Проверить, допустимо ли новое значение (8–15, бюджет не превышен)."""
    if new_value not in POINT_BUY_COSTS:
        return False
    updated = dict(current)
    updated[stat] = new_value
    values = [updated[name] for name in STAT_NAMES]
    return point_buy_total_cost(values) <= POINT_BUY_BUDGET


def apply_bonuses_to_stats(
    stats: dict[str, int], bonuses: dict[str, int]
) -> dict[str, int]:
    """Добавить бонусы к характеристикам."""
    final_stats = stats.copy()
    for stat_name, bonus in bonuses.items():
        if stat_name in final_stats:
            final_stats[stat_name] += bonus
        else:
            final_stats[stat_name] = bonus
    return final_stats


def _apply_racial_bonuses_to_stats(
    base_stats: dict[str, int], race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Применить расовые и подрасовые бонусы к базовым характеристикам."""
    bonuses = get_race_bonuses(race_id, subrace_id)
    return apply_bonuses_to_stats(base_stats, bonuses)


def _build_stats(
    values: list[int], race_id: str, subrace_id: str | None = None
) -> dict[str, int]:
    """Собрать характеристики из шести значений и применить бонусы расы."""
    if len(values) != len(STAT_NAMES):
        raise ValueError(
            f"Expected {len(STAT_NAMES)} values, got {len(values)}"
        )
    base_stats = dict(zip(STAT_NAMES, values, strict=True))
    return _apply_racial_bonuses_to_stats(base_stats, race_id, subrace_id)


def generate_stats_standard_array(
    selected_values: list[int],
    race_id: str,
    subrace_id: str | None = None,
) -> dict[str, int]:
    """Сгенерировать характеристики из стандартного массива."""
    return _build_stats(selected_values, race_id, subrace_id)


def generate_stats_point_buy(
    point_buy_values: list[int],
    race_id: str,
    subrace_id: str | None = None,
) -> dict[str, int]:
    """Сгенерировать характеристики методом покупки очков."""
    return _build_stats(point_buy_values, race_id, subrace_id)


def generate_stats_random(
    random_values: list[int],
    race_id: str,
    subrace_id: str | None = None,
) -> dict[str, int]:
    """Сгенерировать характеристики случайным методом."""
    return _build_stats(random_values, race_id, subrace_id)
