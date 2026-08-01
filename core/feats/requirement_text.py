"""Чистое текстовое форматирование требований черт (без print)."""

from typing import Any

from core.feats.requirement_handlers import format_requirement_text
from core.feats.requirements import FeatRequirementContext
from core.platform.localization import get_string
from core.types import StringsDict


def _split_feat_requirements(
    feat: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """AND- и OR-группы требований из записи черты."""
    raw_reqs = feat.get("requirements", [])
    if not isinstance(raw_reqs, list):
        return [], []
    and_reqs: list[dict[str, Any]] = []
    or_reqs: list[dict[str, Any]] = []
    for req in raw_reqs:
        if not isinstance(req, dict):
            continue
        if req.get("alternative"):
            or_reqs.append(req)
        else:
            and_reqs.append(req)
    return and_reqs, or_reqs


def _format_or_ability_requirements(
    strings: StringsDict,
    or_reqs: list[dict[str, Any]],
) -> str | None:
    """OR-группа ability_score — «Интеллект или Мудрость 13+»."""
    if not or_reqs:
        return None
    if not all(req.get("type") == "ability_score" for req in or_reqs):
        return None
    values = {int(req.get("value", 0)) for req in or_reqs}
    if len(values) != 1:
        return None
    value = next(iter(values))
    abilities = [
        get_string(strings, f"stats.{req.get('target', '')}")
        for req in or_reqs
    ]
    or_sep = get_string(strings, "character.feat_req_or_sep")
    return get_string(
        strings,
        "character.feat_req_ability_or",
        abilities=or_sep.join(abilities),
        value=value,
    )


def _format_requirement_text(
    strings: StringsDict,
    req: dict[str, Any],
    ctx: FeatRequirementContext,
    language: str,
) -> str:
    """Текст одного требования для экрана выбора."""
    return format_requirement_text(strings, req, ctx, language)
