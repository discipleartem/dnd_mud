"""Каталог черт и чистое чтение grants из YAML (без apply/requirements)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.catalogs.races import collect_race_grants
from core.catalogs.skill_ids import PHB_SKILL_IDS
from core.grants.normalize import (
    grants_of_type,
    proficiency_tokens_and_skills_from_grant,
)
from core.platform.catalog_loader import load_catalog

FEATS_FILE = Path("database/progression/feats.yaml")


@dataclass(frozen=True)
class FeatGrant:
    """Выборная черта от расы/подрасы."""

    count: int
    from_list: str
    source: str


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


def resolve_feat_grants(
    feat_id: str, choices: dict[str, Any] | None = None
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Владения из черты с учётом подвыборов."""
    feat = load_feat(feat_id)
    choices = choices or {}
    weapons: list[str] = []
    armors: list[str] = []
    tools: list[str] = []
    skills: list[str] = []
    raw_grants = feat.get("grants", [])
    if not isinstance(raw_grants, list):
        return weapons, armors, tools, skills
    for grant in raw_grants:
        if not isinstance(grant, dict):
            continue
        w, a, t, s = proficiency_tokens_and_skills_from_grant(grant, choices)
        weapons.extend(w)
        armors.extend(a)
        tools.extend(t)
        skills.extend(s)
    return weapons, armors, tools, skills


def get_feat_proficiency_grants(
    feat_id: str,
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Владения из черты: (weapons, armors, tools, skills)."""
    return resolve_feat_grants(feat_id, choices)


def iter_feat_grants(feat_ids: list[str]) -> list[dict[str, Any]]:
    """Grants из выбранных черт."""
    grants: list[dict[str, Any]] = []
    for feat_id in feat_ids:
        feat = load_feat(feat_id)
        raw_grants = feat.get("grants", [])
        if not isinstance(raw_grants, list):
            continue
        for grant in raw_grants:
            if isinstance(grant, dict):
                grants.append(grant)
    return grants


def get_feat_skill_ids(
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Навыки из выбранных черт."""
    feat_choices = feat_choices or {}
    skills: list[str] = []
    for feat_id in feat_ids:
        choices = feat_choices.get(feat_id, {})
        _, _, _, s = resolve_feat_grants(feat_id, choices)
        skills.extend(s)
    return skills


def get_feat_language_ids(
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Языки из черт (linguist)."""
    feat_choices = feat_choices or {}
    langs: list[str] = []
    for feat_id in feat_ids:
        choices = feat_choices.get(feat_id, {})
        raw = choices.get("languages", [])
        if isinstance(raw, list):
            langs.extend(str(lang) for lang in raw)
    return langs


def get_feat_expertise_ids(
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Навыки с экспертным владением из черт (skill_expert)."""
    feat_choices = feat_choices or {}
    skills: list[str] = []
    for feat_id in feat_ids:
        raw = feat_choices.get(feat_id, {}).get("expertise", [])
        if isinstance(raw, list):
            for item_id in raw:
                sid = str(item_id)
                if sid in PHB_SKILL_IDS and sid not in skills:
                    skills.append(sid)
    return skills


def get_feat_save_proficiencies(
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Владение спасбросками из черт (Resilient)."""
    feat_choices = feat_choices or {}
    saves: list[str] = []
    for feat_id in feat_ids:
        feat = load_feat(feat_id)
        choices = feat_choices.get(feat_id, {})
        raw_grants = feat.get("grants", [])
        if not isinstance(raw_grants, list):
            continue
        for grant in raw_grants:
            if not isinstance(grant, dict):
                continue
            if grant.get("type") != "save_proficiency":
                continue
            if grant.get("choice"):
                picked = choices.get("ability")
                if isinstance(picked, str) and picked not in saves:
                    saves.append(picked)
            else:
                target = grant.get("ability")
                if isinstance(target, str) and target not in saves:
                    saves.append(target)
    return saves


def get_race_feat_grants(
    race_id: str, subrace_id: str | None = None
) -> list[FeatGrant]:
    """Слоты выбора черты из grants расы/подрасы."""
    result: list[FeatGrant] = []
    for grant in grants_of_type(
        collect_race_grants(race_id, subrace_id), "feat"
    ):
        count = int(grant.get("count", 1))
        from_list = str(grant.get("from", "all"))
        source = "subrace" if subrace_id else "race"
        result.append(
            FeatGrant(count=count, from_list=from_list, source=source)
        )
    return result


def race_feat_step_required(
    race_id: str, subrace_id: str | None = None
) -> bool:
    """Нужен ли шаг выбора черты при создании."""
    return bool(get_race_feat_grants(race_id, subrace_id))
