"""Интерактивный исполнитель YAML-сценариев приключений."""

from typing import Any

from colorama import Fore, Style

from core.character_storage import update_character
from core.localization import get_string, resolve_localized_text
from core.models import Adventure, Character
from core.scenario_actions import (
    ScenarioActionResult,
    apply_scenario_action,
    load_scenario,
)
from core.types import LanguageCode, StringsDict
from ui.menus import _deps
from ui.menus._common import _press_enter, _print_screen_header
from ui.menus.level_up import run_pending_level_ups
from ui.menus.subclass_trainer import assign_subclass_from_menu


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
        updated = assign_subclass_from_menu(strings, character, language)
        if updated is not None:
            character = updated
        else:
            update_character(character)
        _show_action_message(strings, result.message_key)
        return character

    update_character(character)
    _show_action_message(strings, result.message_key)
    return character


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

    scenario = load_scenario(str(script_file))
    nodes = scenario.get("nodes", {})
    if not isinstance(nodes, dict):
        return character

    node_id: str | None = scenario.get("start_node")
    if not isinstance(node_id, str):
        return character

    current = character

    while node_id:
        node = nodes.get(node_id)
        if not isinstance(node, dict):
            break

        description = _resolve_text(node.get("description"), language)
        _print_screen_header(adventure.get_name(language))
        if description:
            print(description)
            print()

        node_action = node.get("action")
        if isinstance(node_action, str):
            current = _run_node_action(
                node_action, node, current, strings, language
            )
            next_id = node.get("next")
            node_id = str(next_id) if next_id else None
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

        action = selected.get("action")
        if isinstance(action, str):
            current = _run_node_action(
                action, selected, current, strings, language
            )
            if action == "exit":
                break

        next_id = selected.get("next")
        node_id = str(next_id) if next_id else None

    return current
