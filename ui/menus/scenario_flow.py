"""Интерактивный исполнитель YAML-сценариев приключений."""

from collections.abc import Callable
from typing import Any

from colorama import Fore, Style

from core.game_engine import GameEngine, GameSession, UiAction
from core.localization import get_string, resolve_localized_text
from core.models import Adventure, Character
from core.scenario_actions import ScenarioActionResult, apply_scenario_action
from core.session_storage import SessionSnapshot, save_session
from core.types import LanguageCode, StringsDict
from ui.menus import _deps
from ui.menus._common import _press_enter, _print_screen_header
from ui.menus.class_features import apply_pending_class_features
from ui.menus.level_up import run_pending_level_ups
from ui.menus.subclass_trainer import assign_subclass_from_menu
from ui.terminal_wrap import wrap_text


def _resolve_text(value: object, language: LanguageCode) -> str:
    """Локализованный текст узла или действия."""
    if isinstance(value, dict):
        return resolve_localized_text(value, language, fallback="")
    if value is None:
        return ""
    return str(value)


def _show_action_message(
    strings: StringsDict, message_key: str | None
) -> None:
    """Показать сообщение action, если задан ключ."""
    if not message_key:
        return
    print(f"{Fore.YELLOW}{get_string(strings, message_key)}{Style.RESET_ALL}")
    print()


def _persist_menu_result(
    updated: Character | None,
    character: Character,
) -> Character:
    """Сохранить персонажа после UI-меню или вернуть исходного."""
    if updated is not None:
        return updated
    _deps.update_character(character)
    return character


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
    current = character
    for action in pending:
        if action.kind == "level_up":
            current = run_pending_level_ups(strings, current, language)
        elif action.kind == "pick_subclass":
            current = _run_character_menu_action(
                strings,
                current,
                language,
                assign_subclass_from_menu,
                message_key=action.message_key,
            )
        elif action.kind == "apply_class_features":
            current = _persist_menu_result(
                apply_pending_class_features(strings, current, language),
                current,
            )
    _deps.update_character(current)
    return current


def _handle_action_result(
    result: ScenarioActionResult,
    strings: StringsDict,
    language: LanguageCode,
) -> Character:
    """Сохранить персонажа и обработать UI-побочные эффекты action."""
    character = result.character
    if result.level_up_pending:
        character = run_pending_level_ups(strings, character, language)
    if result.pick_subclass:
        return _run_character_menu_action(
            strings,
            character,
            language,
            assign_subclass_from_menu,
            message_key=result.message_key,
        )
    if result.apply_class_features:
        return _persist_menu_result(
            apply_pending_class_features(strings, character, language),
            character,
        )

    _deps.update_character(character)
    _show_action_message(strings, result.message_key)
    return character


def _persist_session(engine: GameEngine, adventure: Adventure) -> None:
    """Сохранить снимок сессии приключения."""
    session = engine.session
    if not session.character.save_slug:
        return
    slug = f"{session.character.save_slug}_{adventure.id}"
    save_session(
        SessionSnapshot(
            save_slug=slug,
            character_save_slug=session.character.save_slug,
            adventure_id=adventure.id,
            current_node_id=session.current_node_id,
            difficulty=session.difficulty,
            flags=dict(session.flags),
            script_file=session.script_file,
        )
    )


def _run_node_action(
    action: str,
    action_data: dict[str, Any],
    character: Character,
    strings: StringsDict,
    language: LanguageCode,
) -> Character:
    """Выполнить action узла сценария с UI."""
    result = apply_scenario_action(action, action_data, character)
    return _handle_action_result(result, strings, language)


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

        description = _resolve_text(node.get("description"), language)
        _print_screen_header(adventure.get_name(language))
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
            _show_action_message(strings, engine_result.message_key)
            node_id = engine_result.next_node_id
            continue

        choices = node.get("choices", [])
        if not isinstance(choices, list) or not choices:
            break

        for idx, choice in enumerate(choices, 1):
            if not isinstance(choice, dict):
                continue
            label = _resolve_text(choice.get("text"), language)
            print(f"  {Fore.YELLOW}{idx}{Style.RESET_ALL}. {label}")
        print()
        print(
            f"  {Fore.YELLOW}0{Style.RESET_ALL}."
            f" {get_string(strings, 'character.back')}"
        )
        print()

        choice_num = _deps.get_int_input(
            get_string(strings, "scenario.choice_prompt", count=len(choices)),
            0,
            len(choices),
            strings,
        )
        if choice_num == 0:
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
        _show_action_message(strings, engine_result.message_key)
        node_id = engine_result.next_node_id

    _deps.update_character(current)
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
        _press_enter(strings)
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
