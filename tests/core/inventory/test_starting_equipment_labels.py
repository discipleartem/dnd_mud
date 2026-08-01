"""Тесты подписей стартового снаряжения класса."""

from typing import Any

import pytest

from core.inventory.starting_equipment import list_equipment_options_by_group
from core.inventory.starting_equipment_labels import (
    equipment_choice_label,
    format_equipment_option_label,
    summarize_class_starting_equipment,
)

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_equipment_choice_label_localizes_melee(
    ru_strings: dict[str, Any],
) -> None:
    assert equipment_choice_label("melee", ru_strings) == "ближний бой"
    assert equipment_choice_label("ranged", ru_strings) == "дальний бой"
    assert equipment_choice_label("unknown_group", ru_strings) == (
        "unknown_group"
    )


def test_format_equipment_option_label_armor_hints(
    ru_strings: dict[str, Any],
) -> None:
    groups = list_equipment_options_by_group("cleric")
    armor_opts = {opt["id"]: opt for opt in groups["armor"]}
    assert (
        format_equipment_option_label(
            armor_opts["scale_mail"], ru_strings, "ru"
        )
        == "а) Чешуйчатый доспех (средние доспехи, КД 14 + Лов, макс. 2)"
    )
    assert (
        format_equipment_option_label(armor_opts["leather"], ru_strings, "ru")
        == "б) Кожаный доспех (лёгкие доспехи, КД 11 + Лов)"
    )
    assert (
        format_equipment_option_label(
            armor_opts["chain_mail"], ru_strings, "ru"
        )
        == "в) Кольчуга (тяжёлые доспехи, КД 16)"
    )

    weapon_opts = {opt["id"]: opt for opt in groups["weapon"]}
    assert (
        format_equipment_option_label(
            weapon_opts["warhammer"], ru_strings, "ru"
        )
        == "б) Боевой молот (воинское оружие, 1к8/1к10)"
    )


def test_format_equipment_option_label_pack_and_melee(
    ru_strings: dict[str, Any],
) -> None:
    fighter = list_equipment_options_by_group("fighter")
    armor = {opt["id"]: opt for opt in fighter["armor"]}
    assert format_equipment_option_label(
        armor["leather_longbow"], ru_strings, "ru"
    ) == (
        "б) Кожаный доспех, длинный лук и 20 стрел "
        "(лёгкие доспехи, КД 11 + Лов, 1к8)"
    )
    pack = {opt["id"]: opt for opt in fighter["pack"]}
    pack_label = format_equipment_option_label(
        pack["dungeoneers_pack"], ru_strings, "ru"
    )
    assert pack_label.startswith("а) Набор исследователя подземелий (")
    assert "Рюкзак" in pack_label
    assert "Шлямбур ×10" in pack_label

    rogue = list_equipment_options_by_group("rogue")
    melee = {opt["id"]: opt for opt in rogue["melee"]}
    assert (
        format_equipment_option_label(melee["rapier"], ru_strings, "ru")
        == "а) Рапира (1к8)"
    )
    assert (
        format_equipment_option_label(melee["shortsword"], ru_strings, "ru")
        == "б) Короткий меч (1к6)"
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
