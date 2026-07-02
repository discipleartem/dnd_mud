"""Отображение рас и расовых бонусов."""

from typing import Any

from colorama import Fore, Style

from core.grants import ABILITY_INCREASE, grants_from_entity, grants_of_type
from core.localization import get_string
from core.types import StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import _ability_name
from ui.menus._display._grants import _print_grant_line
from ui.menus._display._labels import _grant_pool_label


def _has_choice_ability_bonuses(info: dict[str, Any]) -> bool:
    """Есть ли выборный бонус характеристик в grants без ability_bonuses."""
    if info.get("ability_bonuses"):
        return False
    for grant in grants_of_type(grants_from_entity(info), ABILITY_INCREASE):
        if grant.get("choice"):
            return True
    return False


def _choice_language_grants(
    grants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Выборные языковые grants из списка."""
    return [
        grant
        for grant in grants_of_type(grants, "language")
        if grant.get("choice")
    ]


def _format_language_choice_extra(
    strings: StringsDict, grant: dict[str, Any]
) -> str:
    """Краткая подпись выборного языка для строки «Языки»."""
    count = int(grant.get("count", 1))
    pool = str(grant.get("pool", grant.get("from", "common")))
    pool_label = _grant_pool_label(strings, pool, gtype="language")
    return get_string(
        strings,
        "character.language_race_extra",
        count=count,
        pool=pool_label,
    )


def _print_race_grants(
    info: dict[str, Any],
    strings: StringsDict,
    language: str = "ru",
    *,
    omit_choice_languages: bool = False,
) -> None:
    """Вывести особенности из grants[] сущности (без наследования от расы)."""
    grants = grants_from_entity(info)
    visible: list[dict[str, Any]] = []
    for grant in grants:
        if (
            omit_choice_languages
            and grant.get("type") == "language"
            and grant.get("choice")
        ):
            continue
        if (
            _has_choice_ability_bonuses(info)
            and grant.get("type") == ABILITY_INCREASE
            and grant.get("choice")
        ):
            continue
        visible.append(grant)
    if not visible:
        return
    print(get_string(strings, "character.features_label"))
    for grant in visible:
        _print_grant_line(grant, strings, language)


def _print_choice_ability_from_grants(
    info: dict[str, Any], strings: StringsDict
) -> None:
    """Выборный бонус характеристик из grants, если нет ability_bonuses."""
    for grant in grants_of_type(grants_from_entity(info), ABILITY_INCREASE):
        if not grant.get("choice"):
            continue
        count = int(grant.get("count", 1))
        amount = int(grant.get("amount", 1))
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
    info: dict[str, Any],
    strings: StringsDict,
    language: str = "ru",
) -> None:
    """Вывести подробности расы или подрасы."""
    desc = info.get("description", "")
    if desc:
        print(get_string(strings, "character.race_description", desc=desc))

    speed = info.get("speed")
    if speed:
        print(get_string(strings, "character.speed_label", speed=speed))

    entity_grants = grants_from_entity(info)
    choice_languages = _choice_language_grants(entity_grants)
    fixed_languages = info.get("languages", [])
    lang_parts: list[str] = []
    if isinstance(fixed_languages, list):
        lang_parts.extend(
            _deps.get_language_name(str(lang), language)
            for lang in fixed_languages
        )
    merge_choice_into_languages = bool(fixed_languages and choice_languages)
    if merge_choice_into_languages:
        for grant in choice_languages:
            lang_parts.append(_format_language_choice_extra(strings, grant))
    if lang_parts:
        print(
            get_string(
                strings,
                "character.languages_label",
                langs=", ".join(lang_parts),
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

    _print_race_grants(
        info,
        strings,
        language,
        omit_choice_languages=merge_choice_into_languages,
    )


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
        value = int(mechanics.get("amount", 1))
        pending_msg = get_string(
            strings,
            "character.stats_choice_bonus_pending",
            count=count,
            value=value,
        )
        print(f"{Fore.CYAN}{pending_msg}{Style.RESET_ALL}")
        return

    print(_format_bonuses(bonuses, strings))
