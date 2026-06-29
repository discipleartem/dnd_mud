"""Загрузка черт из YAML."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from core.io import load_yaml

FEATS_FILE = Path("database/progression/feats.yaml")


@lru_cache(maxsize=1)
def _load_feats_yaml() -> dict[str, Any]:
    """Загрузить feats из YAML."""
    data = load_yaml(FEATS_FILE)
    feats = data.get("feats", {})
    if isinstance(feats, dict):
        return feats
    return {}


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


def _grants_from_mechanics(
    mechanics: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Из mechanics feature: weapons, armors, tools, skills."""
    weapons: list[str] = []
    armors: list[str] = []
    tools: list[str] = []
    skills: list[str] = []
    mtype = mechanics.get("type", "")
    if mtype == "weapon_proficiency":
        raw = mechanics.get("weapons", [])
        if isinstance(raw, list):
            weapons.extend(str(w) for w in raw)
    elif mtype == "armor_proficiency":
        raw = mechanics.get("armors", [])
        if isinstance(raw, list):
            armors.extend(str(a) for a in raw)
    elif mtype == "tool_proficiency":
        raw = mechanics.get("tools", [])
        if isinstance(raw, list):
            tools.extend(str(t) for t in raw)
    elif mtype == "skill_proficiency":
        raw = mechanics.get("skills", [])
        if isinstance(raw, list):
            skills.extend(str(s) for s in raw)
    return weapons, armors, tools, skills


def get_feat_proficiency_grants(
    feat_id: str,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Владения из черты: (weapons, armors, tools, skills)."""
    feat = load_feat(feat_id)
    weapons: list[str] = []
    armors: list[str] = []
    tools: list[str] = []
    skills: list[str] = []
    raw_features = feat.get("features", [])
    if not isinstance(raw_features, list):
        return weapons, armors, tools, skills
    for feature in raw_features:
        if not isinstance(feature, dict):
            continue
        mechanics = feature.get("mechanics", {})
        if not isinstance(mechanics, dict):
            continue
        w, a, t, s = _grants_from_mechanics(mechanics)
        weapons.extend(w)
        armors.extend(a)
        tools.extend(t)
        skills.extend(s)
    return weapons, armors, tools, skills
