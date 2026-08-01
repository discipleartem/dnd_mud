"""Тесты Phase 2: комнаты, бой, проверки по сложности."""

from core.character.models import Character
from core.engine.combat.rolls import attack_roll, roll_initiative
from core.engine.engine_rules import check_roll_flags
from core.engine.game_engine import GameEngine, GameSession
from core.engine.scenario_actions import apply_scenario_action
from core.engine.scenario_rooms import node_exits, resolve_exit
from core.types import CharacterClass


def test_check_roll_flags_by_difficulty() -> None:
    assert check_roll_flags("easy") == (True, False)
    assert check_roll_flags("normal") == (False, False)
    assert check_roll_flags("hardcore") == (False, True)


def test_ability_check_scenario_action() -> None:
    character = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
        stats={"strength": 16},
    )
    result = apply_scenario_action(
        "ability_check",
        {"ability": "strength", "dc": 10},
        character,
        difficulty="normal",
    )
    assert result.message_key in (
        "scenario.ability_check_success",
        "scenario.ability_check_failure",
    )
    assert result.message_params is not None
    assert result.message_params["ability"] == "strength"


def test_scenario_room_exits_and_engine_step() -> None:
    character = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
    )
    session = GameSession(
        character=character,
        adventure_id="room_test",
        current_node_id="hall",
        difficulty="normal",
    )
    engine = GameEngine(session)
    engine._graph = type(
        "G",
        (),
        {
            "nodes": {
                "hall": {
                    "description": "Hall",
                    "exits": {"north": "chamber"},
                },
                "chamber": {"description": "Chamber"},
            },
            "start_node_id": "hall",
        },
    )()
    assert engine.current_exits() == {"north": "chamber"}
    result = engine.step_exit("north")
    assert result.next_node_id == "chamber"
    assert engine.session.current_node_id == "chamber"


def test_node_exits_helpers() -> None:
    node = {"exits": {"east": "b", "west": None}}
    assert node_exits(node) == {"east": "b"}
    assert resolve_exit(node, "east") == "b"
    assert resolve_exit(node, "west") is None


def test_combat_initiative_and_attack_roll_shape() -> None:
    init = roll_initiative(3)
    assert init["total"] == init["roll"] + 3
    attack = attack_roll(5, target_ac=14)
    assert attack["total"] == attack["roll"] + 5
    assert isinstance(attack["hit"], bool)


def test_game_engine_session_flags() -> None:
    character = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
    )
    session = GameSession(
        character=character,
        adventure_id="tutorial",
        current_node_id="welcome",
        difficulty="hardcore",
    )
    engine = GameEngine(session)
    engine.set_flag("door_open", True)
    assert engine.get_flag("door_open") is True
    assert engine.get_flag("missing", False) is False
    assert engine.rule_mode == "hardcore"
