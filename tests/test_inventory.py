"""Тесты инвентаря и экипировки."""

import pytest

from core.inventory import (
    add_items_to_inventory,
    compute_ac,
    default_equipped,
    equip_defaults,
    expand_pack_contents,
    format_inventory_line,
    inventory_excluding_equipped,
)
from core.models import Character

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_expand_explorers_pack() -> None:
    contents = expand_pack_contents("explorers_pack")
    assert contents
    assert any(item["id"] == "backpack" for item in contents)


def test_compute_ac_with_chain_mail() -> None:
    char = Character(
        name="Test",
        race="human",
        class_id="fighter",
        stats={"dexterity": 14},
        equipped={"armor": "chain_mail", "shield": True},
        inventory=[
            {"kind": "armor", "id": "chain_mail", "qty": 1},
            {"kind": "armor", "id": "shield", "qty": 1},
        ],
    )
    assert compute_ac(char) == 18


def test_equip_defaults_picks_armor_and_weapons() -> None:
    char = Character(
        name="Test",
        race="human",
        class_id="fighter",
        weapon_proficiencies=["simple", "martial", "longsword", "dagger"],
        armor_proficiencies=["light", "medium", "heavy", "shield"],
        inventory=[
            {"kind": "armor", "id": "leather", "qty": 1},
            {"kind": "armor", "id": "chain_mail", "qty": 1},
            {"kind": "armor", "id": "shield", "qty": 1},
            {"kind": "weapon", "id": "longsword", "qty": 1},
            {"kind": "weapon", "id": "dagger", "qty": 1},
        ],
    )
    equipped = equip_defaults(char)
    assert equipped["armor"] == "chain_mail"
    assert equipped["shield"] is True
    assert equipped["main_hand"] == "longsword"
    assert equipped["off_hand"] is None


def test_equip_defaults_rogue_rapier_and_dagger() -> None:
    char = Character(
        name="Rogue",
        race="human",
        class_id="rogue",
        weapon_proficiencies=[
            "simple",
            "martial",
            "rapier",
            "shortsword",
            "shortbow",
            "dagger",
        ],
        armor_proficiencies=["light"],
        inventory=[
            {"kind": "armor", "id": "leather", "qty": 1},
            {"kind": "weapon", "id": "rapier", "qty": 1},
            {"kind": "weapon", "id": "dagger", "qty": 1},
            {"kind": "weapon", "id": "shortbow", "qty": 1},
        ],
    )
    equipped = equip_defaults(char)
    assert equipped["main_hand"] == "rapier"
    assert equipped["off_hand"] == "dagger"
    assert equipped["shield"] is False


def test_equip_defaults_two_handed_blocks_shield_and_off_hand() -> None:
    char = Character(
        name="Barb",
        race="human",
        class_id="fighter",
        weapon_proficiencies=["simple", "martial", "greataxe", "handaxe"],
        armor_proficiencies=["shield"],
        inventory=[
            {"kind": "armor", "id": "shield", "qty": 1},
            {"kind": "weapon", "id": "greataxe", "qty": 1},
            {"kind": "weapon", "id": "handaxe", "qty": 1},
        ],
    )
    equipped = equip_defaults(char)
    assert equipped["main_hand"] == "greataxe"
    assert equipped["shield"] is False
    assert equipped["off_hand"] is None


def test_equip_defaults_caster_no_off_hand_weapon() -> None:
    char = Character(
        name="Cleric",
        race="human",
        class_id="cleric",
        weapon_proficiencies=["simple", "mace", "dagger"],
        armor_proficiencies=["light", "medium", "heavy", "shield"],
        inventory=[
            {"kind": "armor", "id": "scale_mail", "qty": 1},
            {"kind": "armor", "id": "shield", "qty": 1},
            {"kind": "weapon", "id": "mace", "qty": 1},
            {"kind": "weapon", "id": "dagger", "qty": 1},
        ],
    )
    equipped = equip_defaults(char)
    assert equipped["main_hand"] == "mace"
    assert equipped["shield"] is True
    assert equipped["off_hand"] is None


def test_equip_defaults_no_shield_dual_wield_light() -> None:
    char = Character(
        name="Fighter",
        race="human",
        class_id="fighter",
        weapon_proficiencies=["simple", "martial", "longsword", "handaxe"],
        inventory=[
            {"kind": "weapon", "id": "longsword", "qty": 1},
            {"kind": "weapon", "id": "handaxe", "qty": 1},
        ],
    )
    equipped = equip_defaults(char)
    assert equipped["main_hand"] == "longsword"
    assert equipped["off_hand"] == "handaxe"
    assert equipped["shield"] is False


def test_add_items_merges_quantities() -> None:
    merged = add_items_to_inventory(
        [],
        [
            {"kind": "weapon", "id": "dagger", "qty": 1},
            {"kind": "weapon", "id": "dagger", "qty": 1},
        ],
    )
    assert merged == [{"kind": "weapon", "id": "dagger", "qty": 2}]


def test_default_equipped_empty() -> None:
    assert default_equipped()["armor"] is None


def test_inventory_excluding_equipped_hides_worn_only_in_display() -> None:
    inventory = [
        {"kind": "armor", "id": "leather", "qty": 1},
        {"kind": "weapon", "id": "rapier", "qty": 1},
        {"kind": "weapon", "id": "dagger", "qty": 2},
    ]
    equipped = {
        "armor": "leather",
        "shield": False,
        "main_hand": "rapier",
        "off_hand": "dagger",
    }
    visible = inventory_excluding_equipped(inventory, equipped)
    assert visible == [{"kind": "weapon", "id": "dagger", "qty": 1}]
    assert inventory[0]["qty"] == 1


def test_format_inventory_line_omits_equipped() -> None:
    inventory = [
        {"kind": "armor", "id": "leather", "qty": 1},
        {"kind": "weapon", "id": "rapier", "qty": 1},
        {"kind": "tool", "id": "lute", "qty": 1},
    ]
    equipped = {"armor": "leather", "main_hand": "rapier", "shield": False}
    line = format_inventory_line(inventory, "ru", equipped=equipped)
    assert "Кожаный доспех" not in line
    assert "Рапира" not in line
    assert "Лютня" in line
