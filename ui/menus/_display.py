"""Отображение карточек персонажей, рас и характеристик."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from core.models import Character
from ui.menus import _deps
from ui.menus._common import SEPARATOR, _ability_name, _stats_caption_line


def _difficulty_label(strings: dict[str, Any], difficulty: str) -> str:
    """Локализованное название режима сложности."""
    mode_key = f"difficulty.{difficulty}"
    mode = get_string(strings, mode_key)
    if mode == mode_key:
        return difficulty
    return mode


def _difficulty_color(difficulty: str) -> str:
    """Цвет для отображения режима сложности."""
    if difficulty == "hardcore":
        return str(Fore.RED)
    if difficulty == "normal":
        return str(Fore.GREEN)
    return str(Fore.CYAN)


def _character_base_race_label(char: Character, language: str = "ru") -> str:
    """Читаемое название базовой расы персонажа."""
    race_full = _deps.load_race_full(char.race, language)
    name = race_full.get("name")
    if name:
        return str(name)
    return char.race


def _character_subrace_label(
    char: Character, language: str = "ru"
) -> str | None:
    """Читаемое название подрасы или None, если подрасы нет."""
    if not char.subrace:
        return None

    race_full = _deps.load_race_full(char.race, language)
    subraces = race_full.get("subraces", {})
    if isinstance(subraces, dict):
        subrace_info = subraces.get(char.subrace, {})
        if isinstance(subrace_info, dict):
            name = subrace_info.get("name")
            if name:
                name_str = str(name)
                if "(" in name_str and name_str.endswith(")"):
                    return name_str.split("(", maxsplit=1)[1].rstrip(")")
                return name_str
    return char.subrace


def _print_labeled_field(
    strings: dict[str, Any],
    label_key: str,
    value: str,
    indent: str = "     ",
) -> None:
    """Вывести строку «подпись: значение» с цветной подписью."""
    label = get_string(strings, label_key)
    print(
        f"{indent}" f"{Fore.LIGHTBLACK_EX}{label}{Style.RESET_ALL} " f"{value}"
    )


def _character_class_label(char: Character, language: str = "ru") -> str:
    """Читаемое название класса персонажа."""
    for cls in _deps.load_classes(language):
        if cls.get("id") == char.class_name:
            return str(cls.get("name", char.class_name))
    return char.class_name


def _format_character_stats_compact(
    char: Character, strings: dict[str, Any]
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


def _print_characters_list(
    strings: dict[str, Any],
    characters: list[Character],
    language: str,
) -> None:
    """Вывести список сохранённых персонажей."""
    print(
        f"  {Fore.YELLOW}{Style.BRIGHT}"
        f"{get_string(strings, 'choose_character.list_header')}"
        f"{Style.RESET_ALL}"
    )
    print()
    for idx, char in enumerate(characters, 1):
        _print_character_card(idx, char, strings, language)


def _print_character_card(
    idx: int,
    char: Character,
    strings: dict[str, Any],
    language: str = "ru",
) -> None:
    """Вывести карточку персонажа в списке выбора."""
    mode = _difficulty_label(strings, char.difficulty)
    mode_color = _difficulty_color(char.difficulty)
    base_race = _character_base_race_label(char, language)
    subrace = _character_subrace_label(char, language)
    class_label = _character_class_label(char, language)
    indent = "     "

    print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}.")

    _print_labeled_field(
        strings,
        "choose_character.field_name",
        f"{Fore.CYAN}{Style.BRIGHT}{char.name}{Style.RESET_ALL}",
        indent=indent,
    )
    _print_labeled_field(
        strings,
        "choose_character.field_race",
        f"{Fore.CYAN}{base_race}{Style.RESET_ALL}",
        indent=indent,
    )
    if subrace:
        _print_labeled_field(
            strings,
            "choose_character.field_subrace",
            f"{Fore.CYAN}{subrace}{Style.RESET_ALL}",
            indent=indent,
        )
    _print_labeled_field(
        strings,
        "choose_character.field_class",
        f"{Fore.CYAN}{class_label}{Style.RESET_ALL}",
        indent=indent,
    )
    _print_labeled_field(
        strings,
        "choose_character.field_level",
        f"{Fore.YELLOW}{char.level}{Style.RESET_ALL}",
        indent=indent,
    )

    vitals_line = get_string(
        strings,
        "choose_character.vitals_line",
        hp=f"{Fore.GREEN}{char.current_hp}{Style.RESET_ALL}",
        xp=f"{Fore.MAGENTA}{char.experience}{Style.RESET_ALL}",
    )
    print(f"{indent}{vitals_line}")

    stats_compact = _format_character_stats_compact(char, strings)
    if stats_compact:
        stats_line = get_string(
            strings, "choose_character.stats_line", stats=stats_compact
        )
        print(f"{indent}{stats_line}")

    _print_labeled_field(
        strings,
        "choose_character.field_difficulty",
        f"{mode_color}{mode}{Style.RESET_ALL}",
        indent=indent,
    )

    print()


def _print_race_info(info: dict[str, Any], strings: dict[str, Any]) -> None:
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


def _format_bonuses(bonuses: dict[str, int], strings: dict[str, Any]) -> str:
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
    strings: dict[str, Any],
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


def _print_final_stat_line(
    strings: dict[str, Any],
    stat: str,
    value: int,
    race_bonuses: dict[str, int],
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
    strings: dict[str, Any],
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


def _print_point_buy_cost_table(strings: dict[str, Any]) -> None:
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
