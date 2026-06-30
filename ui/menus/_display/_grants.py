"""Локализованное отображение grants[] на экранах расы и предыстории."""

from typing import Any

from core.equipment import (
    get_tool_name,
    get_weapon_name,
    proficiency_token_label,
)
from core.grant_mechanics import normalize_armor_token
from core.localization import get_string
from core.types import StringsDict
from ui.menus._common import _ability_name, _skill_name
from ui.menus._display._labels import (
    _grant_pool_label,
    _grant_type_label,
)

_ABILITY_INCREASE = "ability_increase"


def _armor_labels_from_grant(
    grant: dict[str, Any], strings: StringsDict, language: str
) -> str:
    """Локализованные подписи типов доспехов из grant."""
    raw = grant.get("armor_types", grant.get("armors", []))
    if not isinstance(raw, list) or not raw:
        return ""
    tokens = [normalize_armor_token(str(item)) for item in raw]
    return ", ".join(
        proficiency_token_label(token, strings, language) for token in tokens
    )


def _damage_type_labels(strings: StringsDict, types: list[Any]) -> str:
    """Локализованные подписи типов урона."""
    labels: list[str] = []
    for item in types:
        token = str(item)
        labels.append(
            get_string(
                strings, f"character.grant_damage_{token}", default=token
            )
        )
    return ", ".join(labels)


def _grant_display_name(grant: dict[str, Any], strings: StringsDict) -> str:
    """Имя особенности: name из YAML или локализованный type."""
    name = str(grant.get("name", "")).strip()
    if name:
        return name
    return _grant_type_label(strings, str(grant.get("type", "")))


def _grant_description(
    grant: dict[str, Any],
    strings: StringsDict,
    language: str = "ru",
) -> str:
    """Краткое описание grant для экрана расы или предыстории."""
    gtype = str(grant.get("type", ""))
    explicit = str(grant.get("description", "")).strip()
    if explicit:
        return explicit
    if gtype == "hit_point_bonus" and grant.get("per_level"):
        amount = int(grant.get("value", grant.get("amount", 0)))
        if amount > 0:
            return get_string(
                strings,
                "character.grant_hp_per_level",
                amount=amount,
            )
    if gtype == _ABILITY_INCREASE and grant.get("choice"):
        count = int(grant.get("count", 1))
        amount = int(grant.get("amount", grant.get("value", 1)))
        return get_string(
            strings,
            "character.stats_choice_bonus_subrace_info",
            count=count,
            value=amount,
        )
    if grant.get("choice"):
        count = int(grant.get("count", 1))
        tools = grant.get("tools", [])
        if gtype == "tool_proficiency" and isinstance(tools, list) and tools:
            tool_labels = ", ".join(
                get_tool_name(str(tool_id), language) for tool_id in tools
            )
            return get_string(
                strings,
                "character.grant_choice_tools",
                count=count,
                tools=tool_labels,
            )
        pool = str(grant.get("pool", grant.get("from", "")))
        if pool:
            pool_label = _grant_pool_label(strings, pool, gtype=gtype)
            return get_string(
                strings,
                "character.grant_choice_pool",
                count=count,
                pool=pool_label,
            )
        return get_string(
            strings,
            "character.grant_choice",
            count=count,
        )
    if gtype == "tool_proficiency":
        raw_tools = grant.get("tools", [])
        if isinstance(raw_tools, list) and raw_tools:
            return ", ".join(
                get_tool_name(str(tool_id), language) for tool_id in raw_tools
            )
    weapons = grant.get("weapons", [])
    if isinstance(weapons, list) and weapons:
        return ", ".join(get_weapon_name(str(w), language) for w in weapons)
    if gtype == "skill_bonus" and grant.get("expertise"):
        skill = grant.get("skill")
        if isinstance(skill, str) and skill:
            return get_string(
                strings,
                "character.grant_skill_expertise",
                skill=_skill_name(strings, skill),
            )
    skills = grant.get("skills", grant.get("skill"))
    if isinstance(skills, list) and skills:
        return ", ".join(_skill_name(strings, str(s)) for s in skills)
    if isinstance(skills, str) and skills:
        return _skill_name(strings, skills)
    if gtype == "armor_proficiency":
        armor_labels = _armor_labels_from_grant(grant, strings, language)
        if armor_labels:
            return armor_labels
    if gtype == "speed_ignore_penalty":
        armor_labels = _armor_labels_from_grant(grant, strings, language)
        if armor_labels:
            return get_string(
                strings,
                "character.grant_speed_ignore",
                armors=armor_labels,
            )
    if gtype == "resistance":
        damage_types = grant.get("damage_types", [])
        advantage_saves = grant.get("advantage_saves", [])
        dmg_labels = (
            _damage_type_labels(strings, damage_types)
            if isinstance(damage_types, list)
            else ""
        )
        save_labels = (
            _damage_type_labels(strings, advantage_saves)
            if isinstance(advantage_saves, list)
            else ""
        )
        if save_labels and dmg_labels:
            return get_string(
                strings,
                "character.grant_resistance_full",
                saves=save_labels,
                types=dmg_labels,
            )
        if dmg_labels:
            return get_string(
                strings,
                "character.grant_resistance",
                types=dmg_labels,
            )
        if save_labels:
            return get_string(
                strings,
                "character.grant_advantage_saves",
                types=save_labels,
            )
    if gtype == "speed_bonus":
        speed = grant.get("value", grant.get("amount"))
        if speed is not None:
            return get_string(
                strings,
                "character.grant_speed_value",
                speed=speed,
            )
    if gtype == "advantage" and grant.get("save") and grant.get("effect"):
        effect_key = str(grant["effect"])
        effect_label = get_string(
            strings,
            f"character.grant_effect_{effect_key}",
            default=effect_key,
        )
        return get_string(
            strings,
            "character.grant_advantage_save",
            save=_ability_name(strings, str(grant["save"])),
            effect=effect_label,
        )
    if gtype == "rest" and grant.get("duration") is not None:
        return get_string(
            strings,
            "character.grant_rest_trance",
            duration=int(grant["duration"]),
        )
    range_ft = grant.get("range")
    if gtype == "darkvision" and range_ft is not None:
        return get_string(
            strings,
            "character.grant_darkvision",
            range=range_ft,
        )
    return ""
