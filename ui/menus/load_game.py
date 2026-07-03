"""Flow «Загрузить игру»: список сессий и продолжение приключения."""

from colorama import Fore, Style

from core.catalog_loader import reload_catalogs
from core.character_storage import CHARACTERS_DIR
from core.game_engine import GameEngine, GameSession
from core.mod_loader import set_mod_gating_difficulty
from core.session_storage import (
    find_adventure,
    list_sessions,
    load_character_for_session,
    load_session,
)
from ui.menus import _deps
from ui.menus._common import _press_enter, _print_screen_header
from ui.menus.scenario_flow import run_scenario_with_engine

StringsDict = _deps.StringsDict
LanguageCode = _deps.LanguageCode
get_string = _deps.get_string


def show_load_game_flow(
    strings: StringsDict,
    language: LanguageCode = "ru",
) -> None:
    """Выбор сохранённой сессии и возобновление сценария."""
    sessions = list_sessions()
    if not sessions:
        _print_screen_header(get_string(strings, "load_game.caption"))
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'load_game.no_sessions')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return

    _print_screen_header(get_string(strings, "load_game.caption"))
    for idx, snapshot in enumerate(sessions, 1):
        print(
            f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}."
            f" {snapshot.adventure_id} — {snapshot.character_save_slug}"
        )
    print()
    print(
        f"  {Fore.YELLOW}0{Style.RESET_ALL}."
        f" {get_string(strings, 'load_game.back')}"
    )
    print()
    choice = _deps.get_int_input(
        get_string(strings, "load_game.prompt", count=len(sessions)),
        0,
        len(sessions),
        strings,
    )
    if choice == 0:
        return

    snapshot = sessions[choice - 1]
    loaded = load_session(snapshot.save_slug)
    if loaded is None:
        return
    character = load_character_for_session(loaded, CHARACTERS_DIR)
    if character is None:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'load_game.missing_character')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return

    adventures = _deps.load_adventures()
    adventure = find_adventure(adventures, loaded.adventure_id)
    if adventure is None:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'load_game.missing_adventure')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return

    set_mod_gating_difficulty(loaded.difficulty)
    reload_catalogs()

    session = GameSession(
        character=character,
        adventure_id=loaded.adventure_id,
        current_node_id=loaded.current_node_id,
        difficulty=loaded.difficulty,
        flags=dict(loaded.flags),
        script_file=loaded.script_file,
    )
    engine = GameEngine(session)
    run_scenario_with_engine(engine, adventure, strings, language)
