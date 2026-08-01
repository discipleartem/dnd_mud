"""Тесты расширенных проверок."""

from core.character.models import Character
from core.mechanics.checks import ability_check, passive_skill, skill_check
from core.types import CharacterClass


def test_skill_check_and_passive() -> None:
    character = Character(
        name="Rogue",
        race="human",
        class_id=CharacterClass.ROGUE,
        stats={"dexterity": 16},
        skills=["stealth"],
        level=3,
    )
    result = skill_check(character, "stealth", dc=10)
    assert result["proficient"] is True
    assert result["total"] == result["roll"] + result["modifier"]
    assert passive_skill(character, "stealth") == 10 + result["modifier"]


def test_skill_check_scenario_action_returns_message() -> None:
    from core.engine.scenario_actions import apply_scenario_action

    character = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.ROGUE,
        skills=["stealth"],
    )
    result = apply_scenario_action(
        "skill_check",
        {"skill": "stealth", "dc": 5},
        character,
    )
    assert result.message_key in (
        "scenario.skill_check_success",
        "scenario.skill_check_failure",
    )
    assert result.message_params is not None
    assert result.message_params["skill"] == "stealth"
    assert result.message_params["dc"] == 5


def test_ability_check() -> None:
    character = Character(
        name="Hero",
        race="human",
        class_id=CharacterClass.FIGHTER,
        stats={"strength": 14},
    )
    result = ability_check(character, "strength", dc=12)
    assert result["ability"] == "strength"
    assert "success" in result
