"""Flow создания персонажа: сложность, имя, state machine."""

from core.localization import get_string
from core.models import Character
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import _print_screen_header
from ui.menus._creation_steps import _CreationState, run_creation_steps
from ui.menus.settings import select_difficulty


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
    return run_creation_steps(strings, state, language)
