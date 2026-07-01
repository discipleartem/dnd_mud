"""Тесты снаряжения и форматирования карточек (_display)."""

from typing import Any

import pytest

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
from ui.menus._display._character import _print_character_card
from ui.menus._display._stats import _format_character_stats_compact

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_weapon_and_tool_catalog() -> None:
    assert load_weapon("longsword").get("category") == "martial_melee"
    assert weapon_matches_category("simple", "club")
    assert not weapon_matches_category("martial", "club")
    assert load_armor("shield").get("category") == "shield"
    assert load_tool("thieves_tools").get("name")
    pool = tools_by_category("musical_instruments")
    assert "lute" in pool or len(pool) > 0
    assert "land_vehicles" in resolve_tool_pool("land_vehicles")


def test_proficiency_token_label() -> None:
    ru = load_strings("ru")
    assert proficiency_token_label("longbow", ru, "ru") == "длинные луки"
    en = load_strings("en")
    assert proficiency_token_label("smith_tools", en, "en") == "Smith's tools"


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
    _print_character_card(1, char, ru_strings, "ru")
    output = capsys.readouterr().out
    assert "Арагорн" in output
    assert "Воин" in output


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
