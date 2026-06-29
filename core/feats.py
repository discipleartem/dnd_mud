"""Загрузка черт из YAML — публичный фасад."""

import re
from typing import Any

from core.feats_grants import (
    apply_feat_grants_to_character,
    apply_feats_to_stats,
    get_feat_expertise_ids,
    get_feat_language_ids,
    get_feat_proficiency_grants,
    get_feat_skill_ids,
    resolve_feat_ability_bonuses,
    resolve_feat_grants,
)
from core.feats_loader import (
    FeatGrant,
    FeatRequirementContext,
    load_feat,
    load_feats,
)
from core.hp_bonuses import HpBonusSource, hit_point_bonus_amount

__all__ = [
    "FeatGrant",
    "FeatRequirementContext",
    "apply_feat_grants_to_character",
    "apply_feats_to_stats",
    "can_take_feat",
    "character_has_spellcasting",
    "feat_full_description_lines",
    "feat_has_requirements",
    "feat_meets_requirements",
    "feat_summary_description",
    "get_feat_expertise_ids",
    "get_feat_hp_bonus_per_level",
    "get_feat_hp_bonus_sources",
    "get_feat_language_ids",
    "get_feat_proficiency_grants",
    "get_feat_skill_ids",
    "get_race_feat_grants",
    "list_available_feats",
    "list_feats_for_selection",
    "load_feat",
    "load_feats",
    "race_feat_step_required",
    "requirement_met",
    "resolve_feat_ability_bonuses",
    "resolve_feat_grants",
    "tough_hp_adjustment_on_acquire",
]

_BENEFITS_MARKER = re.compile(
    r"(?:,\s*)?(?:и\s+)?(?:вы\s+)?(?:дающие\s+)?"
    r"получаете\s+следующие\s+преимущества",
    re.IGNORECASE,
)
_BENEFITS_LINE_MARKER = re.compile(
    r"получаете\s+следующие\s+преимущества|дающие\s+следующие\s+преимущества",
    re.IGNORECASE,
)


def _collapse_whitespace(text: str) -> str:
    """Схлопнуть пробелы и переносы для поиска маркера в description_full."""
    return re.sub(r"\s+", " ", text.strip())


def feat_intro_from_full(description_full: str) -> str:
    """Вводный текст PHB до «…получаете следующие преимущества:»."""
    normalized = _collapse_whitespace(description_full)
    match = _BENEFITS_MARKER.search(normalized)
    if not match:
        return ""
    intro = normalized[: match.start()].strip().rstrip(",").strip()
    return intro


def feat_benefit_lines_from_full(description_full: str) -> list[str]:
    """Строки преимуществ (маркированный список) из description_full."""
    lines: list[str] = []
    for raw in description_full.strip().splitlines():
        stripped = raw.strip()
        if not stripped.startswith("•"):
            continue
        if _BENEFITS_LINE_MARKER.search(stripped):
            continue
        lines.append(stripped)
    return lines


def feat_summary_description(feat: dict[str, Any]) -> str:
    """Краткое описание для списка выбора."""
    short = feat.get("description_short")
    if isinstance(short, str) and short.strip():
        return short.strip()
    full = feat.get("description_full")
    if isinstance(full, str) and full.strip():
        intro = feat_intro_from_full(full)
        if intro:
            return intro
    raw = feat.get("description", "")
    return str(raw).strip()


def feat_full_description_lines(feat: dict[str, Any]) -> list[str]:
    """Строки детального описания (преимущества) для экрана подтверждения."""
    full = feat.get("description_full")
    if isinstance(full, str) and full.strip():
        benefits = feat_benefit_lines_from_full(full)
        if benefits:
            return benefits
        return [
            line.rstrip() for line in full.strip().splitlines() if line.strip()
        ]
    if isinstance(full, list):
        return [str(line) for line in full if str(line).strip()]

    lines: list[str] = []
    raw_features = feat.get("features", [])
    if isinstance(raw_features, list):
        for feature in raw_features:
            if not isinstance(feature, dict):
                continue
            fdesc = str(feature.get("description", "")).strip()
            if not fdesc:
                continue
            fname = str(feature.get("name", "")).strip()
            if fname and fname not in fdesc:
                lines.append(f"• {fname}: {fdesc}")
            else:
                lines.append(f"• {fdesc}")
    if not lines:
        summary = str(feat.get("description", "")).strip()
        if summary:
            lines.append(summary)
    return lines


def get_race_feat_grants(
    race_id: str, subrace_id: str | None = None
) -> list[FeatGrant]:
    """Слоты выбора черты из features расы/подрасы."""
    from core.skills import get_merged_race_features

    grants: list[FeatGrant] = []
    for feat in get_merged_race_features(race_id, subrace_id):
        if feat.get("type") != "feat":
            continue
        mechanics = feat.get("mechanics", {})
        if not isinstance(mechanics, dict):
            mechanics = {}
        count = int(mechanics.get("count", 1))
        from_list = str(mechanics.get("from_list", "all"))
        source = "subrace" if subrace_id else "race"
        grants.append(
            FeatGrant(count=count, from_list=from_list, source=source)
        )
    return grants


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


def tough_hp_adjustment_on_acquire(level: int) -> int:
    """Дополнительные HP при взятии черты Крепкий: 2 × уровень."""
    return 2 * level


def get_feat_hp_bonus_sources(feat_ids: list[str]) -> list[HpBonusSource]:
    """Бонусы HP за уровень из выбранных черт (имя — название черты)."""
    sources: list[HpBonusSource] = []
    for feat_id in feat_ids:
        feat = load_feat(feat_id)
        feat_name = str(feat.get("name", feat_id)).strip() or feat_id
        raw_features = feat.get("features", [])
        if not isinstance(raw_features, list):
            continue
        for feature in raw_features:
            if not isinstance(feature, dict):
                continue
            mechanics = feature.get("mechanics", {})
            if not isinstance(mechanics, dict):
                mechanics = {}
            amount = hit_point_bonus_amount(mechanics, feature)
            if amount <= 0:
                continue
            sources.append(HpBonusSource(name=feat_name, amount=amount))
    return sources


def get_feat_hp_bonus_per_level(feat_ids: list[str]) -> int:
    """Дополнительные HP за уровень из выбранных черт."""
    return sum(s.amount for s in get_feat_hp_bonus_sources(feat_ids))


def feat_has_requirements(feat_id: str) -> bool:
    """Есть ли у черты явные требования в YAML."""
    feat = load_feat(feat_id)
    raw_reqs = feat.get("requirements", [])
    return isinstance(raw_reqs, list) and bool(raw_reqs)


def list_feats_for_selection(
    ctx: FeatRequirementContext,
    existing_ids: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Черты для меню: (требования выполнены, требования не выполнены)."""
    eligible: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for feat in load_feats():
        feat_id = str(feat.get("id", ""))
        if not feat_id or not can_take_feat(feat_id, existing_ids):
            continue
        if feat_meets_requirements(feat_id, ctx):
            eligible.append(feat)
        elif feat_has_requirements(feat_id):
            blocked.append(feat)
    return eligible, blocked


def list_available_feats(
    ctx: FeatRequirementContext,
    existing_ids: list[str],
) -> list[dict[str, Any]]:
    """Черты, доступные для выбора (требования выполнены)."""
    eligible, _ = list_feats_for_selection(ctx, existing_ids)
    return eligible
