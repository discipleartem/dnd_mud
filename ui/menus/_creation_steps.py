"""Шаги state machine создания персонажа."""

from core.character.models import Character
from core.platform.localization import get_string
from core.types import StringsDict
from ui.input_handler import get_str_input
from ui.menus._creation_handlers import _STEP_HANDLERS
from ui.menus._creation_state import CreationStep, _CreationState
from ui.menus.console import print_screen_header
from ui.menus.settings import select_difficulty


def show_create_character_flow(
    strings: StringsDict, language: str = "ru"
) -> Character | None:
    """Flow «Создать персонажа»: сложность → создание."""
    difficulty = select_difficulty(strings)
    if difficulty is None:
        return None

    print_screen_header(get_string(strings, "character.creation_caption"))

    name = get_str_input(
        get_string(strings, "character.name_prompt"),
        min_length=2,
        only_letters=True,
        strings=strings,
    )

    state = _CreationState(name=name, difficulty=difficulty)
    return run_creation_steps(strings, state, language)


def run_creation_steps(
    strings: StringsDict,
    state: _CreationState,
    language: str = "ru",
) -> Character | None:
    """Цикл шагов создания персонажа после ввода имени."""
    step: CreationStep = "race"

    while True:
        result = _STEP_HANDLERS[step](strings, state, language)
        if result.character is not None:
            return result.character
        if result.next_step is None:
            return None
        step = result.next_step
