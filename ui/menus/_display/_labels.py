"""Общие хелперы подписей из каталогов."""

from typing import Any


def _label_from_catalog(
    catalog: list[dict[str, Any]],
    entity_id: str,
    *,
    default: str | None = None,
) -> str:
    """Имя сущности по id из списка каталога."""
    for item in catalog:
        if item.get("id") == entity_id:
            return str(item.get("name", entity_id))
    return default if default is not None else entity_id
