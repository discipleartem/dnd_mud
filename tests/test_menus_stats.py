"""Тесты UX генерации характеристик."""

import pytest

from core.character import STAT_NAMES
from ui import menus
from ui.menus import _common, _deps, stats_flow
from ui.menus.stats import stats_methods, stats_shared


def test_method_menu_hides_race_bonuses(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """На экране выбора метода расовые бонусы не показываются."""
    patch_int_input(monkeypatch, menus, [0])

    result = stats_flow.show_stats_generation_flow(
        ru_strings, "half_orc", None, "normal"
    )
    output = capsys.readouterr().out

    assert result is None
    assert "Расовые бонусы" not in output
    assert "Стандартный массив" in output


def test_race_bonuses_shown_after_standard_array_choice(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """После выбора стандартного массива показываются расовые бонусы."""
    patch_int_input(monkeypatch, menus, [1, 0, 0])
    monkeypatch.setattr(_common, "_press_enter", lambda strings: None)
    monkeypatch.setattr(
        _deps,
        "get_race_bonuses",
        lambda race_id, subrace_id=None: {"strength": 2},
    )

    result = stats_flow.show_stats_generation_flow(
        ru_strings, "half_orc", None, "normal"
    )
    output = capsys.readouterr().out

    assert result is None
    assert "Расовые бонусы" in output
    assert "Сила +2" in output


def test_prompt_pool_value_manual_rejects_invalid(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Standard array: отклоняет значение вне пула."""
    patch_int_input(monkeypatch, menus, [99, 15])

    result = stats_flow._prompt_pool_value_manual(
        ru_strings,
        "Сила",
        [15, 14, 13, 12, 10, 8],
        value_min=8,
        value_max=15,
    )
    output = capsys.readouterr().out

    assert result == 15
    assert "недоступно" in output


def test_point_buy_finish_blocked_with_unspent_points(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Point buy: нельзя завершить, пока не распределены все очки."""
    confirm_called: list[bool] = []

    class StopLoopError(Exception):
        pass

    def fake_press_enter(strings: object) -> None:
        raise StopLoopError

    def fake_confirm(*args: object, **kwargs: object) -> str:
        confirm_called.append(True)
        return "back"

    monkeypatch.setattr(stats_shared, "_confirm_stats", fake_confirm)
    monkeypatch.setattr(_common, "_press_enter", fake_press_enter)
    patch_int_input(monkeypatch, menus, [0])

    with pytest.raises(StopLoopError):
        stats_flow._select_stats_point_buy(ru_strings, "human", None)

    output = capsys.readouterr().out
    assert "Распределите все очки! Осталось: 27." in output
    assert confirm_called == []


def test_point_buy_finish_allowed_when_budget_exhausted(
    monkeypatch, ru_strings, patch_int_input
):
    """Point buy: завершение доступно при полном расходе бюджета."""
    build = iter([15, 14, 13, 12, 10, 8])
    confirm_called: list[bool] = []

    def fake_prompt(strings, stat_name, stats, stat):
        stats[stat] = next(build)

    def fake_confirm(*args: object, **kwargs: object) -> str:
        confirm_called.append(True)
        return "back"

    monkeypatch.setattr(
        stats_methods, "_prompt_point_buy_stat_value", fake_prompt
    )
    patch_int_input(monkeypatch, menus, [1, 2, 3, 4, 5, 6, 0])
    monkeypatch.setattr(stats_shared, "_confirm_stats", fake_confirm)

    stats_flow._select_stats_point_buy(ru_strings, "human", None)

    assert confirm_called == [True]
    assert list(build) == []


def test_variant_human_standard_array_applies_choice_bonuses(
    monkeypatch, ru_strings, patch_int_input
):
    """Человек (вариант): выбор 2 характеристик +1."""
    base_stats = dict(zip(STAT_NAMES, [15, 14, 13, 12, 10, 8], strict=True))

    monkeypatch.setattr(
        stats_methods,
        "_assign_stats_from_pool",
        lambda *args, **kwargs: dict(base_stats),
    )
    patch_int_input(monkeypatch, menus, [1, 1, 1])

    result = stats_flow._select_stats_standard_array(
        ru_strings, "human", "variant_human"
    )

    assert result is not None
    assert result["strength"] == 16
    assert result["dexterity"] == 15


def test_variant_human_choice_cancel_redistributes(
    monkeypatch, ru_strings, patch_int_input
):
    """Отмена выбора бонуса возвращает к перераспределению."""
    base_stats = dict(zip(STAT_NAMES, [15, 14, 13, 12, 10, 8], strict=True))
    assign_calls = {"count": 0}

    def fake_assign(*args, **kwargs):
        assign_calls["count"] += 1
        if assign_calls["count"] == 1:
            return dict(base_stats)
        return None

    monkeypatch.setattr(stats_methods, "_assign_stats_from_pool", fake_assign)
    patch_int_input(monkeypatch, menus, [0])

    result = stats_flow._select_stats_standard_array(
        ru_strings, "human", "variant_human"
    )

    assert result is None
    assert assign_calls["count"] == 2


def test_hardcore_race_bonus_back_preserves_rolls(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """HardCore 4d6: «Назад» с бонусов не перебрасывает кости."""
    roll_sequence = iter([15, 13, 9, 9, 14, 14])
    roll_calls = {"count": 0}

    def fake_roll() -> int:
        roll_calls["count"] += 1
        return next(roll_sequence)

    class StopLoopError(Exception):
        pass

    enter_count = {"n": 0}

    def fake_press_enter(strings: object) -> None:
        enter_count["n"] += 1
        if enter_count["n"] >= 2:
            raise StopLoopError

    monkeypatch.setattr(_deps, "roll_ability_score", fake_roll)
    monkeypatch.setattr(_common, "_press_enter", fake_press_enter)
    patch_int_input(monkeypatch, menus, [0])

    with pytest.raises(StopLoopError):
        stats_flow._select_stats_random_hardcore(
            ru_strings, "human", "variant_human"
        )

    output = capsys.readouterr().out
    assert roll_calls["count"] == 6
    assert "15" in output and "13" in output


def test_confirm_stats_shows_bonus_after_choice(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Экран подтверждения показывает (+1) после выбора бонусов."""
    stats = {stat: 10 for stat in STAT_NAMES}
    stats["strength"] = 16
    stats["dexterity"] = 15
    race_bonuses = {"strength": 1, "dexterity": 1}

    patch_int_input(monkeypatch, menus, [0])

    stats_flow._confirm_stats(
        ru_strings,
        stats,
        "human",
        "variant_human",
        reroll_label_key="character.stats_reroll_redistribute",
        race_bonuses=race_bonuses,
    )
    output = capsys.readouterr().out

    assert "(+1)" in output


def test_show_stats_generation_flow_loops_on_method_back(
    monkeypatch, ru_strings, patch_int_input
):
    """При «Назад» с подтверждения flow возвращается к меню методов."""
    calls = {"standard": 0}
    final_stats = dict.fromkeys(STAT_NAMES, 10)

    def fake_standard_array(strings, race_id, subrace_id):
        calls["standard"] += 1
        if calls["standard"] == 1:
            return None
        return final_stats

    patch_int_input(monkeypatch, menus, [1, 1])
    monkeypatch.setattr(
        "ui.menus.stats.stats_flow._select_stats_standard_array",
        fake_standard_array,
    )

    result = stats_flow.show_stats_generation_flow(
        ru_strings, "human", None, "normal"
    )

    assert calls["standard"] == 2
    assert result == final_stats
