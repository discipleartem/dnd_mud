"""Требования черт и отбор для меню выбора."""

from typing import Any

from core.feat_visibility import feat_visible_for_selection
from core.feats_loader import (
    FeatGrant,
    FeatRequirementContext,
    load_feat,
    load_feats,
)


def get_race_feat_grants(
    race_id: str, subrace_id: str | None = None
) -> list[FeatGrant]:
    """Слоты выбора черты из grants расы/подрасы."""
    from core.grants import grants_of_type
    from core.races import collect_race_grants

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


def character_has_spellcasting(
    class_id: str, subclass_id: str | None, level: int
) -> bool:
    """Может ли персонаж накладывать заклинания (для требований черт)."""
    from core.classes import character_has_spellcasting as _from_yaml

    return _from_yaml(class_id, subclass_id, level)


def _armor_requirement_met(
    required: list[str], armor_tokens: list[str]
) -> bool:
    """Проверка владения доспехом для требования черты."""
    return any(armor in armor_tokens for armor in required)


def _requirement_met(
    req: dict[str, Any],
    ctx: FeatRequirementContext,
    *,
    or_group: list[dict[str, Any]] | None = None,
) -> bool:
    """Одно требование черты."""
    rtype = req.get("type", "")
    if rtype == "ability_score":
        target = str(req.get("target", ""))
        value = int(req.get("value", 0))
        if target not in ctx.stats:
            return False
        return int(ctx.stats[target]) >= value
    if rtype == "armor_proficiency":
        raw = req.get("armors", [])
        if isinstance(raw, list):
            return _armor_requirement_met(
                [str(a) for a in raw], ctx.armor_tokens
            )
        return False
    if rtype == "spellcasting":
        return ctx.has_spellcasting
    return True


def requirement_met(req: dict[str, Any], ctx: FeatRequirementContext) -> bool:
    """Выполнено ли одно требование черты."""
    return _requirement_met(req, ctx)


def feat_meets_requirements(feat_id: str, ctx: FeatRequirementContext) -> bool:
    """Выполнены ли требования черты."""
    feat = load_feat(feat_id)
    raw_reqs = feat.get("requirements", [])
    if not isinstance(raw_reqs, list) or not raw_reqs:
        return True

    or_reqs: list[dict[str, Any]] = []
    and_reqs: list[dict[str, Any]] = []
    for req in raw_reqs:
        if not isinstance(req, dict):
            continue
        if req.get("alternative"):
            or_reqs.append(req)
        else:
            and_reqs.append(req)

    for req in and_reqs:
        if not _requirement_met(req, ctx):
            return False
    if or_reqs:
        return any(_requirement_met(req, ctx) for req in or_reqs)
    return True


def can_take_feat(
    feat_id: str,
    existing_ids: list[str],
    *,
    repeatable: bool | None = None,
) -> bool:
    """Можно ли взять черту (уникальность)."""
    feat = load_feat(feat_id)
    is_repeatable = bool(feat.get("repeatable", False))
    if repeatable is not None:
        is_repeatable = repeatable
    if is_repeatable:
        return True
    return feat_id not in existing_ids


def feat_has_requirements(feat_id: str) -> bool:
    """Есть ли у черты явные требования в YAML."""
    feat = load_feat(feat_id)
    raw_reqs = feat.get("requirements", [])
    return isinstance(raw_reqs, list) and bool(raw_reqs)


def list_feats_for_selection(
    ctx: FeatRequirementContext,
    existing_ids: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Черты для меню: (доступные, требования не выполнены, скрытые)."""
    eligible: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    hidden: list[dict[str, Any]] = []
    for feat in load_feats():
        feat_id = str(feat.get("id", ""))
        if not feat_id or not can_take_feat(feat_id, existing_ids):
            continue
        if not feat_visible_for_selection(feat_id, ctx):
            hidden.append(feat)
            continue
        if feat_meets_requirements(feat_id, ctx):
            eligible.append(feat)
        elif feat_has_requirements(feat_id):
            blocked.append(feat)
    return eligible, blocked, hidden
