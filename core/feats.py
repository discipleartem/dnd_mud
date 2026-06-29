"""Загрузка черт из YAML."""

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from core.hp_bonuses import HpBonusSource, hit_point_bonus_amount
from core.io import load_yaml
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
    class_id: str | None = None
    subclass_id: str | None = None
    level: int = 1
    has_spellcasting: bool = False


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


def resolve_feat_ability_bonuses(
    feat_id: str, choices: dict[str, Any] | None = None
) -> StatMap:
    """Бонусы к характеристикам из черты."""
    from core.stats import STAT_NAMES

    feat = load_feat(feat_id)
    choices = choices or {}
    bonuses: StatMap = {}
    fixed = feat.get("ability_bonuses", {})
    if isinstance(fixed, dict):
        for key, val in fixed.items():
            if key in STAT_NAMES:
                bonuses[key] = int(val)

    choice_list = feat.get("ability_bonuses_choice", [])
    amount = int(feat.get("ability_bonuses_amount", 1))
    if isinstance(choice_list, list) and choice_list:
        picked = choices.get("ability")
        if isinstance(picked, str) and picked in choice_list:
            bonuses[picked] = bonuses.get(picked, 0) + amount
    return bonuses


def _grants_from_mechanics(
    mechanics: dict[str, Any],
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Из mechanics feature: weapons, armors, tools, skills."""
    from core.skills import PHB_SKILL_IDS

    choices = choices or {}
    weapons: list[str] = []
    armors: list[str] = []
    tools: list[str] = []
    skills: list[str] = []
    mtype = mechanics.get("type", "")
    if mtype == "weapon_proficiency":
        if mechanics.get("choice"):
            raw = choices.get("weapons", [])
            if isinstance(raw, list):
                weapons.extend(str(w) for w in raw)
        else:
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
    elif mtype == "multiple_proficiency":
        raw = choices.get("skills_tools", [])
        if isinstance(raw, list):
            for entry in raw:
                if not isinstance(entry, dict):
                    continue
                kind = entry.get("type", "skill")
                item_id = str(entry.get("id", ""))
                if kind == "tool":
                    tools.append(item_id)
                elif item_id in PHB_SKILL_IDS:
                    skills.append(item_id)
    elif mtype == "skill_expertise":
        raw = choices.get("expertise", [])
        if isinstance(raw, list):
            for item_id in raw:
                sid = str(item_id)
                if sid in PHB_SKILL_IDS:
                    skills.append(sid)
    # language: обрабатывается в get_feat_language_ids, не владения
    return weapons, armors, tools, skills


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
    raw_features = feat.get("features", [])
    if not isinstance(raw_features, list):
        return weapons, armors, tools, skills
    for feature in raw_features:
        if not isinstance(feature, dict):
            continue
        mechanics = feature.get("mechanics", {})
        if not isinstance(mechanics, dict):
            continue
        w, a, t, s = _grants_from_mechanics(mechanics, choices)
        weapons.extend(w)
        armors.extend(a)
        tools.extend(t)
        skills.extend(s)
    return weapons, armors, tools, skills


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
    from core.skills import PHB_SKILL_IDS

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


def apply_feats_to_stats(
    stats: StatMap,
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> StatMap:
    """Применить бонусы характеристик от всех черт."""
    from core.stats import (
        ABILITY_SCORE_MAX,
        STAT_NAMES,
        apply_bonuses_to_stats,
    )

    feat_choices = feat_choices or {}
    result = stats.copy()
    for feat_id in feat_ids:
        bonuses = resolve_feat_ability_bonuses(
            feat_id, feat_choices.get(feat_id, {})
        )
        result = apply_bonuses_to_stats(result, bonuses)
    for stat in STAT_NAMES:
        if stat in result and result[stat] > ABILITY_SCORE_MAX:
            result[stat] = ABILITY_SCORE_MAX
    return result


def apply_feat_grants_to_character(
    character: Any,
    feat_id: str,
    choices: dict[str, Any] | None = None,
) -> Any:
    """Добавить на персонажа владения, навыки и языки из одной черты."""
    from dataclasses import replace

    from core.proficiencies import merge_proficiency_tokens
    from core.skills import merge_proficiencies

    choices = choices or {}
    feat_choices = {feat_id: choices}
    weapons, armors, tools, _ = resolve_feat_grants(feat_id, choices)
    skills = get_feat_skill_ids([feat_id], feat_choices)
    languages = get_feat_language_ids([feat_id], feat_choices)
    expertise = get_feat_expertise_ids([feat_id], feat_choices)

    merged_langs = list(character.languages)
    for lang_id in languages:
        if lang_id not in merged_langs:
            merged_langs.append(lang_id)

    return replace(
        character,
        weapon_proficiencies=merge_proficiency_tokens(
            character.weapon_proficiencies, weapons
        ),
        armor_proficiencies=merge_proficiency_tokens(
            character.armor_proficiencies, armors
        ),
        tool_proficiencies=merge_proficiency_tokens(
            character.tool_proficiencies, tools
        ),
        skills=merge_proficiencies(character.skills, skills),
        languages=merged_langs,
        skill_expertise=merge_proficiencies(
            character.skill_expertise, expertise
        ),
    )


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


def get_feat_proficiency_grants(
    feat_id: str,
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Владения из черты: (weapons, armors, tools, skills)."""
    return resolve_feat_grants(feat_id, choices)


def feat_has_requirements(feat_id: str) -> bool:
    """Есть ли у черты явные требования в YAML."""
    feat = load_feat(feat_id)
    raw_reqs = feat.get("requirements", [])
    return isinstance(raw_reqs, list) and bool(raw_reqs)


def list_feats_for_selection(
    ctx: FeatRequirementContext,
    existing_ids: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Черты для меню: (требования выполнены, требования не выполнены).

    Уже взятые черты (кроме repeatable) не включаются.
    """
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
