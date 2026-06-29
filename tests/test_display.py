"""Тесты форматирования карточек персонажа (_display)."""

from core.models import Character
from ui.menus._display._character import _print_character_card
from ui.menus._display._stats import _format_character_stats_compact


def test_format_character_stats_compact(ru_strings):
    """Компактная строка характеристик содержит аббревиатуры и значения."""
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        stats={
            "strength": 16,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 8,
        },
    )
    compact = _format_character_stats_compact(char, ru_strings)
    assert "16" in compact
    assert "14" in compact
    assert "Сил" in compact or "Str" in compact


def test_print_character_card_shows_name_and_class(capsys, ru_strings):
    """Карточка персонажа выводит имя и класс."""
    char = Character(
        name="Арагорн",
        race="human",
        class_id="fighter",
        level=3,
        subclass_id="champion",
        current_hp=28,
        max_hp=28,
        stats={"strength": 16, "dexterity": 14, "constitution": 14},
    )
    _print_character_card(1, char, ru_strings, "ru")
    output = capsys.readouterr().out
    assert "Арагорн" in output
    assert "Воин" in output
    assert "3" in output
