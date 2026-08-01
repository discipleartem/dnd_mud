"""Интерактивный исполнитель YAML-сценариев приключений."""

from collections.abc import Callable
from typing import Any

from colorama import Fore, Style

from core.character.models import Adventure, Character
from core.character.storage import update_character
from core.game_engine import GameEngine, GameSession, UiAction
from core.platform.localization import get_string, resolve_localized_text
from core.session_runner import (
    apply_pending_ui_actions,
    persist_adventure_session,
    resolve_menu_character,
)
from core.types import LanguageCode, StringsDict
from ui.menus.class_features import apply_pending_class_features
from ui.menus.console import (
    press_enter,
    print_numbered_row,
    print_screen_header,
    read_numbered_choice,
)
from ui.menus.level_up import run_pending_level_ups
from ui.menus.subclass_trainer import assign_subclass_from_menu
from ui.terminal_wrap import wrap_text


def _show_action_message(
    strings: StringsDict,
    message_key: str | None,
    message_params: dict[str, Any] | None = None,
) -> None:
    """Показать сообщение action, если задан ключ."""
    if not message_key:
        return
    params = message_params or {}
    print(
        f"{Fore.YELLOW}"
        f"{get_string(strings, message_key, **params)}"
        f"{Style.RESET_ALL}"
    )
    print()


def _persist_menu_result(
    updated: Character | None,
    character: Character,
) -> Character:
    """Сохранить персонажа после UI-меню или вернуть исходного."""
    return resolve_menu_character(updated, character)


def _run_character_menu_action(
    strings: StringsDict,
    character: Character,
    language: LanguageCode,
    menu_fn: Callable[
        [StringsDict, Character, LanguageCode],
        Character | None,
    ],
    *,
    message_key: str | None = None,
) -> Character:
    """Выполнить UI-меню и сохранить результат."""
    character = _persist_menu_result(
        menu_fn(strings, character, language),
        character,
    )
    _show_action_message(strings, message_key)
    return character


def _handle_engine_ui(
    pending: list[UiAction],
    character: Character,
    strings: StringsDict,
    language: LanguageCode,
) -> Character:
    """Обработать UI-действия из движка."""

    def _dispatch(action: UiAction, current: Character) -> Character:
        handler = _PENDING_UI_HANDLERS.get(action.kind)
        if handler is None:
            return current
        return handler(strings, current, language, action)

    return apply_pending_ui_actions(pending, character, _dispatch)


def _handle_level_up_ui(
    strings: StringsDict,
    character: Character,
    language: LanguageCode,
    _action: UiAction,
) -> Character:
    return run_pending_level_ups(strings, character, language)


def _handle_pick_subclass_ui(
    strings: StringsDict,
    character: Character,
    language: LanguageCode,
    action: UiAction,
) -> Character:
    return _run_character_menu_action(
        strings,
        character,
        language,
        assign_subclass_from_menu,
        message_key=action.message_key,
    )


def _handle_apply_class_features_ui(
    strings: StringsDict,
    character: Character,
    language: LanguageCode,
    _action: UiAction,
) -> Character:
    return _persist_menu_result(
        apply_pending_class_features(strings, character, language),
        character,
    )


_PENDING_UI_HANDLERS: dict[
    str,
    Callable[[StringsDict, Character, LanguageCode, UiAction], Character],
] = {
    "level_up": _handle_level_up_ui,
    "pick_subclass": _handle_pick_subclass_ui,
    "apply_class_features": _handle_apply_class_features_ui,
}


def _persist_session(engine: GameEngine, adventure: Adventure) -> None:
    """Сохранить снимок сессии приключения."""
    persist_adventure_session(engine, adventure)


def run_scenario_with_engine(
    engine: GameEngine,
    adventure: Adventure,
    strings: StringsDict,
    language: LanguageCode = "ru",
) -> Character:
    """Запустить сценарий через GameEngine."""
    graph = engine.load_scenario(adventure)
    node_id = engine.session.current_node_id or graph.start_node_id
    current = engine.session.character

    while node_id:
        engine.session.current_node_id = node_id
        node = engine.current_node()
        if node is None:
            break

        description = resolve_localized_text(
            node.get("description"), language, fallback=""
        )
        print_screen_header(adventure.get_name(language))
        if description:
            print(wrap_text(description))
            print()

        node_action = node.get("action")
        if isinstance(node_action, str):
            engine_result = engine.step_auto_node(node)
            current = engine_result.character
            current = _handle_engine_ui(
                engine_result.pending_ui, current, strings, language
            )
            engine.session.character = current
            _persist_session(engine, adventure)
            if engine_result.exit_scenario:
                break
            _show_action_message(
                strings,
                engine_result.message_key,
                engine_result.message_params,
            )
            node_id = engine_result.next_node_id
            continue

        choices = node.get("choices", [])
        if not isinstance(choices, list) or not choices:
            break

        for idx, choice in enumerate(choices, 1):
            if not isinstance(choice, dict):
                continue
            label = resolve_localized_text(
                choice.get("text"), language, fallback=""
            )
            print_numbered_row(idx, label)
        choice_num = read_numbered_choice(
            strings,
            len(choices),
            prompt_key="scenario.choice_prompt",
            back_label_key="character.back",
        )
        if choice_num is None:
            break

        selected = choices[choice_num - 1]
        if not isinstance(selected, dict):
            break

        engine_result = engine.step_choice(selected)
        current = engine_result.character
        current = _handle_engine_ui(
            engine_result.pending_ui, current, strings, language
        )
        engine.session.character = current
        _persist_session(engine, adventure)
        if engine_result.exit_scenario:
            break
        _show_action_message(
            strings,
            engine_result.message_key,
            engine_result.message_params,
        )
        node_id = engine_result.next_node_id

    update_character(current)
    return current


def run_scenario(
    adventure: Adventure,
    character: Character,
    strings: StringsDict,
    language: LanguageCode = "ru",
) -> Character:
    """Запустить сценарий приключения. Возвращает обновлённого персонажа."""
    script_file = adventure.script_file
    if not script_file:
        print(
            f"{Fore.YELLOW}"
            f"{get_string(strings, 'scenario.no_script')}"
            f"{Style.RESET_ALL}"
        )
        print()
        press_enter(strings)
        return character

    session = GameSession(
        character=character,
        adventure_id=adventure.id,
        current_node_id=None,
        difficulty=character.difficulty,
        script_file=str(script_file),
    )
    engine = GameEngine(session)
    return run_scenario_with_engine(engine, adventure, strings, language)
