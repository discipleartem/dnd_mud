"""Отображение карточек персонажей."""

from colorama import Fore, Style

from core.classes import get_subclass_choice_level
from core.equipment import proficiency_token_label
from core.localization import get_string
from core.models import Character
from core.subclasses import subclass_is_active
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import _skill_name
from ui.menus._display._class import (
    _character_class_label,
    _character_subclass_label,
)
from ui.menus._display._difficulty import _difficulty_color, _difficulty_label
from ui.menus._display._stats import _format_character_stats_compact
from ui.menus.expertise import format_expertise_display


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


def _empty_field_value(strings: StringsDict) -> str:
    """Плейсхолдер для пустого поля карточки персонажа."""
    empty = get_string(strings, "choose_character.field_empty")
    return f"{Fore.LIGHTBLACK_EX}{empty}{Style.RESET_ALL}"


def _print_labeled_field(
    strings: StringsDict,
    label_key: str,
    value: str,
    indent: str = "     ",
) -> None:
    """Вывести строку «подпись: значение» с цветной подписью."""
    label = get_string(strings, label_key)
    print(
        f"{indent}" f"{Fore.LIGHTBLACK_EX}{label}{Style.RESET_ALL} " f"{value}"
    )


def _format_proficiency_token_list(
    strings: StringsDict,
    tokens: list[str],
    *,
    language: str = "ru",
) -> str:
    """Локализованный список токенов владений."""
    names = [proficiency_token_label(t, strings, language) for t in tokens]
    return ", ".join(names)


def _print_character_proficiencies(
    char: Character,
    strings: StringsDict,
    language: str,
    *,
    indent: str = "     ",
) -> None:
    """Владения персонажа: заголовок и категории с отступом."""
    categories: tuple[tuple[list[str], str], ...] = (
        (
            char.armor_proficiencies,
            "choose_character.field_proficiencies_armor",
        ),
        (
            char.weapon_proficiencies,
            "choose_character.field_proficiencies_weapons",
        ),
        (
            char.tool_proficiencies,
            "choose_character.field_proficiencies_tools",
        ),
    )
    has_any = any(tokens for tokens, _ in categories)
    if not has_any:
        _print_labeled_field(
            strings,
            "choose_character.field_proficiencies",
            _empty_field_value(strings),
            indent=indent,
        )
        return

    header = get_string(strings, "choose_character.field_proficiencies")
    print(f"{indent}{Fore.LIGHTBLACK_EX}{header}{Style.RESET_ALL}")
    sub_indent = f"{indent}  "
    for tokens, label_key in categories:
        if not tokens:
            continue
        value = _format_proficiency_token_list(
            strings,
            tokens,
            language=language,
        )
        cat_label = get_string(strings, label_key)
        print(
            f"{sub_indent}{Fore.LIGHTBLACK_EX}{cat_label}{Style.RESET_ALL} "
            f"{Fore.CYAN}{value}{Style.RESET_ALL}"
        )


def _print_character_card(
    idx: int,
    char: Character,
    strings: StringsDict,
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
    if char.languages:
        lang_line = ", ".join(
            _deps.get_language_name(lang_id, language)
            for lang_id in char.languages
        )
        lang_display = f"{Fore.CYAN}{lang_line}{Style.RESET_ALL}"
    else:
        lang_display = _empty_field_value(strings)
    _print_labeled_field(
        strings,
        "choose_character.field_languages",
        lang_display,
        indent=indent,
    )
    if char.background_id:
        bg = _deps.load_background_full(char.background_id, language)
        bg_name = bg.get("name", char.background_id)
        bg_display = f"{Fore.CYAN}{bg_name}{Style.RESET_ALL}"
    else:
        bg_display = _empty_field_value(strings)
    _print_labeled_field(
        strings,
        "choose_character.field_background",
        bg_display,
        indent=indent,
    )
    _print_labeled_field(
        strings,
        "choose_character.field_class",
        f"{Fore.CYAN}{class_label}{Style.RESET_ALL}",
        indent=indent,
    )
    subclass_label = _character_subclass_label(char, language)
    if subclass_label:
        display = f"{Fore.CYAN}{subclass_label}{Style.RESET_ALL}"
        if char.subclass_id and not subclass_is_active(char):
            choice_level = get_subclass_choice_level(char.class_id)
            pending = get_string(
                strings,
                "choose_character.subclass_pending_level",
                level=choice_level,
            )
            display = (
                f"{display} {Fore.LIGHTBLACK_EX}{pending}{Style.RESET_ALL}"
            )
        _print_labeled_field(
            strings,
            "choose_character.field_subclass",
            display,
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

    if char.skills:
        skills_line = ", ".join(
            _skill_name(strings, skill_id) for skill_id in char.skills
        )
        skills_display = f"{Fore.CYAN}{skills_line}{Style.RESET_ALL}"
    else:
        skills_display = _empty_field_value(strings)
    _print_labeled_field(
        strings,
        "choose_character.field_skills",
        skills_display,
        indent=indent,
    )

    expertise_line = format_expertise_display(
        strings, char.skill_expertise, char.tool_expertise
    )
    expertise_display = (
        f"{Fore.CYAN}{expertise_line}{Style.RESET_ALL}"
        if expertise_line
        else _empty_field_value(strings)
    )
    _print_labeled_field(
        strings,
        "choose_character.field_expertise",
        expertise_display,
        indent=indent,
    )

    _print_character_proficiencies(char, strings, language, indent=indent)

    _print_labeled_field(
        strings,
        "choose_character.field_difficulty",
        f"{mode_color}{mode}{Style.RESET_ALL}",
        indent=indent,
    )

    print()


def _print_characters_list(
    strings: StringsDict,
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
