"""Тесты расширенных проверок."""

from core.checks import ability_check, passive_skill, skill_check
from core.models import Character


def test_skill_check_and_passive() -> None:
    character = Character(
        name="Rogue",
        race="human",
        class_id="rogue",
        stats={"dexterity": 16},
        skills=["stealth"],
        level=3,
    )
    result = skill_check(character, "stealth", dc=10)
    assert result["proficient"] is True
    assert result["total"] == result["roll"] + result["modifier"]
    assert passive_skill(character, "stealth") == 10 + result["modifier"]


def test_ability_check() -> None:
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        stats={"strength": 14},
    )
    result = ability_check(character, "strength", dc=12)
    assert result["ability"] == "strength"
    assert "success" in result
