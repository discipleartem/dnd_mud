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


def test_print_race_info_shows_grants(capsys, ru_strings):
    """Экран подрасы выводит особенности из grants[]."""
    from ui.menus._display._race import _print_race_info

    high_elf = {
        "name": "Высший эльф",
        "description": "Описание",
        "grants": [
            {
                "type": "weapon_proficiency",
                "name": "Эльфийская боевая подготовка",
                "weapons": ["longsword", "longbow"],
            },
            {
                "type": "language",
                "name": "Дополнительный язык",
                "choice": True,
                "count": 1,
                "pool": "common",
            },
        ],
    }
    _print_race_info(high_elf, ru_strings, "ru")
    output = capsys.readouterr().out
    assert "Эльфийская боевая подготовка" in output
    assert "Дополнительный язык" in output
    assert "обычные языки" in output
    assert "Длинный меч" in output
    assert "longsword" not in output


def test_print_variant_human_grants_localized(capsys, ru_strings):
    """Вариант человека: типы grant и пул all — на русском."""
    from ui.menus._display._race import _print_race_info

    variant = {
        "name": "Человек (вариант)",
        "description": "Описание",
        "grants": [
            {
                "type": "ability_increase",
                "count": 2,
                "amount": 1,
                "choice": True,
            },
            {
                "type": "skill_proficiency",
                "count": 1,
                "choice": True,
                "from": "all",
            },
            {
                "type": "feat",
                "count": 1,
                "choice": True,
                "from": "all",
            },
        ],
    }
    _print_race_info(variant, ru_strings, "ru")
    output = capsys.readouterr().out
    assert "ability_increase" not in output
    assert "skill_proficiency" not in output
    assert "Увеличение характеристик" in output
    assert "Владение навыком" in output
    assert "Черта" in output
    assert "все навыки" in output
    assert "все черты" in output
    assert " из all" not in output


def test_print_dwarf_subrace_grant_descriptions(capsys, ru_strings):
    """Подрасы дварфа: описания особенностей из структуры grants[]."""
    from core.races import load_race_full
    from ui.menus._display._race import _print_race_info

    dwarf = load_race_full("dwarf", "ru")
    hill = dwarf["subraces"]["hill_dwarf"]
    _print_race_info(hill, ru_strings, "ru")
    hill_out = capsys.readouterr().out
    assert "Дварфская выдержка" in hill_out
    assert "HP за уровень" in hill_out

    mountain = dwarf["subraces"]["mountain_dwarf"]
    _print_race_info(mountain, ru_strings, "ru")
    mountain_out = capsys.readouterr().out
    assert "Владение доспехами дварфов" in mountain_out
    assert "лёгкие доспехи" in mountain_out
    assert "средние доспехи" in mountain_out


def test_print_background_info_shows_proficiencies(capsys, ru_strings):
    """Предыстория: владения, снаряжение и описание умения."""
    from core.backgrounds import load_background_full
    from ui.menus._display._background import _print_background_info

    acolyte = load_background_full("acolyte", "ru")
    _print_background_info(acolyte, ru_strings, "ru")
    out = capsys.readouterr().out
    assert "Проницательность" in out or "проницательность" in out.lower()
    assert "обычные языки" in out
    assert "священный символ" in out
    assert "Приют для верующих" in out
    assert "храмах" in out

    soldier = load_background_full("soldier", "ru")
    _print_background_info(soldier, ru_strings, "ru")
    soldier_out = capsys.readouterr().out
    assert "игровые наборы" in soldier_out
    assert "Воинское звание" in soldier_out
