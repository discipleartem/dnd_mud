"""Тесты проверок режима сложности."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_adventure_allows_all_when_no_restrictions():
    from core.difficulty import adventure_allows_difficulty
    from core.models import Adventure

    adventure = Adventure(id="test", name="Test")

    assert adventure_allows_difficulty(adventure, "normal") is True
    assert adventure_allows_difficulty(adventure, "hardcore") is True


def test_adventure_hardcore_only():
    from core.difficulty import adventure_allows_difficulty
    from core.models import Adventure

    adventure = Adventure(id="hc", name="HC", hardcore_only=True)

    assert adventure_allows_difficulty(adventure, "hardcore") is True
    assert adventure_allows_difficulty(adventure, "normal") is False


def test_adventure_allowed_game_difficulties():
    from core.difficulty import adventure_allows_difficulty
    from core.models import Adventure

    adventure = Adventure(
        id="normal_only",
        name="Normal",
        allowed_game_difficulties=["normal"],
    )

    assert adventure_allows_difficulty(adventure, "normal") is True
    assert adventure_allows_difficulty(adventure, "hardcore") is False


def test_mod_allows_difficulty_without_requirement():
    from core.difficulty import mod_allows_difficulty

    assert mod_allows_difficulty({"name": "Any mod"}, "normal") is True


def test_mod_requires_hardcore():
    from core.difficulty import mod_allows_difficulty

    meta = {"name": "HC mod", "requires_game_difficulty": "hardcore"}

    assert mod_allows_difficulty(meta, "hardcore") is True
    assert mod_allows_difficulty(meta, "normal") is False
