"""Черты персонажа: загрузка, применение, требования, видимость, описания."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.catalog_loader import load_catalog
from core.classes import character_has_spellcasting
from core.grants import (
    normalize_armor_token,
    proficiency_tokens_and_skills_from_grant,
)
from core.grants_context import CreationContext
from core.progression import HpBonusSource, hit_point_bonus_amount
from core.types import StatMap

FEATS_FILE = Path("database/progression/feats.yaml")

_BENEFITS_MARKER = re.compile(
    r"(?:,\s*)?(?:и\s+)?(?:вы\s+)?(?:дающие\s+)?"
    r"получаете\s+следующие\s+преимущества",
    re.IGNORECASE,
)
_BENEFITS_LINE_MARKER = re.compile(
    r"получаете\s+следующие\s+преимущества|дающие\s+следующие\s+преимущества",
    re.IGNORECASE,
)

_PROFICIENCY_GRANT_TYPES = frozenset(
    {
        "weapon_proficiency",
        "armor_proficiency",
        "skill_proficiency",
        "tool_proficiency",
        "multiple_proficiency",
        "bonus_proficiencies",
    }
)


# ============================================================================
# Dataclasses и загрузка
# ============================================================================


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


# ============================================================================
# Описания черт
# ============================================================================


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
    raw_grants = feat.get("grants", [])
    if isinstance(raw_grants, list):
        for grant in raw_grants:
            if not isinstance(grant, dict):
                continue
            gdesc = str(grant.get("description", "")).strip()
            if not gdesc:
                continue
            gname = str(grant.get("name", "")).strip()
            if gname and gname not in gdesc:
                lines.append(f"• {gname}: {gdesc}")
            else:
                lines.append(f"• {gdesc}")
    if not lines:
        summary = str(feat.get("description", "")).strip()
        if summary:
            lines.append(summary)
    return lines


# ============================================================================
# Применение черт
# ============================================================================


def tough_hp_adjustment_on_acquire(level: int) -> int:
    """Дополнительные HP при взятии черты Крепкий: 2 × уровень."""
    return 2 * level


def get_feat_hp_bonus_sources(feat_ids: list[str]) -> list[HpBonusSource]:
    """Бонусы HP за уровень из выбранных черт (имя — название черты)."""
    sources: list[HpBonusSource] = []
    for feat_id in feat_ids:
        feat = load_feat(feat_id)
        feat_name = str(feat.get("name", feat_id)).strip() or feat_id
        raw_grants = feat.get("grants", [])
        if not isinstance(raw_grants, list):
            continue
        for grant in raw_grants:
            if not isinstance(grant, dict):
                continue
            amount = hit_point_bonus_amount(grant)
            if amount <= 0:
                continue
            name = str(grant.get("name", "")).strip() or feat_name
            sources.append(HpBonusSource(name=name, amount=amount))
    return sources


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


def get_feat_proficiency_grants(
    feat_id: str,
    choices: dict[str, Any] | None = None,
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Владения из черты: (weapons, armors, tools, skills)."""
    return resolve_feat_grants(feat_id, choices)


def _iter_feat_grants(feat_ids: list[str]) -> list[dict[str, Any]]:
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


def has_non_light_dual_wield(feat_ids: list[str]) -> bool:
    """Черта «Использование двух оружий» — сражение без свойства «лёгкое»."""
    return any(
        grant.get("type") == "dual_wielder"
        and grant.get("non_light_dual_wield")
        for grant in _iter_feat_grants(feat_ids)
    )


def dual_wielder_ac_bonus_from_feats(feat_ids: list[str]) -> int:
    """Бонус КД из grant dual_wielder (обычно +1)."""
    bonus = 0
    for grant in _iter_feat_grants(feat_ids):
        if grant.get("type") != "dual_wielder":
            continue
        amount = grant.get("ac_bonus", 0)
        if isinstance(amount, int) and amount > 0:
            bonus += amount
    return bonus


# ============================================================================
# Видимость черт
# ============================================================================


def _creation_context(
    race_id: str,
    subrace_id: str | None,
    background_id: str | None,
    class_id: str,
    subclass_id: str | None,
    level: int,
    *,
    skills: list[str] | None = None,
    weapon_tokens: list[str] | None = None,
    tool_tokens: list[str] | None = None,
) -> CreationContext:
    return CreationContext(
        race_id=race_id,
        subrace_id=subrace_id,
        class_id=class_id,
        background_id=background_id,
        subclass_id=subclass_id,
        level=level,
        extra_skills=tuple(skills) if skills else (),
        extra_weapon_tokens=tuple(weapon_tokens) if weapon_tokens else (),
        extra_tool_tokens=tuple(tool_tokens) if tool_tokens else (),
    )


def creation_known_for_feat_picks(
    race_id: str,
    subrace_id: str | None,
    background_id: str | None,
    class_id: str,
    subclass_id: str | None,
    level: int,
) -> tuple[list[str], list[str], list[str]]:
    """Навыки, инструменты и токены оружия до подвыборов внутри черты."""
    from core.character_build import resolve_grants_for_context

    ctx = _creation_context(
        race_id, subrace_id, background_id, class_id, subclass_id, level
    )
    grants = resolve_grants_for_context(ctx, include_feat_languages=False)
    return (
        list(grants.skill_ids),
        list(grants.tool_tokens),
        list(grants.weapon_tokens),
    )


def build_feat_selection_context(
    stats: StatMap,
    race_id: str,
    subrace_id: str | None,
    background_id: str | None,
    class_id: str,
    subclass_id: str | None,
    level: int,
    *,
    skills: list[str] | None = None,
    weapon_tokens: list[str] | None = None,
    tool_tokens: list[str] | None = None,
) -> FeatRequirementContext:
    """Контекст видимости и требований черт на шаге создания (после класса).

    Опциональные ``skills`` / ``weapon_tokens`` / ``tool_tokens`` дополняют
    владения расы, класса и предыстории (например, от уже выбранных черт).
    """
    from core.character_build import resolve_grants_for_context

    ctx = _creation_context(
        race_id,
        subrace_id,
        background_id,
        class_id,
        subclass_id,
        level,
        skills=skills,
        weapon_tokens=weapon_tokens,
        tool_tokens=tool_tokens,
    )
    grants = resolve_grants_for_context(ctx, include_feat_languages=False)
    return FeatRequirementContext(
        stats=stats,
        weapon_tokens=list(grants.weapon_tokens),
        armor_tokens=list(grants.armor_tokens),
        tool_tokens=list(grants.tool_tokens),
        race_id=race_id,
        subrace_id=subrace_id,
        background_id=background_id,
        class_id=class_id,
        subclass_id=subclass_id,
        level=level,
        has_spellcasting=character_has_spellcasting(
            class_id, subclass_id, level
        ),
        skills=list(grants.skill_ids),
    )


def build_feat_selection_context_from_character(
    character: Any,
) -> FeatRequirementContext:
    """Контекст видимости и требований черт при левелапе."""
    return FeatRequirementContext(
        stats=character.stats,
        weapon_tokens=list(character.weapon_proficiencies),
        armor_tokens=list(character.armor_proficiencies),
        tool_tokens=list(character.tool_proficiencies),
        race_id=character.race,
        subrace_id=character.subrace,
        background_id=getattr(character, "background_id", None),
        class_id=character.class_id,
        subclass_id=character.subclass_id,
        level=character.level + 1,
        has_spellcasting=character_has_spellcasting(
            character.class_id,
            character.subclass_id,
            character.level + 1,
        ),
        skills=list(character.skills),
    )


def _armor_tokens_from_grant(grant: dict[str, Any]) -> list[str]:
    raw = grant.get("armor_types", grant.get("armors", []))
    if not isinstance(raw, list):
        return []
    return [normalize_armor_token(str(armor)) for armor in raw]


def _grant_adds_new_proficiency(
    grant: dict[str, Any], ctx: FeatRequirementContext
) -> bool:
    """Даёт ли grant новое владение относительно контекста."""
    from core.equipment import all_tool_ids, all_weapon_ids
    from core.proficiencies import has_tool_proficiency, has_weapon_proficiency
    from core.skills import PHB_SKILL_IDS

    mtype = str(grant.get("type", ""))
    if mtype not in _PROFICIENCY_GRANT_TYPES:
        return True

    if mtype == "bonus_proficiencies":
        weapons_new = False
        armors_new = False
        raw_w = grant.get("weapons", [])
        if grant.get("choice"):
            weapons_new = any(
                not has_weapon_proficiency(ctx.weapon_tokens, weapon_id)
                for weapon_id in all_weapon_ids()
            )
        elif isinstance(raw_w, list) and raw_w:
            weapons_new = any(
                not has_weapon_proficiency(ctx.weapon_tokens, str(weapon_id))
                for weapon_id in raw_w
            )
        armors = _armor_tokens_from_grant(grant)
        if armors:
            armors_new = any(armor not in ctx.armor_tokens for armor in armors)
        if isinstance(raw_w, list) and raw_w or grant.get("choice"):
            if armors:
                return weapons_new or armors_new
            return weapons_new
        if armors:
            return armors_new
        return True

    if mtype == "armor_proficiency":
        armors = _armor_tokens_from_grant(grant)
        if not armors:
            return True
        return any(armor not in ctx.armor_tokens for armor in armors)

    if mtype == "weapon_proficiency":
        if grant.get("choice"):
            return any(
                not has_weapon_proficiency(ctx.weapon_tokens, weapon_id)
                for weapon_id in all_weapon_ids()
            )
        raw = grant.get("weapons", [])
        if not isinstance(raw, list) or not raw:
            return True
        return any(
            not has_weapon_proficiency(ctx.weapon_tokens, str(weapon_id))
            for weapon_id in raw
        )

    if mtype == "skill_proficiency":
        grant_skills: list[str] = []
        raw = grant.get("skills", [])
        if isinstance(raw, list):
            grant_skills.extend(str(skill) for skill in raw)
        skill_one = grant.get("skill")
        if isinstance(skill_one, str) and skill_one:
            grant_skills.append(skill_one)
        if not grant_skills:
            if grant.get("choice"):
                return any(skill not in ctx.skills for skill in PHB_SKILL_IDS)
            return True
        return any(skill not in ctx.skills for skill in grant_skills)

    if mtype == "tool_proficiency":
        if grant.get("choice"):
            return any(
                not has_tool_proficiency(ctx.tool_tokens, tool_id)
                for tool_id in all_tool_ids()
            )
        raw = grant.get("tools", [])
        if not isinstance(raw, list) or not raw:
            return True
        return any(
            not has_tool_proficiency(ctx.tool_tokens, str(tool_id))
            for tool_id in raw
        )

    if mtype == "multiple_proficiency":
        skill_available = any(
            skill not in ctx.skills for skill in PHB_SKILL_IDS
        )
        tool_available = any(
            not has_tool_proficiency(ctx.tool_tokens, tool_id)
            for tool_id in all_tool_ids()
        )
        return skill_available or tool_available

    return True


def feat_visible_for_selection(
    feat_id: str, ctx: FeatRequirementContext
) -> bool:
    """Показывать ли черту в меню выбора (не скрыта по владениям)."""
    feat = load_feat(feat_id)
    raw_grants = feat.get("grants", [])
    if not isinstance(raw_grants, list) or not raw_grants:
        return True
    return any(
        _grant_adds_new_proficiency(grant, ctx)
        for grant in raw_grants
        if isinstance(grant, dict)
    )


# ============================================================================
# Требования черт
# ============================================================================


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


def _armor_requirement_met(
    required: list[str], armor_tokens: list[str]
) -> bool:
    """Проверка владения доспехом для требования черты."""
    return any(armor in armor_tokens for armor in required)


def _requirement_met(
    req: dict[str, Any],
    ctx: FeatRequirementContext,
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


def active_feat_ids(character: Any) -> list[str]:
    """Черты персонажа, проходящие ongoing-проверку требований."""
    ctx = build_feat_selection_context_from_character(character)
    return [
        feat_id
        for feat_id in character.feat_ids
        if feat_is_active(feat_id, character, ctx=ctx)
    ]


def feat_requirement_context_from_character(
    character: Any,
) -> FeatRequirementContext:
    """Контекст требований черт из персонажа (alias для visibility)."""
    return build_feat_selection_context_from_character(character)


def feat_is_active(
    feat_id: str,
    character: Any,
    *,
    ctx: FeatRequirementContext | None = None,
) -> bool:
    """Активна ли черта с учётом текущих требований."""
    if feat_id not in getattr(character, "feat_ids", []):
        return False
    if ctx is None:
        ctx = feat_requirement_context_from_character(character)
    return feat_meets_requirements(feat_id, ctx)


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


__all__ = [
    # Dataclasses
    "FeatGrant",
    "FeatRequirementContext",
    # Loading
    "load_feat",
    "load_feats",
    # Descriptions
    "feat_full_description_lines",
    "feat_summary_description",
    # Apply
    "apply_feat_grants_to_character",
    "apply_feats_to_stats",
    "get_feat_expertise_ids",
    "get_feat_hp_bonus_sources",
    "get_feat_language_ids",
    "get_feat_proficiency_grants",
    "get_feat_save_proficiencies",
    "get_feat_skill_ids",
    "resolve_feat_ability_bonuses",
    "resolve_feat_grants",
    "tough_hp_adjustment_on_acquire",
    # Visibility
    "build_feat_selection_context",
    "build_feat_selection_context_from_character",
    "creation_known_for_feat_picks",
    "feat_visible_for_selection",
    # Requirements
    "active_feat_ids",
    "can_take_feat",
    "feat_has_requirements",
    "feat_is_active",
    "feat_meets_requirements",
    "feat_requirement_context_from_character",
    "get_race_feat_grants",
    "list_feats_for_selection",
    "race_feat_step_required",
    "requirement_met",
]
