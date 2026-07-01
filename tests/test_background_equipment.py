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


def test_get_background_equipment_items_criminal_phb_gear() -> None:
    items = get_background_equipment_items(
        "criminal",
        background_tool_picks=["dice_set"],
    )
    ids = {(i["kind"], i["id"]) for i in items}
    assert ids == {
        ("equipment", "crowbar"),
        ("equipment", "dark_common_clothes"),
    }


def test_get_background_equipment_items_entertainer_instrument_from_pick() -> (
    None
):
    items = get_background_equipment_items(
        "entertainer",
        background_tool_picks=["lute"],
    )
    ids = {(i["kind"], i["id"]) for i in items}
    assert ("tool", "lute") in ids
    assert ("tool", "disguise_kit") not in ids
    assert ("equipment", "trinket") in ids
    assert ("equipment", "costume") in ids


def test_background_inventory_ignores_proficiency_only_picks() -> None:
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


def test_get_background_equipment_items_soldier_dice_or_cards_only() -> None:
    dice = get_background_equipment_items(
        "soldier",
        background_tool_picks=["dice_set"],
    )
    cards = get_background_equipment_items(
        "soldier",
        background_tool_picks=["playing_cards"],
    )
    none = get_background_equipment_items(
        "soldier",
        background_tool_picks=["three_dragon_ante"],
    )
    for items in (dice, cards):
        ids = {(i["kind"], i["id"]) for i in items}
        assert ("equipment", "emblem") in ids
        assert ("equipment", "trophy") in ids
        assert ("equipment", "common_clothes") in ids
        assert sum(1 for kind, _ in ids if kind == "tool") == 1
    assert ("tool", "dice_set") in {(i["kind"], i["id"]) for i in dice}
    assert ("tool", "playing_cards") in {(i["kind"], i["id"]) for i in cards}
    assert not any(item["kind"] == "tool" for item in none)


def test_get_background_equipment_items_noble_gaming_prof_not_inventory() -> (
    None
):
    items = get_background_equipment_items(
        "noble",
        background_tool_picks=["three_dragon_ante"],
    )
    ids = {(i["kind"], i["id"]) for i in items}
    assert ("tool", "three_dragon_ante") not in ids
    assert ("equipment", "fine_clothes") in ids


def test_get_background_equipment_items_folk_hero_artisan_tools() -> None:
    items = get_background_equipment_items(
        "folk_hero",
        background_tool_picks=["smith_tools"],
    )
    ids = {(i["kind"], i["id"]) for i in items}
    assert ("tool", "smith_tools") in ids
    assert ("equipment", "shovel") in ids
    assert ("equipment", "iron_pot") in ids


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
    assert ("equipment", "dark_common_clothes") in inv_ids
    assert ("tool", "dice_set") not in inv_ids
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
    assert ("tool", "forgery_kit") not in inv_ids
