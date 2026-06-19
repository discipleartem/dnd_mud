"""Тесты UX генерации характеристик."""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def ru_strings():
    """Строки локализации ru."""
    from core.localization import load_strings

    return load_strings("ru")


def test_method_menu_hides_race_bonuses(monkeypatch, capsys, ru_strings):
    """На экране выбора метода расовые бонусы не показываются."""
    from ui import menus

    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )

    result = menus.show_stats_generation_flow(
        ru_strings, "half_orc", None, "normal"
    )
    output = capsys.readouterr().out

    assert result is None
    assert "Расовые бонусы" not in output
    assert "Стандартный массив" in output


def test_race_bonuses_shown_before_standard_array(
    monkeypatch, capsys, ru_strings
):
    """После выбора стандартного массива показываются расовые бонусы."""
    from ui import menus

    inputs = iter([1, 0, 0])

    monkeypatch.setattr(menus, "_press_enter", lambda strings: None)
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: next(inputs),
    )
    monkeypatch.setattr(
        menus,
        "get_race_bonuses",
        lambda race_id, subrace_id=None: {"strength": 2},
    )

    result = menus.show_stats_generation_flow(
        ru_strings, "half_orc", None, "normal"
    )
    output = capsys.readouterr().out

    assert result is None
    assert "Расовые бонусы" in output
    assert "Сила +2" in output
    bonus_pos = output.find("Расовые бонусы")
    avail_pos = output.find("Доступные значения")
    assert bonus_pos != -1 and avail_pos != -1 and bonus_pos < avail_pos
    assert "Введите значение" in output
    assert "[Enter]" not in output[bonus_pos:avail_pos]


def test_prompt_pool_value_manual_rejects_invalid(
    monkeypatch, capsys, ru_strings
):
    """Standard array: отклоняет значение вне пула."""
    from ui import menus

    inputs = iter([99, 15])

    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: next(inputs),
    )

    result = menus._prompt_pool_value_manual(
        ru_strings, "Сила", [15, 14, 13, 12, 10, 8]
    )
    output = capsys.readouterr().out

    assert result == 15
    assert "недоступно" in output


def test_prompt_point_buy_allows_lowering_stat(monkeypatch, ru_strings):
    """Point buy: можно понизить характеристику и освободить очки."""
    from core.character import STAT_NAMES
    from ui import menus

    stats = dict.fromkeys(STAT_NAMES, 8)
    stats["strength"] = 15
    stats["dexterity"] = 15
    stats["constitution"] = 15

    inputs = iter([10])

    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: next(inputs),
    )

    menus._prompt_point_buy_stat_value(ru_strings, "Сила", stats, "strength")

    assert stats["strength"] == 10


def test_random_normal_accept_shows_roll_menu(monkeypatch, capsys, ru_strings):
    """Random Normal: после броска — меню «Принять / Перегенерировать»."""
    from ui import menus

    monkeypatch.setattr(menus, "roll_ability_score", lambda: 12)
    monkeypatch.setattr(
        menus,
        "_assign_stats_from_pool",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )

    menus._select_stats_random_normal(ru_strings, "human", None)
    output = capsys.readouterr().out

    assert "Принять броски" in output
    assert "Перегенерировать" in output
    assert "[Enter]" not in output


def test_random_normal_regenerate_rerolls(monkeypatch, ru_strings):
    """Random Normal: «Перегенерировать» запускает новый бросок."""
    from ui import menus

    roll_values = iter([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
    choices = iter([2, 0])

    monkeypatch.setattr(menus, "roll_ability_score", lambda: next(roll_values))
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: next(choices),
    )

    result = menus._select_stats_random_normal(ru_strings, "human", None)

    assert result is None


def test_confirm_stats_reroll_label_redistribute(
    monkeypatch, capsys, ru_strings
):
    """Point buy / standard array: пункт 2 — «Перераспределить»."""
    from core.character import STAT_NAMES
    from ui import menus

    stats = {stat: 10 for stat in STAT_NAMES}
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )
    monkeypatch.setattr(
        menus, "get_race_bonuses", lambda race_id, subrace_id=None: {}
    )

    result = menus._confirm_stats(
        ru_strings,
        stats,
        "human",
        None,
        reroll_label_key="character.stats_reroll_redistribute",
    )
    output = capsys.readouterr().out

    assert result == "back"
    assert "Перераспределить" in output
    assert "Перегенерировать" not in output


def test_confirm_stats_reroll_label_regenerate(
    monkeypatch, capsys, ru_strings
):
    """Случайный метод: пункт 2 — «Перегенерировать»."""
    from core.character import STAT_NAMES
    from ui import menus

    stats = {stat: 10 for stat in STAT_NAMES}
    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 0,
    )
    monkeypatch.setattr(
        menus, "get_race_bonuses", lambda race_id, subrace_id=None: {}
    )

    menus._confirm_stats(
        ru_strings,
        stats,
        "human",
        None,
        reroll_label_key="character.stats_reroll_regenerate",
    )
    output = capsys.readouterr().out

    assert "Перегенерировать" in output
    assert "Перераспределить" not in output


def test_print_final_stat_line_shows_bonus(capsys, ru_strings):
    """Итоговая характеристика показывает расовый бонус как (+N)."""
    from ui import menus

    menus._print_final_stat_line(ru_strings, "strength", 17, {"strength": 2})
    output = capsys.readouterr().out

    assert "Сила:" in output
    assert "17" in output
    assert "(+2)" in output


def test_print_final_stat_line_no_bonus(capsys, ru_strings):
    """Без расового бонуса суффикс (+N) не показывается."""
    from ui import menus

    menus._print_final_stat_line(ru_strings, "dexterity", 14, {"strength": 2})
    output = capsys.readouterr().out

    assert "14" in output
    assert "(+" not in output


def test_show_stats_generation_flow_loops_on_method_back(
    monkeypatch, ru_strings
):
    """При «Назад» с подтверждения flow возвращается к меню методов."""
    from core.character import STAT_NAMES
    from ui import menus

    calls = {"standard": 0}
    final_stats = dict.fromkeys(STAT_NAMES, 10)

    def fake_standard_array(strings, race_id, subrace_id):
        calls["standard"] += 1
        if calls["standard"] == 1:
            return None
        return final_stats

    monkeypatch.setattr(
        menus,
        "get_int_input",
        lambda prompt, min_v, max_v, strings=None: 1,
    )
    monkeypatch.setattr(
        menus, "_select_stats_standard_array", fake_standard_array
    )

    result = menus.show_stats_generation_flow(
        ru_strings, "human", None, "normal"
    )

    assert calls["standard"] == 2
    assert result == final_stats
