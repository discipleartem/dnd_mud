"""Шаги state machine создания персонажа."""

from core.localization import get_string
from core.models import Character
from core.types import StringsDict
from ui.menus import _deps
from ui.menus._common import (
    _print_screen_header,
    _print_success_and_wait,
)
from ui.menus._creation_finalize import (
    save_created_character,
)
from ui.menus._creation_state import _CreationState
from ui.menus.settings import select_difficulty


def finalize_creation(
    strings: StringsDict, state: _CreationState
) -> Character | None:
    """Сохранить персонажа и показать сообщение об успехе."""
    character = save_created_character(state)
    if character is None:
        return None
    msg = get_string(strings, "character.save_success", name=state.name)
    _print_success_and_wait(strings, msg)
    return character


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


def run_creation_steps(
    strings: StringsDict,
    state: _CreationState,
    language: str = "ru",
) -> Character | None:
    """Цикл шагов создания персонажа после ввода имени."""
    from ui.menus._creation_handlers import _STEP_HANDLERS
    from ui.menus._creation_state import CreationStep

    step: CreationStep = "race"

    while True:
        result = _STEP_HANDLERS[step](strings, state, language)
        if result.character is not None:
            return result.character
        if result.next_step is None:
            return None
        step = result.next_step
