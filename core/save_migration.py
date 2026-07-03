"""Миграции JSON сейвов персонажей при загрузке."""

from typing import Any

from core.inventory import equip_defaults
from core.models import Character

CHARACTERS_SCHEMA_VERSION = 1
EQUIP_LOGIC_VERSION = 1


def _schema_version(data: dict[str, Any]) -> int:
    """Версия схемы из JSON; 0 — legacy без поля."""
    raw = data.get("schema_version")
    if isinstance(raw, int):
        return raw
    return 0


def _migrate_v0_to_v1(data: dict[str, Any]) -> dict[str, Any]:
    """Legacy: class → class_id, race_id → race."""
    result = dict(data)
    if "class_id" not in result and "class" in result:
        result["class_id"] = result.pop("class")
    if "race" not in result and "race_id" in result:
        result["race"] = result.pop("race_id")
    result["schema_version"] = 1
    return result


def _migrate_equipped(data: dict[str, Any]) -> dict[str, Any]:
    """Пересчёт экипировки для сейвов до dual-wield / versatile."""
    if data.get("equip_logic_version", 0) >= EQUIP_LOGIC_VERSION:
        return data
    if not data.get("inventory"):
        result = dict(data)
        result["equip_logic_version"] = EQUIP_LOGIC_VERSION
        return result
    character = Character.from_dict(data)
    result = dict(data)
    result["equipped"] = equip_defaults(character)
    result["equip_logic_version"] = EQUIP_LOGIC_VERSION
    return result


def migrate_character_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Применить цепочку миграций к сырым данным JSON."""
    result = dict(data)
    version = _schema_version(result)
    if version < 1:
        result = _migrate_v0_to_v1(result)
    result = _migrate_equipped(result)
    if _schema_version(result) < CHARACTERS_SCHEMA_VERSION:
        result["schema_version"] = CHARACTERS_SCHEMA_VERSION
    return result
