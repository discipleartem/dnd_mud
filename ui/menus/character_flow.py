"""Flow «Создать персонажа»: имя, раса, подраса, класс."""

from typing import Any

from colorama import Fore, Style

from core.localization import get_string
from core.models import Character
from ui.menus import _deps
from ui.menus._common import _press_enter, _print_screen_header
from ui.menus._display import _print_race_info
from ui.menus.settings import select_difficulty
from ui.menus.stats_flow import show_stats_generation_flow


def _select_subrace(
    strings: dict[str, Any], race_id: str, language: str = "ru"
) -> tuple[bool, str | None]:
    """Показать описание расы и выбрать подрасу."""
    race_full = _deps.load_race_full(race_id, language)
    subraces = race_full.get("subraces", {})
    allow_base = bool(race_full.get("allow_base_race_choice", False))

    _print_screen_header(get_string(strings, "character.subrace_caption"))

    race_name = race_full.get("name", race_id)
    print(f"{Fore.CYAN}{race_name}{Style.RESET_ALL}")
    _print_race_info(race_full, strings)
    print()

    if not subraces:
        if allow_base:
            print(get_string(strings, "character.no_subraces"))
            print()
            print(
                f"  {Fore.YELLOW}1{Style.RESET_ALL}. "
                f"{Fore.CYAN}{race_name}{Style.RESET_ALL}"
            )
            print(
                f"  {Fore.YELLOW}0{Style.RESET_ALL}."
                f" {get_string(strings, 'character.back')}"
            )
            print()
            choice = _deps.get_int_input(
                get_string(strings, "character.subrace_prompt"),
                0,
                1,
                strings,
            )
            if choice == 0:
                return False, None
            return True, None
        return False, None

    print(get_string(strings, "character.subraces_label"))
    choices: list[tuple[str | None, dict[str, Any]]] = []
    if allow_base:
        base_info = dict(race_full)
        base_info["name"] = race_full.get("base_choice_name", race_name)
        choices.append((None, base_info))

    for subrace_id, subrace_info in subraces.items():
        choices.append((str(subrace_id), subrace_info))

    for idx, (subrace_id, subrace_info) in enumerate(choices, 1):
        print()
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{Fore.CYAN}{subrace_info.get('name', '?')}"
            f"{Style.RESET_ALL}"
        )
        if not (subrace_id is None and idx == 1):
            _print_race_info(subrace_info, strings)

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    choice = _deps.get_int_input(
        get_string(strings, "character.subrace_prompt"),
        0,
        len(choices),
        strings,
    )
    if choice == 0:
        return False, None

    subrace_id, _ = choices[choice - 1]
    return True, subrace_id


def _select_class(
    strings: dict[str, Any], language: str = "ru"
) -> dict[str, Any] | None:
    """Выбрать класс персонажа или вернуться назад."""
    classes = _deps.load_classes(language)
    _print_screen_header(get_string(strings, "character.class_prompt"))
    for idx, cls in enumerate(classes, 1):
        print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {cls.get('name', '?')}")
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    class_idx = _deps.get_int_input(
        get_string(strings, "character.class_prompt", count=len(classes)),
        0,
        len(classes),
        strings,
    )
    if class_idx == 0:
        return None
    return classes[class_idx - 1]


def show_create_character_flow(
    strings: dict[str, Any], language: str = "ru"
) -> Character | None:
    """Flow «Создать персонажа»: сложность → создание."""
    difficulty = select_difficulty(strings)
    if difficulty is None:
        return None

    _print_screen_header(get_string(strings, "character.creation_caption"))

    name = _deps.get_str_input(
        get_string(strings, "character.name_prompt"),
        min_length=2,
        only_letters=True,
        strings=strings,
    )

    while True:
        races = _deps.load_races(language)
        _print_screen_header(get_string(strings, "character.race_caption"))

        for idx, race in enumerate(races, 1):
            print(
                f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
                f"{race.get('name', '?')}"
            )

        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'character.back')}"
        )
        print()
        choice = _deps.get_int_input(
            get_string(strings, "character.race_prompt", count=len(races)),
            0,
            len(races),
            strings,
        )
        if choice == 0:
            return None

        selected = races[choice - 1]
        race_id = str(selected.get("id") or selected.get("name"))

        while True:
            subrace_selected, subrace_id = _select_subrace(
                strings, race_id, language
            )
            if not subrace_selected:
                break

            while True:
                stats = show_stats_generation_flow(
                    strings, race_id, subrace_id, difficulty
                )
                if stats is None:
                    break

                cls = _select_class(strings, language)
                if cls is None:
                    continue

                class_id = cls.get("id") or cls.get("name")

                character = _deps.save_character(
                    name=name,
                    race_id=str(race_id),
                    class_id=str(class_id),
                    difficulty=difficulty,
                    subrace_id=str(subrace_id) if subrace_id else None,
                    stats=stats,
                )

                msg = get_string(strings, "character.save_success", name=name)
                print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
                print()
                _press_enter(strings)

                return character
