"""Версии и миграции JSON сохранений персонажей."""

from typing import Any

CHARACTERS_SCHEMA_VERSION = 1


def migrate_character_data(data: dict[str, Any]) -> dict[str, Any]:
    """Привести загруженный JSON персонажа к текущей схеме."""
    version = data.get("schema_version", 0)
    if not isinstance(version, int):
        version = 0
    if version >= CHARACTERS_SCHEMA_VERSION:
        return data
    migrated = dict(data)
    migrated["schema_version"] = CHARACTERS_SCHEMA_VERSION
    return migrated
