"""Тесты миграции JSON сейвов персонажей."""

from core.inventory import equip_defaults
from core.models import Character
from core.save_migration import migrate_character_dict


def test_migrate_legacy_class_key() -> None:
    """Legacy «class» → class_id."""
    raw = {
        "name": "Hero",
        "race": "human",
        "class": "fighter",
        "level": 1,
        "stats": {},
        "current_hp": 10,
        "experience": 0,
        "difficulty": "normal",
    }
    migrated = migrate_character_dict(raw)
    assert migrated["class_id"] == "fighter"
    assert "class" not in migrated
    assert migrated["schema_version"] == 1
    character = Character.from_dict(migrated)
    assert character.class_id == "fighter"


def test_migrate_recalculates_equipped() -> None:
    """Старый equipped пересчитывается через equip_defaults."""
    raw = {
        "schema_version": 1,
        "name": "Rogue",
        "race": "human",
        "class_id": "rogue",
        "level": 1,
        "stats": {
            "dex": 14,
            "str": 10,
            "con": 12,
            "int": 10,
            "wis": 10,
            "cha": 10,
        },
        "current_hp": 8,
        "experience": 0,
        "difficulty": "normal",
        "weapon_proficiencies": ["simple"],
        "inventory": [
            {"kind": "weapon", "id": "shortsword", "qty": 1},
            {"kind": "weapon", "id": "dagger", "qty": 1},
        ],
        "equipped": {"main_hand": "shortsword", "off_hand": None},
    }
    migrated = migrate_character_dict(raw)
    character = Character.from_dict(migrated)
    expected = equip_defaults(character)
    assert migrated["equipped"] == expected
    assert migrated["equip_logic_version"] == 1


def test_migrate_skips_when_equip_logic_current() -> None:
    """Повторная миграция не трогает equipped."""
    equipped = {"main_hand": "dagger", "off_hand": None, "armor": None}
    raw = {
        "schema_version": 1,
        "equip_logic_version": 1,
        "name": "Hero",
        "race": "human",
        "class_id": "fighter",
        "level": 1,
        "stats": {},
        "current_hp": 10,
        "experience": 0,
        "difficulty": "normal",
        "inventory": [{"kind": "weapon", "id": "dagger", "qty": 1}],
        "equipped": equipped,
    }
    migrated = migrate_character_dict(raw)
    assert migrated["equipped"] == equipped
