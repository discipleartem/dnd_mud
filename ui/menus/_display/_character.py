"""Отображение карточек персонажей."""

from colorama import Fore, Style

from core.classes import get_subclass_choice_level
from core.localization import get_string
from core.models import Character
from core.progression.subclasses import subclass_is_active
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._display._character_header import (
    _character_base_race_label,
    _character_subrace_label,
    _empty_field_value,
    _format_character_feats,
    _print_labeled_field,
)
from ui.menus._display._character_sections import (
    _print_character_equipment,
    _print_character_proficiencies,
    _print_character_saving_throws,
    _print_character_skills_and_expertise,
)
from ui.menus._display._class import (
    _character_class_label,
    _character_subclass_label,
)
from ui.menus._display._difficulty import _difficulty_color, _difficulty_label
from ui.menus._display._stats import _format_character_stats_compact


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
    if char.feat_ids:
        feats_text = _format_character_feats(char, language)
        feats_display = f"{Fore.CYAN}{feats_text}{Style.RESET_ALL}"
        _print_labeled_field(
            strings,
            "choose_character.field_feats",
            feats_display,
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

    _print_character_skills_and_expertise(char, strings, indent=indent)

    _print_character_proficiencies(char, strings, language, indent=indent)

    _print_character_saving_throws(char, strings, indent=indent)

    _print_character_equipment(char, strings, language, indent=indent)

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
