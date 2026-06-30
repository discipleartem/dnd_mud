"""Отображение рас и расовых бонусов."""

from typing import Any

from colorama import Fore, Style

from core.equipment import (
    get_tool_name,
    get_weapon_name,
    proficiency_token_label,
)
from core.grant_mechanics import _normalize_armor_token
from core.grants import grants_from_entity, grants_of_type
from core.localization import get_string
from core.types import StatMap, StringsDict
from ui.menus import _deps
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
    tokens = [_normalize_armor_token(str(item)) for item in raw]
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
    """Краткое описание grant для экрана расы."""
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


def _print_race_grants(
    info: dict[str, Any], strings: StringsDict, language: str = "ru"
) -> None:
    """Вывести особенности из grants[] (после миграции YAML)."""
    grants = grants_from_entity(info)
    if not grants:
        return
    print(get_string(strings, "character.features_label"))
    for grant in grants:
        name = _grant_display_name(grant, strings)
        desc = _grant_description(grant, strings, language)
        print(
            get_string(
                strings,
                "character.feature_line",
                name=name,
                desc=desc,
            )
        )


def _print_choice_ability_from_grants(
    info: dict[str, Any], strings: StringsDict
) -> None:
    """Выборный бонус характеристик из grants, если нет ability_bonuses."""
    for grant in grants_of_type(grants_from_entity(info), _ABILITY_INCREASE):
        if not grant.get("choice"):
            continue
        count = int(grant.get("count", 1))
        amount = int(grant.get("amount", grant.get("value", 1)))
        choice_info = get_string(
            strings,
            "character.stats_choice_bonus_subrace_info",
            count=count,
            value=amount,
        )
        print(
            get_string(
                strings,
                "character.ability_bonuses_label",
                bonuses=choice_info,
            )
        )
        return


def _print_race_info(
    info: StringsDict, strings: StringsDict, language: str = "ru"
) -> None:
    """Вывести подробности расы или подрасы."""
    desc = info.get("description", "")
    if desc:
        print(get_string(strings, "character.race_description", desc=desc))

    speed = info.get("speed")
    if speed:
        print(get_string(strings, "character.speed_label", speed=speed))

    languages = info.get("languages", [])
    if languages:
        language_line = ", ".join(
            _deps.get_language_name(str(lang), language) for lang in languages
        )
        print(
            get_string(
                strings, "character.languages_label", langs=language_line
            )
        )

    bonuses = info.get("ability_bonuses", {})
    if bonuses:
        bonus_parts = []
        for stat, val in bonuses.items():
            stat_label = _ability_name(strings, stat)
            bonus_parts.append(
                f"{Fore.CYAN}{stat_label}{Style.RESET_ALL}"
                f"+{Fore.GREEN}{val}{Style.RESET_ALL}"
            )
        bonuses_str = ", ".join(bonus_parts)
        print(
            get_string(
                strings, "character.ability_bonuses_label", bonuses=bonuses_str
            )
        )
    else:
        _print_choice_ability_from_grants(info, strings)

    _print_race_grants(info, strings, language)


def _format_bonuses(bonuses: StatMap, strings: StringsDict) -> str:
    """Отформатировать расовые бонусы для отображения."""
    if not bonuses:
        return (
            f"{Fore.CYAN}"
            f"{get_string(strings, 'character.stats_no_bonuses')}"
            f"{Style.RESET_ALL}"
        )

    bonus_strs = []
    for stat, bonus in bonuses.items():
        stat_name = _ability_name(strings, stat)
        bonus_strs.append(
            get_string(
                strings,
                "character.stats_bonus_format",
                stat=stat_name,
                bonus=bonus,
            )
        )

    bonus_line = ", ".join(bonus_strs)
    race_msg = get_string(
        strings, "character.stats_race_bonuses", bonuses=bonus_line
    )
    return f"{Fore.CYAN}{race_msg}{Style.RESET_ALL}"


def _print_race_bonuses(
    strings: StringsDict,
    race_id: str,
    subrace_id: str | None,
) -> None:
    """Вывести блок расовых бонусов."""
    bonuses = _deps.get_race_bonuses(race_id, subrace_id)
    if bonuses:
        print(_format_bonuses(bonuses, strings))
        return

    mechanics = _deps.get_choice_ability_bonus_mechanics(race_id, subrace_id)
    if mechanics:
        count = int(mechanics.get("count", 1))
        value = int(mechanics.get("value", 1))
        pending_msg = get_string(
            strings,
            "character.stats_choice_bonus_pending",
            count=count,
            value=value,
        )
        print(f"{Fore.CYAN}{pending_msg}{Style.RESET_ALL}")
        return

    print(_format_bonuses(bonuses, strings))
