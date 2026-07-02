"""Тесты снаряжения и форматирования карточек (_display)."""

from typing import Any

import pytest
from colorama import Fore

from core.equipment import (
    load_armor,
    load_tool,
    load_weapon,
    proficiency_token_label,
    resolve_tool_pool,
    tools_by_category,
    weapon_matches_category,
)
from core.localization import load_strings
from core.models import Character
from ui.menus._common import _sort_ids_by_proficiency
from ui.menus._display._character import (
    _format_character_feats,
    _print_character_card,
)
from ui.menus._display._stats import (
    _format_ability_modifier,
    _format_character_stats_compact,
)


def test_sort_ids_by_proficiency() -> None:
    def has_prof(profs: list[str], item_id: str) -> bool:
        return item_id in profs

    def name_key(item_id: str) -> str:
        return item_id

    items = ["viola", "lute", "flute", "drum"]
    profs = ["lute", "flute"]
    sorted_items = _sort_ids_by_proficiency(
        items, profs, has_prof, name_key=name_key
    )
    assert sorted_items[:2] == ["flute", "lute"]
    assert sorted_items[2:] == ["drum", "viola"]


def test_option_display_label_strips_proficiency_hint() -> None:
    from core.localization import load_strings
    from core.starting_equipment import format_equipment_option_label

    ru_strings = load_strings("ru")
    option = {
        "label": {
            "ru": "б) Боевой молот (если владеете)",
            "en": "b) Warhammer (if proficient)",
        },
        "requires_weapon_pool": "martial",
    }
    assert format_equipment_option_label(option, ru_strings, "ru") == (
        "б) Боевой молот (воинское оружие)"
    )
    en_strings = load_strings("en")
    assert format_equipment_option_label(option, en_strings, "en") == (
        "b) Warhammer (martial weapons)"
    )


def test_armor_menu_shows_unavailable_chain_mail(
    ru_strings: dict[str, Any],
) -> None:
    from io import StringIO
    from unittest.mock import patch

    from core.starting_equipment import list_equipment_options_by_group
    from ui.menus.equipment import _pick_option_for_group

    groups = list_equipment_options_by_group("cleric")
    with (
        patch("ui.menus._deps.get_int_input", return_value=0),
        patch("sys.stdout", new_callable=StringIO) as buf,
    ):
        _pick_option_for_group(
            ru_strings,
            "armor",
            groups["armor"],
            ["simple"],
            ["light", "medium", "shield", "heavy"],
            [],
            "ru",
            9,
        )
        output = buf.getvalue()
    assert "Кольчуга (тяжёлые доспехи)" in output
    assert "(Сил 13)" in output
    assert Fore.RED in output or "\x1b[31m" in output
    assert output.count("Чешуйчатый") == 1
    assert output.count("Кожаный") == 1


def test_weapon_menu_warhammer_available_for_dwarf_weapon_proficiency(
    ru_strings: dict[str, Any],
) -> None:
    from io import StringIO
    from unittest.mock import patch

    from core.starting_equipment import list_equipment_options_by_group
    from ui.menus.equipment import _pick_option_for_group

    groups = list_equipment_options_by_group("cleric")
    dwarf_weapons = [
        "simple",
        "battleaxe",
        "handaxe",
        "light_hammer",
        "warhammer",
    ]
    with (
        patch("ui.menus._deps.get_int_input", return_value=0),
        patch("sys.stdout", new_callable=StringIO) as buf,
    ):
        _pick_option_for_group(
            ru_strings,
            "weapon",
            groups["weapon"],
            dwarf_weapons,
            ["light", "medium", "shield"],
            [],
            "ru",
            10,
        )
        output = buf.getvalue()
    assert "а) Булава" in output
    assert "\x1b[36mб) Боевой молот (воинское оружие)\x1b[0m" in output


def test_weapon_menu_shows_unavailable_warhammer_without_proficiency(
    ru_strings: dict[str, Any],
) -> None:
    from io import StringIO
    from unittest.mock import patch

    from core.starting_equipment import list_equipment_options_by_group
    from ui.menus.equipment import _pick_option_for_group

    groups = list_equipment_options_by_group("cleric")
    with (
        patch("ui.menus._deps.get_int_input", return_value=0),
        patch("sys.stdout", new_callable=StringIO) as buf,
    ):
        _pick_option_for_group(
            ru_strings,
            "weapon",
            groups["weapon"],
            ["simple"],
            ["light", "medium", "shield"],
            [],
            "ru",
            10,
        )
        output = buf.getvalue()
    assert "а) Булава" in output
    assert "б) Боевой молот (воинское оружие)" in output
    assert "2. б) Боевой молот" not in output
    assert Fore.LIGHTBLACK_EX in output or "\x1b[90m" in output


def test_weapon_and_tool_catalog() -> None:
    from core.equipment import (
        armor_equipped_hint,
        format_versatile_catalog_hint,
        format_weapon_property_labels,
        get_equipment_item_name,
        weapon_ammunition_item_id,
        weapon_property_hint,
        weapon_range,
    )

    ru_strings = load_strings("ru")
    assert armor_equipped_hint("leather", ru_strings) == "лёгкий, КД 11 + Лов"
    assert armor_equipped_hint("breastplate", ru_strings) == (
        "средний, КД 14 + Лов, макс. 2"
    )
    assert armor_equipped_hint("chain_mail", ru_strings) == (
        "тяжёлый, КД 16, Сил 13, помеха скрытности"
    )
    assert armor_equipped_hint("padded", ru_strings) == (
        "лёгкий, КД 11 + Лов, помеха скрытности"
    )
    assert format_weapon_property_labels("warhammer", ru_strings) == []
    assert format_versatile_catalog_hint("warhammer", ru_strings) == (
        "универсальное: 1к8 / 1к10"
    )
    assert "фехтовальное" in weapon_property_hint("dagger", ru_strings)
    assert "метательное" not in weapon_property_hint("dagger", ru_strings)
    assert format_weapon_property_labels("mace", ru_strings) == []
    assert format_weapon_property_labels("light_crossbow", ru_strings) == [
        "двуручное",
        "перезарядка",
    ]
    assert weapon_range("light_crossbow") == {"normal": 80, "long": 320}
    assert weapon_range("dagger") == {"normal": 20, "long": 60}
    assert weapon_ammunition_item_id("light_crossbow") == "crossbow_bolts"
    assert get_equipment_item_name("crossbow_case", "ru") == "Сумка для болтов"

    assert load_weapon("longsword").get("category") == "martial_melee"
    assert weapon_matches_category("simple", "club")
    assert not weapon_matches_category("martial", "club")
    assert load_armor("shield").get("category") == "shield"
    assert load_tool("thieves_tools").get("name")
    pool = tools_by_category("musical_instruments")
    assert "lute" in pool or len(pool) > 0
    assert "land_vehicles" in resolve_tool_pool("land_vehicles")
    assert resolve_tool_pool("soldier_gaming") == ["dice_set", "playing_cards"]


def test_proficiency_token_label() -> None:
    ru = load_strings("ru")
    assert proficiency_token_label("longbow", ru, "ru") == "длинные луки"
    en = load_strings("en")
    assert proficiency_token_label("smith_tools", en, "en") == "Smith's tools"


def test_format_ability_modifier() -> None:
    assert _format_ability_modifier(3) == "(+3)"
    assert _format_ability_modifier(-2) == "(-2)"
    assert _format_ability_modifier(0) == ""


def test_format_character_stats_compact_hides_zero_mod(
    ru_strings: dict[str, Any],
) -> None:
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        stats={
            "strength": 6,
            "dexterity": 10,
            "constitution": 12,
            "intelligence": 14,
            "wisdom": 14,
            "charisma": 17,
        },
    )
    compact = _format_character_stats_compact(char, ru_strings)
    assert "(+0)" not in compact
    assert "10" in compact
    assert "(+1)" in compact
    assert "(-2)" in compact


def test_format_character_feats() -> None:
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        feat_ids=["tough", "athlete"],
    )
    assert _format_character_feats(char, "ru") == "Крепкий, Атлетичный"


def test_format_character_stats_and_card(
    capsys: pytest.CaptureFixture[str], ru_strings: dict[str, Any]
) -> None:
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
    compact = _format_character_stats_compact(char, ru_strings)
    assert "16" in compact
    assert "(+3)" in compact
    assert "(+2)" in compact
    char.save_proficiencies = ["strength", "constitution"]
    char.feat_ids = ["tough", "athlete"]
    _print_character_card(1, char, ru_strings, "ru")
    output = capsys.readouterr().out
    assert "Арагорн" in output
    assert "Воин" in output
    assert "Черты:" in output
    assert "Крепкий, Атлетичный" in output
    assert "Сила" in output or "сила" in output.lower()
    assert "Телосложение" in output or "телосложение" in output.lower()
    assert "+5" not in output.split("спасброски")[-1].split("\n")[0]


def test_print_race_info_grants(
    capsys: pytest.CaptureFixture[str], ru_strings: dict[str, Any]
) -> None:
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
    assert "Длинный меч" in output
