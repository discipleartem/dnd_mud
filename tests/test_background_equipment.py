"""Тесты стартового снаряжения предыстории."""

from pathlib import Path

import pytest

from core.backgrounds import get_background_equipment_items
from core.character_storage import save_character

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")

STAT_NAMES = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]


def test_get_background_equipment_items_yaml_and_picked_tools_only() -> None:
    items = get_background_equipment_items(
        "criminal",
        background_tool_picks=["dice_set"],
    )
    ids = {(i["kind"], i["id"]) for i in items}
    assert ("equipment", "crowbar") in ids
    assert ("equipment", "common_clothes") in ids
    assert ("tool", "thieves_tools") in ids
    assert ("tool", "dice_set") in ids


def test_get_background_equipment_items_ignores_tool_proficiencies() -> None:
    """Владение инструментом класса не добавляет предмет предыстории."""
    items = get_background_equipment_items(
        "entertainer",
        background_tool_picks=["lute"],
    )
    ids = {(i["kind"], i["id"]) for i in items}
    assert ("tool", "lute") in ids
    assert ("tool", "lyre") not in ids
    assert ("tool", "disguise_kit") not in ids


def test_get_background_equipment_items_acolyte_phb_gear() -> None:
    items = get_background_equipment_items("acolyte")
    ids = {(i["kind"], i["id"]) for i in items}
    assert ("equipment", "emblem") in ids
    assert ("equipment", "book") in ids
    assert ("equipment", "incense") in ids
    assert ("equipment", "vestments") in ids
    assert ("equipment", "common_clothes") in ids


def test_save_character_merges_background_items_into_inventory(
    characters_dir: Path,
) -> None:
    stats = dict.fromkeys(STAT_NAMES, 12)
    saved = save_character(
        name="BgHero",
        race_id="human",
        class_id="rogue",
        difficulty="normal",
        stats=stats,
        background_id="criminal",
        tool_proficiencies=["thieves_tools", "dice_set", "lute", "lyre"],
        background_tool_picks=["dice_set"],
        equipment_choices={
            "melee": "rapier",
            "ranged": "shortbow",
            "pack": "burglars_pack",
        },
    )
    inv_ids = {(i["kind"], i["id"]) for i in saved.inventory}
    assert ("equipment", "crowbar") in inv_ids
    assert ("tool", "thieves_tools") in inv_ids
    assert ("tool", "dice_set") in inv_ids
    assert ("tool", "lute") not in inv_ids
    assert ("tool", "lyre") not in inv_ids
    assert ("weapon", "rapier") in inv_ids


def test_save_character_charlatan_tools_in_inventory(
    characters_dir: Path,
) -> None:
    stats = dict.fromkeys(STAT_NAMES, 10)
    saved = save_character(
        name="Charlatan",
        race_id="human",
        class_id="rogue",
        stats=stats,
        background_id="charlatan",
        equipment_choices={
            "melee": "rapier",
            "ranged": "shortbow",
            "pack": "burglars_pack",
        },
    )
    inv_ids = {(i["kind"], i["id"]) for i in saved.inventory}
    assert ("equipment", "fine_clothes") in inv_ids
    assert ("tool", "disguise_kit") in inv_ids
    assert ("tool", "forgery_kit") in inv_ids
