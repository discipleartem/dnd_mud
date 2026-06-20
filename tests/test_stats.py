"""Тесты генерации и валидации характеристик."""

from core.stats import (
    POINT_BUY_BUDGET,
    STAT_NAMES,
    point_buy_points_remaining,
    validate_point_buy_finish,
)


def test_validate_point_buy_finish_accepts_full_budget() -> None:
    values = [15, 14, 13, 12, 10, 8]
    assert validate_point_buy_finish(values) is None
    assert point_buy_points_remaining(values) == 0


def test_validate_point_buy_finish_rejects_unspent_points() -> None:
    values = [8, 8, 8, 8, 8, 8]
    assert (
        validate_point_buy_finish(values) == "character.stats_points_unspent"
    )
    assert point_buy_points_remaining(values) == POINT_BUY_BUDGET


def test_validate_point_buy_finish_rejects_overspent_budget() -> None:
    values = [15, 15, 15, 15, 15, 15]
    assert (
        validate_point_buy_finish(values) == "character.stats_points_overspent"
    )
    assert point_buy_points_remaining(values) < 0


def test_point_buy_points_remaining_matches_stat_names_length() -> None:
    values = [10, 10, 10, 10, 10, 10]
    assert len(values) == len(STAT_NAMES)
    assert point_buy_points_remaining(values) == POINT_BUY_BUDGET - 12
