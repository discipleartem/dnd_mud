"""Flow «Загрузить игру»: список сессий и продолжение приключения."""

from colorama import Fore, Style

from core.adventure import load_adventures
from core.catalog_loader import bootstrap_session_catalogs
from core.game_engine import GameEngine, GameSession
from core.localization import get_string
from core.session_storage import (
    find_adventure,
    list_sessions,
    load_character_for_session,
    load_session,
)
from core.types import LanguageCode, StringsDict
from ui.menus._common import (
    _press_enter,
    _print_screen_header,
    _read_numbered_choice,
)
from ui.menus.scenario_flow import run_scenario_with_engine


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
    choice = _read_numbered_choice(
        strings,
        len(sessions),
        prompt_key="load_game.prompt",
        back_label_key="load_game.back",
        prompt_kwargs={"count": len(sessions)},
    )
    if choice is None:
        return

    snapshot = sessions[choice - 1]
    loaded = load_session(snapshot.save_slug)
    if loaded is None:
        return
    character = load_character_for_session(loaded)
    if character is None:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'load_game.missing_character')}"
            f"{Style.RESET_ALL}"
        )
        print()
        _press_enter(strings)
        return

    adventures = load_adventures()
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

    bootstrap_session_catalogs(loaded.difficulty)

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
