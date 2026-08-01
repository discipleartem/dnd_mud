"""Тесты кубиков, констант PHB, point-buy и сложности приключений."""

import random

import pytest

from core.catalogs.adventure import Adventure
from core.character.models import Character
from core.constants import (
    ability_modifier,
    proficiency_bonus,
)
from core.engine.difficulty import (
    adventure_allows_difficulty,
    adventure_requires_hardcore,
    adventure_unavailable_reason,
)
from core.mechanics import dice
from core.mechanics.stats import (
    ABILITY_SCORE_MAX,
    ABILITY_SCORE_MIN,
    STAT_NAMES,
    point_buy_points_remaining,
    validate_final_stats,
    validate_point_buy_finish,
)
from core.types import CharacterClass
from tests.creation_helpers import flat_stats


@pytest.mark.parametrize(
    "level,expected_bonus",
    [(1, 2), (5, 3)],
)
def test_proficiency_bonus(level: int, expected_bonus: int) -> None:
    assert proficiency_bonus(level) == expected_bonus


def test_dice_roll(monkeypatch: pytest.MonkeyPatch) -> None:
    values = iter([3, 5])
    monkeypatch.setattr(random, "randint", lambda _a, _b: next(values))
    assert dice.roll(count=2, sides=6, modifier=2) == 10


@pytest.mark.parametrize(
    "score,expected",
    [
        (1, -5),
        (9, -1),
        (10, 0),
        (11, 0),
        (20, 5),
        (0, -5),
        (22, 6),
        (25, 7),
        (30, 10),
        (31, 10),
    ],
)
def test_ability_modifier(score: int, expected: int) -> None:
    assert ability_modifier(score) == expected


def test_validate_final_stats_bounds() -> None:
    base = flat_stats(10)
    assert validate_final_stats(base) is None
    over = dict(base)
    over["strength"] = ABILITY_SCORE_MAX + 1
    assert validate_final_stats(over) == ("strength", ABILITY_SCORE_MAX + 1)
    under = dict(base)
    under["dexterity"] = ABILITY_SCORE_MIN - 1
    assert validate_final_stats(under) == ("dexterity", 0)


def test_point_buy_validation() -> None:
    full = [15, 14, 13, 12, 10, 8]
    assert validate_point_buy_finish(full) is None
    assert point_buy_points_remaining(full) == 0
    low = [8, 8, 8, 8, 8, 8]
    assert validate_point_buy_finish(low) == "character.stats_points_unspent"
    assert len(low) == len(STAT_NAMES)


def test_adventure_difficulty_rules() -> None:
    open_adv = Adventure(id="test", name="Test")
    assert adventure_allows_difficulty(open_adv, "normal") is True
    hc = Adventure(id="hc", name="HC", hardcore_only=True)
    assert adventure_allows_difficulty(hc, "hardcore") is True
    assert adventure_allows_difficulty(hc, "normal") is False
    hc_list = Adventure(
        id="hc_list",
        name="HC",
        allowed_game_difficulties=["hardcore"],
    )
    assert adventure_requires_hardcore(hc_list) is True


def test_adventure_unavailable_reason() -> None:
    high = Adventure(id="high", name="High", min_level=5)
    char = Character(
        name="Hero", race="human", class_id=CharacterClass.FIGHTER, level=1
    )
    assert (
        adventure_unavailable_reason(high, char)
        == "adventures.unavailable_reason_level"
    )
    hc = Adventure(id="hc", name="HC", hardcore_only=True)
    normal_char = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
        difficulty="normal",
    )
    assert (
        adventure_unavailable_reason(hc, normal_char)
        == "adventures.unavailable_reason_hardcore"
    )
