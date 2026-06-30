"""Отображение рас и расовых бонусов."""

from typing import Any

from colorama import Fore, Style

from core.grants import grants_from_entity, grants_of_type
from core.localization import get_string
from core.types import StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import _ability_name

_ABILITY_INCREASE = "ability_increase"


def _grant_description(grant: dict[str, Any], strings: StringsDict) -> str:
    """Краткое описание grant для экрана расы."""
    gtype = str(grant.get("type", ""))
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
        pool = grant.get("pool", grant.get("from", ""))
        if pool:
            return get_string(
                strings,
                "character.grant_choice_pool",
                count=count,
                pool=pool,
                default=f"выбор: {count} из {pool}",
            )
        return get_string(
            strings,
            "character.grant_choice",
            count=count,
            default=f"на выбор: {count}",
        )
    weapons = grant.get("weapons", [])
    if isinstance(weapons, list) and weapons:
        return ", ".join(str(w) for w in weapons)
    skills = grant.get("skills", grant.get("skill"))
    if isinstance(skills, list) and skills:
        return ", ".join(str(s) for s in skills)
    if isinstance(skills, str) and skills:
        return skills
    range_ft = grant.get("range")
    if gtype == "darkvision" and range_ft is not None:
        return get_string(
            strings,
            "character.grant_darkvision",
            range=range_ft,
            default=f"{range_ft} фт.",
        )
    return str(grant.get("description", ""))


def _print_race_grants(info: dict[str, Any], strings: StringsDict) -> None:
    """Вывести особенности из grants[] (после миграции YAML)."""
    grants = grants_from_entity(info)
    if not grants:
        return
    print(get_string(strings, "character.features_label"))
    for grant in grants:
        name = str(grant.get("name", grant.get("type", "")))
        desc = _grant_description(grant, strings)
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


def _print_race_info(info: StringsDict, strings: StringsDict) -> None:
    """Вывести подробности расы или подрасы."""
    desc = info.get("description", "")
    if desc:
        print(get_string(strings, "character.race_description", desc=desc))

    speed = info.get("speed")
    if speed:
        print(get_string(strings, "character.speed_label", speed=speed))

    languages = info.get("languages", [])
    if languages:
        language_line = ", ".join(str(lang) for lang in languages)
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

    _print_race_grants(info, strings)


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
