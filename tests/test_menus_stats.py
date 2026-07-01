"""Тесты UX генерации характеристик."""

import pytest

from core.stats import STAT_NAMES
from ui.menus import _common, _deps
from ui.menus import stats as stats_menu
from ui.menus.stats import stats_methods, stats_shared


def test_standard_array_shows_race_bonuses_after_assign(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    patch_int_input(monkeypatch, [1, 0, 0])
    monkeypatch.setattr(_common, "_press_enter", lambda strings: None)
    monkeypatch.setattr(
        _deps,
        "get_race_bonuses",
        lambda race_id, subrace_id=None: {"strength": 2},
    )
    result = stats_menu.show_stats_generation_flow(
        ru_strings, "half_orc", None, "normal"
    )
    output = capsys.readouterr().out
    assert result is None
    assert "Расовые бонусы" in output
    assert "Сила +2" in output


def test_point_buy_finish_blocked_with_unspent_points(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    class StopLoopError(Exception):
        pass

    def fake_press_enter(strings: object) -> None:
        raise StopLoopError

    monkeypatch.setattr(stats_shared, "_confirm_stats", lambda *a, **k: "back")
    monkeypatch.setattr(stats_methods, "_press_enter", fake_press_enter)
    patch_int_input(monkeypatch, [0])
    with pytest.raises(StopLoopError):
        stats_methods._select_stats_point_buy(ru_strings, "human", None)
    assert "Распределите все очки!" in capsys.readouterr().out


def test_variant_human_standard_array_applies_choice_bonuses(
    monkeypatch, ru_strings, patch_int_input
):
    base_stats = dict(zip(STAT_NAMES, [15, 14, 13, 12, 10, 8], strict=True))
    monkeypatch.setattr(
        stats_methods,
        "_assign_stats_from_pool",
        lambda *args, **kwargs: dict(base_stats),
    )
    patch_int_input(monkeypatch, [1, 1, 1])
    result = stats_methods._select_stats_standard_array(
        ru_strings, "human", "variant_human"
    )
    assert result is not None
    assert result["strength"] == 16
    assert result["dexterity"] == 15


def test_hardcore_4d6_no_regenerate_option(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    monkeypatch.setattr(_deps, "roll_ability_score", lambda: 12)
    monkeypatch.setattr(stats_methods, "_press_enter", lambda strings: None)
    patch_int_input(monkeypatch, [1])
    stats_methods._select_stats_random_hardcore(ru_strings, "elf", None)
    output = capsys.readouterr().out
    assert "Принять характеристики" in output
    assert "Перегенерировать" not in output
