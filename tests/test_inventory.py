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
        stats={"strength": 14, "dexterity": 10},
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


def test_equip_defaults_skips_armor_below_strength() -> None:
    char = Character(
        name="Cleric",
        race="dwarf",
        class_id="cleric",
        stats={"strength": 9, "dexterity": 13},
        armor_proficiencies=["light", "medium", "heavy", "shield"],
        inventory=[
            {"kind": "armor", "id": "chain_mail", "qty": 1},
            {"kind": "armor", "id": "scale_mail", "qty": 1},
        ],
    )
    equipped = equip_defaults(char)
    assert equipped["armor"] == "scale_mail"


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
    assert equipped["main_hand_grip"] == "two_handed"
    assert equipped["off_hand"] is None
    assert equipped["shield"] is False


def test_equip_defaults_versatile_one_handed_with_shield() -> None:
    char = Character(
        name="Cleric",
        race="dwarf",
        class_id="cleric",
        weapon_proficiencies=[
            "simple",
            "warhammer",
            "battleaxe",
            "handaxe",
            "light_hammer",
        ],
        armor_proficiencies=["light", "medium", "heavy", "shield"],
        inventory=[
            {"kind": "armor", "id": "chain_mail", "qty": 1},
            {"kind": "armor", "id": "shield", "qty": 1},
            {"kind": "weapon", "id": "warhammer", "qty": 1},
        ],
    )
    equipped = equip_defaults(char)
    assert equipped["main_hand"] == "warhammer"
    assert equipped["main_hand_grip"] == "one_handed"
    assert equipped["shield"] is True
    assert equipped["off_hand"] is None


def test_equip_defaults_versatile_two_handed_without_shield() -> None:
    char = Character(
        name="Fighter",
        race="dwarf",
        class_id="fighter",
        weapon_proficiencies=["simple", "martial", "warhammer"],
        inventory=[{"kind": "weapon", "id": "warhammer", "qty": 1}],
    )
    equipped = equip_defaults(char)
    assert equipped["main_hand"] == "warhammer"
    assert equipped["main_hand_grip"] == "two_handed"
    assert equipped["off_hand"] is None


def test_get_equipped_display_hands_and_occupied() -> None:
    from core.inventory import get_equipped_display

    char = Character(
        name="Test",
        race="human",
        class_id="fighter",
        equipped={
            "main_hand": "greataxe",
            "shield": False,
        },
    )
    labels, muted = get_equipped_display(char, "ru")
    assert labels["main_hand"] == "Секира"
    assert labels["off_hand"] == "двуручное"
    assert muted is True

    versatile = Character(
        name="Fighter",
        race="dwarf",
        class_id="fighter",
        equipped={
            "main_hand": "warhammer",
            "main_hand_grip": "two_handed",
            "shield": False,
        },
    )
    vers_labels, vers_muted = get_equipped_display(versatile, "ru")
    assert vers_labels["main_hand_hint"] == "две руки"
    assert vers_labels["damage_one_dice"] == "1к8"
    assert vers_labels["damage_two_dice"] == "1к10"
    assert vers_labels["damage_active"] == "two"
    assert vers_labels["off_hand"] == "универсальное"
    assert vers_muted is True

    cleric = Character(
        name="Cleric",
        race="dwarf",
        class_id="cleric",
        equipped={
            "armor": "chain_mail",
            "shield": True,
            "main_hand": "warhammer",
            "main_hand_grip": "one_handed",
        },
    )
    cleric_labels, cleric_muted = get_equipped_display(cleric, "ru")
    assert cleric_labels["armor"] == "Кольчуга"
    assert cleric_labels["armor_hint"] == (
        "тяжёлый, КД 16, Сил 13, помеха скрытности"
    )
    assert cleric_labels["main_hand"] == "Боевой молот"
    assert cleric_labels["main_hand_hint"] == "одна рука"
    assert cleric_labels["damage_one_dice"] == "1к8"
    assert cleric_labels["damage_two_dice"] == "1к10"
    assert cleric_labels["damage_active"] == "one"
    assert cleric_labels["off_hand"] == "Щит"
    assert cleric_muted is False
    assert "shield" not in cleric_labels

    crossbow_char = Character(
        name="Cleric",
        race="human",
        class_id="cleric",
        equipped={
            "main_hand": "light_crossbow",
            "main_hand_grip": "two_handed",
            "shield": False,
        },
        inventory=[
            {"kind": "equipment", "id": "crossbow_bolts", "qty": 20},
        ],
    )
    cb_labels, cb_muted = get_equipped_display(crossbow_char, "ru")
    assert cb_labels["main_hand"] == "Арбалет лёгкий"
    assert cb_labels["main_hand_hint"] == "двуручное, перезарядка"
    assert cb_labels["ammunition"] == "тип: Арбалетные болты, количество: 20"
    assert cb_labels["distance"] == "оптимальная 80, допустимая: 320"
    assert cb_muted is True


def test_get_equipped_display_empty_armor_slot() -> None:
    from core.inventory import get_equipped_display

    char = Character(
        name="Cleric",
        race="dwarf",
        class_id="cleric",
        equipped={
            "main_hand": "warhammer",
            "main_hand_grip": "one_handed",
            "shield": True,
        },
    )
    labels, muted = get_equipped_display(char, "ru")
    assert labels["armor"] == "пусто"
    assert labels["main_hand"] == "Боевой молот"
    assert labels["off_hand"] == "Щит"
    assert muted is False


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
