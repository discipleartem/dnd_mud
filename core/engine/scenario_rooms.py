"""Модель комнат и выходов в YAML-сценариях."""

from typing import Any


def node_exits(node: dict[str, Any]) -> dict[str, str]:
    """Направление → id узла из поля ``exits``."""
    raw = node.get("exits")
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for direction, target in raw.items():
        if target is None:
            continue
        result[str(direction)] = str(target)
    return result


def resolve_exit(node: dict[str, Any], direction: str) -> str | None:
    """Целевой узел по направлению или None."""
    return node_exits(node).get(direction)
