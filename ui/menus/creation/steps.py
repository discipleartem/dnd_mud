"""Шаги state machine создания персонажа."""

from core.character.creation_draft import (
    clear_creation_draft,
    load_creation_draft,
    save_creation_draft,
)
from core.character.models import Character
from core.platform.localization import get_string
from core.types import StringsDict
from ui.input_handler import get_str_input
from ui.menus.console import print_screen_header
from ui.menus.creation.handlers import _STEP_HANDLERS
from ui.menus.creation.state import (
    CreationStep,
    _CreationState,
    draft_from_state,
    state_from_draft,
)
from ui.menus.hub.settings import select_difficulty


def _persist_draft(state: _CreationState, step: CreationStep) -> None:
    save_creation_draft(draft_from_state(state, step))


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
    _persist_draft(state, "race")
    return run_creation_steps(strings, state, language)


def show_continue_character_flow(
    strings: StringsDict, language: str = "ru"
) -> Character | None:
    """Продолжить незавершённое создание персонажа."""
    draft = load_creation_draft()
    if draft is None:
        return None
    print_screen_header(get_string(strings, "character.creation_caption"))
    state = state_from_draft(draft)
    return run_creation_steps(
        strings, state, language, start_step=draft.current_step
    )


def run_creation_steps(
    strings: StringsDict,
    state: _CreationState,
    language: str = "ru",
    *,
    start_step: CreationStep = "race",
) -> Character | None:
    """Цикл шагов создания персонажа после ввода имени."""
    step: CreationStep = start_step

    try:
        while True:
            result = _STEP_HANDLERS[step](strings, state, language)
            if result.character is not None:
                clear_creation_draft()
                return result.character
            if result.next_step is None:
                clear_creation_draft()
                return None
            step = result.next_step
            _persist_draft(state, step)
    except KeyboardInterrupt:
        # Fallback: основная защита в input_handler; черновик не чистим.
        return None
