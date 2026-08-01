"""Application helpers для сессии приключения (без UI I/O)."""

from collections.abc import Callable

from core.character_storage import update_character
from core.game_engine import GameEngine, UiAction
from core.models import Adventure, Character
from core.session_storage import SessionSnapshot, save_session


def resolve_menu_character(
    updated: Character | None,
    character: Character,
) -> Character:
    """Вернуть результат меню или исходного персонажа после update."""
    if updated is not None:
        return updated
    update_character(character)
    return character


def apply_pending_ui_actions(
    pending: list[UiAction],
    character: Character,
    handler: Callable[[UiAction, Character], Character],
) -> Character:
    """Применить UI-действия engine и сохранить персонажа."""
    current = character
    for action in pending:
        current = handler(action, current)
    update_character(current)
    return current


def persist_adventure_session(
    engine: GameEngine, adventure: Adventure
) -> None:
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
