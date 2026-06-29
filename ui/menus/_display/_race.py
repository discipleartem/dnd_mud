"""Отображение рас и расовых бонусов."""

from colorama import Fore, Style

from core.localization import get_string
from core.types import StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import _ability_name


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
        for feat in info.get("features", []):
            if not isinstance(feat, dict):
                continue
            if feat.get("type") != "ability_bonus":
                continue
            mechanics = feat.get("mechanics", {})
            if isinstance(mechanics, dict) and mechanics.get("choice"):
                count = int(mechanics.get("count", 1))
                value = int(mechanics.get("value", 1))
                choice_info = get_string(
                    strings,
                    "character.stats_choice_bonus_subrace_info",
                    count=count,
                    value=value,
                )
                print(
                    get_string(
                        strings,
                        "character.ability_bonuses_label",
                        bonuses=choice_info,
                    )
                )
                break

    features = info.get("features", [])
    if features:
        print(get_string(strings, "character.features_label"))
        for feat in features:
            description = feat.get("description", "")
            print(
                get_string(
                    strings,
                    "character.feature_line",
                    name=feat.get("name", ""),
                    desc=description,
                )
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
