"""Flow «Создать персонажа»: имя, раса, подраса, класс, архетип."""

from dataclasses import dataclass, field
from typing import Any, Literal

from colorama import Fore, Style

from core.localization import get_string
from core.models import Character
from core.subclasses import subclass_offered_at_creation
from core.types import GameDifficulty, StatMap, StringsDict
from ui.menus import _deps
from ui.menus._common import (
    SEPARATOR,
    _print_screen_header,
    _print_success_and_wait,
    _run_numbered_menu,
)
from ui.menus._display import (
    _print_class_info,
    _print_class_summary,
    _print_race_info,
    _print_subclass_info,
)
from ui.menus.settings import select_difficulty
from ui.menus.stats import show_stats_generation_flow

CreationStep = Literal["race", "subrace", "stats", "class", "subclass"]


@dataclass
class _CreationState:
    """Состояние пошагового создания персонажа."""

    name: str
    difficulty: GameDifficulty
    race_id: str | None = None
    subrace_id: str | None = None
    stats: StatMap | None = None
    class_id: str | None = None
    subclass_id: str | None = None
    hardcore_rolls: list[int] = field(default_factory=list)


def _select_subrace(
    strings: StringsDict, race_id: str, language: str = "ru"
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
        if not allow_base:
            return False, None
        print(get_string(strings, "character.no_subraces"))
        print()
        choice = _run_numbered_menu(
            strings,
            [str(race_name)],
            prompt_key="character.subrace_prompt",
            back_label_key="character.back",
        )
        if choice is None:
            return False, None
        return True, None

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
    strings: StringsDict, language: str = "ru"
) -> dict[str, Any] | None:
    """Выбрать класс персонажа (краткий обзор каждого класса)."""
    classes = _deps.load_classes(language)
    _print_screen_header(get_string(strings, "character.class_caption"))

    class_details: list[dict[str, Any]] = []
    for cls in classes:
        class_id = str(cls.get("id") or cls.get("name"))
        class_details.append(_deps.load_class_full(class_id, language))

    for idx, class_info in enumerate(class_details, 1):
        if idx > 1:
            print(f"  {Fore.LIGHTBLACK_EX}{'─' * 74}{Style.RESET_ALL}")
        print()
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{Fore.CYAN}{Style.BRIGHT}"
            f"{class_info.get('name', '?')}"
            f"{Style.RESET_ALL}"
        )
        _print_class_summary(class_info, strings)

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    choice = _deps.get_int_input(
        get_string(strings, "character.class_prompt"),
        0,
        len(class_details),
        strings,
    )
    if choice == 0:
        return None
    return class_details[choice - 1]


def _select_subclass(
    strings: StringsDict,
    class_id: str,
    language: str = "ru",
) -> str | None:
    """Выбрать подкласс (подробный обзор архетипов)."""
    class_full = _deps.load_class_full(class_id, language)
    subclasses = _deps.load_subclasses(class_id, language)

    if not subclasses:
        return None

    _print_screen_header(get_string(strings, "character.subclass_caption"))

    class_name = class_full.get("name", class_id)
    print(f"{Fore.CYAN}{Style.BRIGHT}{class_name}{Style.RESET_ALL}")
    _print_class_info(class_full, strings)
    print()
    print(SEPARATOR)
    print()

    subclasses_title = get_string(
        strings, "character.subclasses_label"
    ).strip()
    print(f"{Fore.YELLOW}{Style.BRIGHT}{subclasses_title}{Style.RESET_ALL}")
    for idx, sub_info in enumerate(subclasses, 1):
        print()
        if idx > 1:
            print(f"  {Fore.LIGHTBLACK_EX}{'─' * 74}{Style.RESET_ALL}")
            print()
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. "
            f"{Fore.CYAN}{Style.BRIGHT}"
            f"{sub_info.get('name', '?')}"
            f"{Style.RESET_ALL}"
        )
        _print_subclass_info(sub_info, strings)

    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'character.back')}"
    )
    print()
    choice = _deps.get_int_input(
        get_string(strings, "character.subclass_prompt"),
        0,
        len(subclasses),
        strings,
    )
    if choice == 0:
        return None

    selected = subclasses[choice - 1]
    return str(selected.get("id", ""))


def _save_created_character(state: _CreationState) -> Character:
    """Сохранить персонажа из состояния создания."""
    assert state.race_id is not None
    assert state.stats is not None
    assert state.class_id is not None

    return _deps.save_character(
        name=state.name,
        race_id=str(state.race_id),
        class_id=str(state.class_id),
        difficulty=state.difficulty,
        subrace_id=str(state.subrace_id) if state.subrace_id else None,
        stats=state.stats,
        subclass_id=state.subclass_id,
    )


def show_create_character_flow(
    strings: StringsDict, language: str = "ru"
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

    state = _CreationState(name=name, difficulty=difficulty)
    step: CreationStep = "race"

    while True:
        match step:
            case "race":
                races = _deps.load_races(language)
                _print_screen_header(
                    get_string(strings, "character.race_caption")
                )
                choice = _run_numbered_menu(
                    strings,
                    [race.get("name", "?") for race in races],
                    prompt_key="character.race_prompt",
                    back_label_key="character.back",
                )
                if choice is None:
                    return None
                selected = races[choice - 1]
                state.race_id = str(selected.get("id") or selected.get("name"))
                step = "subrace"

            case "subrace":
                assert state.race_id is not None
                subrace_selected, subrace_id = _select_subrace(
                    strings, state.race_id, language
                )
                if not subrace_selected:
                    if state.difficulty == "hardcore":
                        state.hardcore_rolls.clear()
                    step = "race"
                    continue
                state.subrace_id = subrace_id
                step = "stats"

            case "stats":
                assert state.race_id is not None
                hardcore_rolls = (
                    state.hardcore_rolls
                    if state.difficulty == "hardcore"
                    else None
                )
                stats = show_stats_generation_flow(
                    strings,
                    state.race_id,
                    state.subrace_id,
                    state.difficulty,
                    hardcore_rolls=hardcore_rolls,
                )
                if stats is None:
                    step = "subrace"
                    continue
                state.stats = stats
                step = "class"

            case "class":
                assert state.race_id is not None
                assert state.stats is not None
                cls = _select_class(strings, language)
                if cls is None:
                    step = "stats"
                    continue

                state.class_id = str(cls.get("id") or cls.get("name"))
                if subclass_offered_at_creation(
                    state.difficulty, state.class_id
                ):
                    step = "subclass"
                else:
                    character = _save_created_character(state)
                    msg = get_string(
                        strings, "character.save_success", name=state.name
                    )
                    _print_success_and_wait(strings, msg)
                    return character

            case "subclass":
                assert state.class_id is not None
                subclass_id = _select_subclass(
                    strings, state.class_id, language
                )
                if subclass_id is None:
                    step = "class"
                    continue
                state.subclass_id = subclass_id
                character = _save_created_character(state)
                msg = get_string(
                    strings, "character.save_success", name=state.name
                )
                _print_success_and_wait(strings, msg)
                return character
