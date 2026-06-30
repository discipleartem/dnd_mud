"""Загрузка каталога черт из YAML."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.catalog_loader import load_catalog
from core.types import StatMap

FEATS_FILE = Path("database/progression/feats.yaml")


@dataclass(frozen=True)
class FeatGrant:
    """Выборная черта от расы/подрасы."""

    count: int
    from_list: str
    source: str


@dataclass(frozen=True)
class FeatRequirementContext:
    """Контекст для проверки требований черты."""

    stats: StatMap
    weapon_tokens: list[str]
    armor_tokens: list[str]
    tool_tokens: list[str]
    race_id: str | None = None
    subrace_id: str | None = None
    background_id: str | None = None
    class_id: str | None = None
    subclass_id: str | None = None
    level: int = 1
    has_spellcasting: bool = False
    skills: list[str] = field(default_factory=list)


def _load_feats_yaml() -> dict[str, Any]:
    """Загрузить feats из YAML."""
    return load_catalog(FEATS_FILE, "feats")


def load_feats() -> list[dict[str, Any]]:
    """Список всех черт."""
    result: list[dict[str, Any]] = []
    for feat_id, info in _load_feats_yaml().items():
        if isinstance(info, dict):
            entry = dict(info)
            entry["id"] = feat_id
            result.append(entry)
    return result


def load_feat(feat_id: str) -> dict[str, Any]:
    """Данные одной черты."""
    info = _load_feats_yaml().get(feat_id, {})
    if isinstance(info, dict):
        entry = dict(info)
        entry["id"] = feat_id
        return entry
    return {"id": feat_id}
