"""Тесты game engine."""

from core.game_engine import GameEngine, GameSession
from core.models import Adventure, Character
from core.types import CharacterClass


def test_game_engine_grant_xp_triggers_level_up_pending() -> None:
    character = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
        experience=0,
    )
    adventure = Adventure(
        id="tutorial",
        script_file="adventures/tutorial.yaml",
    )
    session = GameSession(
        character=character,
        adventure_id=adventure.id,
        current_node_id=None,
        difficulty="normal",
    )
    engine = GameEngine(session)
    engine.load_scenario(adventure)
    result = engine.apply_action("grant_xp", {"amount": 500})
    assert result.character.experience == 500
    assert result.pending_ui
