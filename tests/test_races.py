"""Тесты загрузки рас из YAML."""

from core.races import get_race_bonuses, load_races


def test_load_races_returns_non_empty_list() -> None:
    races = load_races()
    assert len(races) > 0
    assert "id" in races[0]
    assert "name" in races[0]


def test_get_race_bonuses_human() -> None:
    bonuses = get_race_bonuses("human")
    assert isinstance(bonuses, dict)
    assert len(bonuses) > 0
