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


def test_game_engine_step_choice_advances_node() -> None:
    character = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
    )
    adventure = Adventure(
        id="tutorial",
        script_file="adventures/tutorial.yaml",
    )
    session = GameSession(
        character=character,
        adventure_id=adventure.id,
        current_node_id="welcome",
        difficulty="normal",
    )
    engine = GameEngine(session)
    engine.load_scenario(adventure)
    node = engine.current_node()
    assert node is not None
    choice = node.get("choices", [])[0]
    assert isinstance(choice, dict)
    result = engine.step_choice(choice)
    assert result.next_node_id == "training"
    assert engine.session.current_node_id == "training"


def test_game_engine_exit_scenario_flag() -> None:
    character = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
    )
    session = GameSession(
        character=character,
        adventure_id="tutorial",
        current_node_id="finish",
        difficulty="normal",
        script_file="adventures/tutorial.yaml",
    )
    engine = GameEngine(session)
    result = engine.apply_action("exit", {})
    assert result.exit_scenario is True
