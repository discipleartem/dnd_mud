"""Тесты стартового снаряжения класса."""

from typing import Any

import pytest

from core.starting_equipment import (
    all_weapons_in_pool,
    equipment_option_available,
    format_equipment_option_label,
    get_class_starting_equipment_config,
    list_equipment_options_by_group,
    resolve_starting_items,
    summarize_class_starting_equipment,
    weapons_for_pool,
)

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_fighter_starting_equipment_config() -> None:
    config = get_class_starting_equipment_config("fighter")
    assert config.get("choices")
    assert isinstance(config.get("fixed"), list)


def test_all_weapons_in_pool_includes_non_proficient() -> None:
    all_simple = all_weapons_in_pool("simple")
    proficient = weapons_for_pool("simple", ["club"])
    assert "club" in all_simple
    assert len(all_simple) > len(proficient)


def test_format_equipment_option_label_armor_hints(
    ru_strings: dict[str, Any],
) -> None:
    groups = list_equipment_options_by_group("cleric")
    armor_opts = {opt["id"]: opt for opt in groups["armor"]}
    assert (
        format_equipment_option_label(
            armor_opts["scale_mail"], ru_strings, "ru"
        )
        == "а) Чешуйчатый доспех (средние доспехи)"
    )
    assert (
        format_equipment_option_label(armor_opts["leather"], ru_strings, "ru")
        == "б) Кожаный доспех (лёгкие доспехи)"
    )
    assert (
        format_equipment_option_label(
            armor_opts["chain_mail"], ru_strings, "ru"
        )
        == "в) Кольчуга (тяжёлые доспехи)"
    )

    weapon_opts = {opt["id"]: opt for opt in groups["weapon"]}
    assert (
        format_equipment_option_label(
            weapon_opts["warhammer"], ru_strings, "ru"
        )
        == "б) Боевой молот (воинское оружие)"
    )


def test_summarize_cleric_starting_equipment_sections(
    ru_strings: dict[str, Any],
) -> None:
    sections = summarize_class_starting_equipment("cleric", ru_strings, "ru")
    assert "Щит" in sections["armor"]
    assert any("Кольчуга" in line for line in sections["armor"])
    assert any("Булава" in line for line in sections["weapon"])
    assert "Эмблема" in sections["gear"]
    assert "tool" not in sections


def test_cleric_equipment_option_availability() -> None:
    groups = list_equipment_options_by_group("cleric")
    weapon_opts = {opt["id"]: opt for opt in groups["weapon"]}
    simple_only = ["simple"]
    light_medium = ["light", "medium"]

    assert equipment_option_available(weapon_opts["mace"], simple_only, [])
    assert not equipment_option_available(
        weapon_opts["warhammer"], simple_only, []
    )
    assert equipment_option_available(
        weapon_opts["warhammer"], simple_only + ["martial"], []
    )

    armor_opts = {opt["id"]: opt for opt in groups["armor"]}
    assert equipment_option_available(armor_opts["leather"], [], light_medium)
    assert equipment_option_available(
        armor_opts["scale_mail"], [], light_medium
    )
    assert not equipment_option_available(
        armor_opts["chain_mail"], [], light_medium
    )
    assert equipment_option_available(
        armor_opts["chain_mail"], [], light_medium + ["heavy"]
    )


def test_resolve_fighter_starting_items() -> None:
    choices = {
        "armor": "chain_mail",
        "weapon_primary": "martial_shield",
        "weapon_primary_weapon_0": "longsword",
        "ranged_or_axes": "handaxes",
        "pack": "explorers_pack",
    }
    profs = ["simple", "martial", "light", "medium", "heavy", "shield"]
    items = resolve_starting_items("fighter", choices, profs, profs)
    ids = {(i["kind"], i["id"]) for i in items}
    assert ("armor", "chain_mail") in ids
    assert ("weapon", "longsword") in ids
    assert ("weapon", "handaxe") in ids


def test_resolve_rogue_fixed_gear() -> None:
    items = resolve_starting_items(
        "rogue",
        {
            "melee": "rapier",
            "ranged": "shortbow",
            "pack": "burglars_pack",
        },
        ["simple", "martial", "longsword", "rapier", "shortsword"],
        ["light"],
    )
    ids = {(i["kind"], i["id"]) for i in items}
    assert ("armor", "leather") in ids
    assert ("tool", "thieves_tools") in ids
    assert ("weapon", "rapier") in ids
