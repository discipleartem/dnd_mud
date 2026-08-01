"""Тесты текстового форматирования grants в UI."""

import pytest

from ui.menus.display.grants_text import (
    _grant_description,
    _grant_display_name,
)

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_grant_equipment_item_and_musical_pool_labels() -> None:
    """Локализация equipment_item и пула musical_instruments."""
    from core.platform.localization import load_strings

    ru = load_strings("ru")
    equipment_grant = {
        "type": "equipment_item",
        "items": [
            {"kind": "equipment", "id": "emblem", "qty": 1},
            {"kind": "equipment", "id": "incense", "qty": 5},
        ],
    }
    assert _grant_display_name(equipment_grant, ru) == "Снаряжение"
    assert _grant_description(equipment_grant, ru, "ru") == (
        "Эмблема, Палочка благовоний ×5"
    )
    tool_choice = {
        "type": "tool_proficiency",
        "choice": True,
        "count": 1,
        "pool": "musical_instruments",
    }
    assert _grant_description(tool_choice, ru, "ru") == (
        "выбор: 1 из музыкальные инструменты"
    )
