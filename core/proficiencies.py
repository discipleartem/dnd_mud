"""Владения оружием, доспехами и инструментами.

Сбор токенов из grants и проверки владения.
"""

from dataclasses import dataclass
from typing import Any

from core.classes import (
    get_class_dict,
    get_subclass_choice_level,
    get_subclass_dict,
    iter_class_grants,
)
from core.equipment import (
    armor_category,
    resolve_tool_pool,
    tool_category,
    weapon_matches_category,
)
from core.feat_catalog import get_feat_proficiency_grants
from core.grants import (
    mechanics_from_grant_entry,
    normalize_armor_token,
    proficiency_tokens_from_grant,
)
from core.io import merge_unique
from core.models import Character
from core.races import collect_race_grants


@dataclass
class ProficiencyChoice:
    """Выбор владения игроком."""

    count: int
    pool: str
    source: str
    options: list[str] | None = None


# ============================================================================
# Проверки владений
# ============================================================================


def has_weapon_proficiency(proficiencies: list[str], weapon_id: str) -> bool:
    """Владение оружием по токенам."""
    if weapon_id in proficiencies:
        return True
    for token in proficiencies:
        if weapon_matches_category(token, weapon_id):
            return True
    return False


def has_weapon_pool_proficiency(
    pool: str, weapon_proficiencies: list[str]
) -> bool:
    """Владение категорией оружия (simple, martial), не отдельным видом."""
    if pool in weapon_proficiencies:
        return True
    if pool == "martial":
        return any(
            token in weapon_proficiencies
            for token in ("martial_melee", "martial_ranged")
        )
    if pool == "simple":
        return any(
            token in weapon_proficiencies
            for token in ("simple_melee", "simple_ranged")
        )
    return False


def has_armor_proficiency(proficiencies: list[str], armor_id: str) -> bool:
    """Владение доспехом или щитом."""
    cat = armor_category(armor_id)
    if not cat:
        return False
    normalized = normalize_armor_token(cat)
    return normalized in proficiencies or cat in proficiencies


def has_tool_proficiency(proficiencies: list[str], tool_id: str) -> bool:
    """Владение инструментом или категорией."""
    if tool_id in proficiencies:
        return True
    cat = tool_category(tool_id)
    if cat and cat in proficiencies:
        return True
    for token in proficiencies:
        if token in ("artisans_tools", "gaming_sets", "musical_instruments"):
            pool = resolve_tool_pool(token)
            if tool_id in pool:
                return True
    return False


def is_valid_tool_selection(
    selected: list[str], pool: list[str], count: int
) -> bool:
    """Проверить выбор инструментов."""
    if len(selected) != count:
        return False
    if len(set(selected)) != count:
        return False
    pool_set = set(pool)
    return all(t in pool_set for t in selected)


def get_class_saving_throws(class_id: str) -> list[str]:
    """Спасброски класса."""
    info = get_class_dict(class_id)
    if not info:
        return []
    raw = info.get("saving_throws", [])
    if isinstance(raw, list):
        return [str(s) for s in raw]
    return []


def has_save_proficiency(proficiencies: list[str], ability_id: str) -> bool:
    """Владение спасброском по характеристике."""
    return ability_id in proficiencies


def subclass_proficiencies_active(
    class_id: str, subclass_id: str | None, level: int
) -> bool:
    """Подкласс даёт владения на текущем уровне."""
    if not subclass_id:
        return False
    return level >= get_subclass_choice_level(class_id)


# ============================================================================
# Сбор владений из grants
# ============================================================================


def merge_proficiency_tokens(*parts: list[str]) -> list[str]:
    """Объединить списки владений без дублей."""
    return merge_unique(*parts)


def _tokens_from_mechanics(
    mechanics: dict[str, Any],
) -> tuple[list[str], list[str], list[str]]:
    """Из grant/class feature: weapons, armors, tools."""
    return proficiency_tokens_from_grant(mechanics)


def _collect_from_grants(
    grants: list[dict[str, Any]],
    level: int,
    *,
    require_level: bool,
) -> tuple[list[str], list[str], list[str], list[ProficiencyChoice]]:
    """Владения и выборы из grants или class features."""
    weapons: list[str] = []
    armors: list[str] = []
    tools: list[str] = []
    choices: list[ProficiencyChoice] = []
    for entry in grants:
        feat_level = entry.get("level")
        if (
            require_level
            and isinstance(feat_level, int)
            and feat_level > level
        ):
            continue
        merged = mechanics_from_grant_entry(entry)
        w, a, t = _tokens_from_mechanics(merged)
        weapons.extend(w)
        armors.extend(a)
        tools.extend(t)
        if merged.get("choice") and merged.get("type") == "tool_proficiency":
            count = int(merged.get("count", 1))
            pool = str(merged.get("pool", ""))
            raw_opts = merged.get("tools", [])
            options = (
                [str(o) for o in raw_opts]
                if isinstance(raw_opts, list)
                else None
            )
            if pool and not options:
                options = resolve_tool_pool(pool)
            choices.append(
                ProficiencyChoice(
                    count=count,
                    pool=pool or "tools",
                    source="feature",
                    options=options,
                )
            )
    return weapons, armors, tools, choices


def get_class_proficiency_tokens(
    class_id: str,
) -> tuple[list[str], list[str], list[str]]:
    """Базовые владения класса."""
    info = get_class_dict(class_id)
    if not info:
        return [], [], []
    prof = info.get("proficiencies", {})
    if not isinstance(prof, dict):
        return [], [], []
    raw_w = prof.get("weapons", [])
    weapons = [str(w) for w in raw_w] if isinstance(raw_w, list) else []
    raw_a = prof.get("armor", [])
    armors = (
        [normalize_armor_token(str(a)) for a in raw_a]
        if isinstance(raw_a, list)
        else []
    )
    raw_t = prof.get("tools", [])
    tools = [str(t) for t in raw_t] if isinstance(raw_t, list) else []
    return weapons, armors, tools


def get_class_tool_choices(class_id: str) -> list[ProficiencyChoice]:
    """Выборы инструментов класса."""
    info = get_class_dict(class_id)
    if not info:
        return []
    prof = info.get("proficiencies", {})
    if not isinstance(prof, dict):
        return []
    result: list[ProficiencyChoice] = []
    raw = prof.get("tool_choices", [])
    if not isinstance(raw, list):
        return result
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        count = int(entry.get("count", 1))
        pool = str(entry.get("pool", ""))
        result.append(
            ProficiencyChoice(
                count=count,
                pool=pool,
                source="class",
                options=resolve_tool_pool(pool) if pool else None,
            )
        )
    return result


def get_subclass_proficiency_tokens(
    class_id: str,
    subclass_id: str | None,
    level: int,
) -> tuple[list[str], list[str], list[str], list[ProficiencyChoice]]:
    """Владения подкласса с учётом уровня feature."""
    if not subclass_id:
        return [], [], [], []
    sub = get_subclass_dict(class_id, subclass_id)
    if sub is None:
        return [], [], [], []
    return _collect_from_grants(
        iter_class_grants(sub),
        level,
        require_level=True,
    )


def get_racial_proficiency_tokens(
    race_id: str,
    subrace_id: str | None = None,
) -> tuple[list[str], list[str], list[str], list[ProficiencyChoice]]:
    """Расовые владения из grants."""
    grants = collect_race_grants(race_id, subrace_id)
    return _collect_from_grants(grants, level=99, require_level=False)


def get_background_tool_proficiencies(
    background_id: str,
) -> tuple[list[str], list[ProficiencyChoice]]:
    """Инструменты предыстории: fixed + choices."""
    from core.backgrounds import get_background_tool_proficiencies as _bg_tools

    fixed, raw_choices = _bg_tools(background_id)
    choices: list[ProficiencyChoice] = []
    for entry in raw_choices:
        count = int(entry.get("count", 1))
        pool = str(entry.get("pool", ""))
        choices.append(
            ProficiencyChoice(
                count=count,
                pool=pool,
                source="background",
                options=resolve_tool_pool(pool) if pool else None,
            )
        )
    return fixed, choices


def get_feat_proficiency_tokens(
    feat_ids: list[str],
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Владения из черт персонажа."""
    feat_choices = feat_choices or {}
    weapons: list[str] = []
    armors: list[str] = []
    tools: list[str] = []
    for feat_id in feat_ids:
        choices = feat_choices.get(feat_id, {})
        w, a, t, _skills = get_feat_proficiency_grants(feat_id, choices)
        weapons.extend(w)
        armors.extend(a)
        tools.extend(t)
    return weapons, armors, tools


def get_proficiency_choices(
    race_id: str,
    subrace_id: str | None,
    class_id: str,
    background_id: str | None,
    subclass_id: str | None,
    level: int,
) -> list[ProficiencyChoice]:
    """Все выборы владений при создании."""
    choices: list[ProficiencyChoice] = []
    _, _, _, racial_choices = get_racial_proficiency_tokens(
        race_id, subrace_id
    )
    for rc in racial_choices:
        choices.append(
            ProficiencyChoice(
                count=rc.count,
                pool=rc.pool,
                source="race",
                options=rc.options,
            )
        )
    choices.extend(get_class_tool_choices(class_id))
    if background_id:
        _, bg_choices = get_background_tool_proficiencies(background_id)
        choices.extend(bg_choices)
    _, _, _, sub_choices = get_subclass_proficiency_tokens(
        class_id, subclass_id, level
    )
    for sc in sub_choices:
        choices.append(
            ProficiencyChoice(
                count=sc.count,
                pool=sc.pool,
                source="subclass",
                options=sc.options,
            )
        )
    return choices


def build_fixed_proficiencies(
    race_id: str,
    subrace_id: str | None,
    class_id: str,
    background_id: str | None,
    subclass_id: str | None,
    level: int,
    feat_ids: list[str] | None = None,
    feat_choices: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[str], list[str], list[str]]:
    """Собрать фиксированные владения без игровых выборов."""
    from core.grants_resolve import (
        build_fixed_proficiencies as _build_fixed,
    )

    return _build_fixed(
        race_id,
        subrace_id,
        class_id,
        background_id,
        subclass_id,
        level,
        feat_ids=feat_ids,
        feat_choices=feat_choices,
    )


def apply_subclass_proficiencies_to_character(
    character: Character,
    subclass_id: str,
) -> list[ProficiencyChoice]:
    """Добавить владения подкласса. Возвращает невыполненные выборы."""
    sw, sa, st, choices = get_subclass_proficiency_tokens(
        character.class_id, subclass_id, character.level
    )
    character.weapon_proficiencies = merge_proficiency_tokens(
        character.weapon_proficiencies, sw
    )
    character.armor_proficiencies = merge_proficiency_tokens(
        character.armor_proficiencies, sa
    )
    character.tool_proficiencies = merge_proficiency_tokens(
        character.tool_proficiencies, st
    )
    return choices


__all__ = [
    "ProficiencyChoice",
    "merge_proficiency_tokens",
    # Checks
    "has_weapon_proficiency",
    "has_weapon_pool_proficiency",
    "has_armor_proficiency",
    "has_tool_proficiency",
    "is_valid_tool_selection",
    "get_class_saving_throws",
    "has_save_proficiency",
    "subclass_proficiencies_active",
    # Collect
    "get_class_proficiency_tokens",
    "get_class_tool_choices",
    "get_subclass_proficiency_tokens",
    "get_racial_proficiency_tokens",
    "get_background_tool_proficiencies",
    "get_feat_proficiency_tokens",
    "get_proficiency_choices",
    "build_fixed_proficiencies",
    "apply_subclass_proficiencies_to_character",
]
