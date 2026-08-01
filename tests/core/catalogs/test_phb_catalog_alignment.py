"""Сверка каталогов database/ с каноном docs/rules (PHB partial)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from core.catalogs.classes import get_class_dict
from core.catalogs.races import collect_race_grants, get_race_bonuses

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests" / "fixtures" / "phb_equipment.yaml"


def _load_yaml(path: Path, key: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    assert isinstance(data, dict)
    section = data.get(key, {})
    assert isinstance(section, dict)
    return section


ALL_STATS = [
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
]


@pytest.mark.parametrize(
    ("race_id", "subrace_id", "bonuses"),
    [
        ("human", "standard", dict.fromkeys(ALL_STATS, 1)),
        ("dwarf", "mountain_dwarf", {"constitution": 2, "strength": 2}),
        ("half_orc", "half_orc", {"strength": 2, "constitution": 1}),
    ],
)
def test_race_ability_bonuses_match_phb(
    race_id: str, subrace_id: str, bonuses: dict[str, int]
) -> None:
    """Бонусы характеристик рас соответствуют PHB."""
    assert get_race_bonuses(race_id, subrace_id) == bonuses


@pytest.mark.parametrize(
    ("race_id", "subrace_id", "grant_type"),
    [
        ("half_orc", "half_orc", "darkvision"),
        ("half_orc", "half_orc", "skill_proficiency"),
        ("elf", "dark_elf_drow", "darkvision"),
        ("elf", None, "immunity"),
    ],
)
def test_race_grants_include_phb_features(
    race_id: str, subrace_id: str | None, grant_type: str
) -> None:
    """Ключевые расовые особенности присутствуют в grants."""
    types = {g.get("type") for g in collect_race_grants(race_id, subrace_id)}
    assert grant_type in types


@pytest.mark.parametrize(
    ("subrace_id", "expected_range"),
    [
        ("high_elf", 60),
        ("wood_elf", 60),
        ("dark_elf_drow", 120),
    ],
)
def test_elf_subrace_darkvision_range(
    subrace_id: str, expected_range: int
) -> None:
    """Тёмное зрение эльфийских подрас — один grant с дальностью PHB."""
    grants = collect_race_grants("elf", subrace_id)
    darkvision = [g for g in grants if g.get("type") == "darkvision"]
    assert len(darkvision) == 1
    assert darkvision[0].get("range") == expected_range


@pytest.mark.parametrize(
    ("class_id", "level", "feature_id"),
    [
        ("fighter", 2, "action_surge"),
        ("fighter", 5, "extra_attack"),
        ("rogue", 2, "cunning_action"),
        ("rogue", 5, "uncanny_dodge"),
        ("cleric", 2, "channel_divinity"),
        ("bard", 14, "magical_secrets_14"),
    ],
)
def test_class_progression_feature_ids(
    class_id: str, level: int, feature_id: str
) -> None:
    """Умения класса на уровне соответствуют PHB-карточкам."""
    info = get_class_dict(class_id)
    assert info
    progression = info.get("progression", {})
    level_data = progression.get(level) or progression.get(str(level), {})
    if not isinstance(level_data, dict):
        grants: list[Any] = []
    else:
        grants = level_data.get("grants", [])
    ids = {g.get("id") for g in grants if isinstance(g, dict)}
    assert feature_id in ids


def test_phb_equipment_fixture_matches_catalog() -> None:
    """Исправленные предметы снаряжения совпадают с эталоном PHB."""
    expected = yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(expected, dict)

    weapons = _load_yaml(ROOT / "database/equipment/weapon.yaml", "weapons")
    gear = _load_yaml(ROOT / "database/equipment/equipment.yaml", "equipment")

    for weapon_id, exp in expected.get("weapons", {}).items():
        item = weapons[weapon_id]
        assert item["cost"] == exp["cost"]
        assert item["damage"] == exp["damage"]
        assert item["weight"] == exp["weight"]

    for gear_id, exp in expected.get("gear", {}).items():
        assert gear[gear_id]["cost"] == exp["cost"]


@pytest.mark.parametrize(
    "feat_id",
    [
        "dungeon_delver",
        "healer",
        "alert",
        "linguist",
        "crossbow_expert",
        "charger",
        "dual_wielder",
        "observant",
        "tavern_brawler",
    ],
)
def test_feat_grants_no_removed_phb_fields(feat_id: str) -> None:
    """Grants черт не содержат устаревших полей после выравнивания с PHB."""
    feats = _load_yaml(ROOT / "database/progression/feats.yaml", "feats")
    feat = feats[feat_id]
    grants = feat.get("grants", [])
    assert isinstance(grants, list)
    for grant in grants:
        assert isinstance(grant, dict)
        assert "counter_attack_damage" not in grant
        assert "stabilize_no_check" not in grant
    if feat_id == "dungeon_delver":
        trap = next(g for g in grants if g.get("type") == "trap_mastery")
        assert trap.get("search_traps_normal_speed") is True
    if feat_id == "healer":
        heal = next(g for g in grants if g.get("type") == "healing")
        assert heal.get("stabilize_restores_1_hp") is True
    if feat_id == "alert":
        assert any(g.get("type") == "alert" for g in grants)
    if feat_id == "linguist":
        assert any(g.get("type") == "cipher_writing" for g in grants)
    if feat_id == "crossbow_expert":
        mastery = next(g for g in grants if g.get("type") == "weapon_mastery")
        assert mastery.get("ranged_no_disadvantage_in_melee") is True
    if feat_id == "charger":
        charge = next(g for g in grants if g.get("type") == "charger")
        assert charge.get("shove_bonus_action") is True
        assert charge.get("shove_distance") == 10
    if feat_id == "dual_wielder":
        dual = next(g for g in grants if g.get("type") == "dual_wielder")
        assert dual.get("non_light_dual_wield") is True
        assert dual.get("draw_stow_two_weapons") is True
    if feat_id == "observant":
        assert any(g.get("type") == "lip_reading" for g in grants)
    if feat_id == "tavern_brawler":
        brawler = next(
            g for g in grants if g.get("type") == "unarmed_improvised"
        )
        assert brawler.get("bonus_action_grapple_on_hit") is True
