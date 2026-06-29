"""Отображение характеристик при генерации."""

from colorama import Fore, Style

from core.localization import get_string
from core.models import Character
from core.types import StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import SEPARATOR, _ability_name, _stats_caption_line
from ui.menus._display._race import _print_race_bonuses


def _format_character_stats_compact(
    char: Character, strings: StringsDict
) -> str:
    """Компактная строка характеристик: аббревиатура + значение."""
    if not char.stats:
        return ""

    parts = []
    for stat in _deps.STAT_NAMES:
        value = char.stats.get(stat)
        if value is None:
            continue
        abbr = _ability_name(strings, stat)[:3]
        parts.append(
            f"{Fore.CYAN}{abbr}{Style.RESET_ALL} "
            f"{Fore.YELLOW}{value:>2}{Style.RESET_ALL}"
        )
    return "  ".join(parts)


def _print_final_stat_line(
    strings: StringsDict,
    stat: str,
    value: int,
    race_bonuses: StatMap,
) -> None:
    """Вывести итоговую характеристику с пометкой расового бонуса (+N)."""
    stat_name = _ability_name(strings, stat)
    bonus = race_bonuses.get(stat, 0)
    if bonus > 0:
        print(
            f"  {stat_name}: {Fore.YELLOW}{value}{Style.RESET_ALL} "
            f"{Fore.GREEN}(+{bonus}){Style.RESET_ALL}"
        )
        return
    print(f"  {stat_name}: {Fore.YELLOW}{value}{Style.RESET_ALL}")


def _print_stats_generation_header(
    strings: StringsDict,
    race_id: str | None = None,
    subrace_id: str | None = None,
) -> None:
    """Заголовок генерации характеристик и расовые бонусы."""
    print(SEPARATOR)
    print(_stats_caption_line(strings))
    print(SEPARATOR)
    print()
    if race_id is not None:
        _print_race_bonuses(strings, race_id, subrace_id)
        print()


def _print_point_buy_cost_table(strings: StringsDict) -> None:
    """Таблица стоимости значений характеристик (point-buy)."""
    title = get_string(strings, "character.stats_point_buy_price_table")
    value_hdr = get_string(strings, "character.stats_point_buy_price_value")
    cost_hdr = get_string(strings, "character.stats_point_buy_price_cost")
    print(f"{Fore.GREEN}{title}{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}{value_hdr:>5}  {cost_hdr:>5}{Style.RESET_ALL}")
    for value in sorted(_deps.POINT_BUY_COSTS):
        cost = _deps.POINT_BUY_COSTS[value]
        print(
            f"  {Fore.CYAN}{value:>5}{Style.RESET_ALL}  "
            f"{Fore.CYAN}{cost:>5}{Style.RESET_ALL}"
        )
    print()
