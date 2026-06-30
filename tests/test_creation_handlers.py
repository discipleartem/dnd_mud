"""Тесты навигации и guard-clauses обработчиков создания персонажа."""

import pytest

from core.stats import STAT_NAMES
from ui.menus._creation_handlers import _handle_feats, _handle_skills
from ui.menus._creation_navigation import (
    back_step_from_feats,
    back_step_from_proficiencies,
    back_step_from_skills,
)
from ui.menus._creation_state import _CreationState


def _flat_stats(value: int = 10) -> dict[str, int]:
    return dict.fromkeys(STAT_NAMES, value)


def test_back_step_from_skills_returns_proficiencies() -> None:
    state = _CreationState(name="Test", difficulty="normal")
    assert back_step_from_skills(state) == "proficiencies"


def test_back_step_from_feats_without_class_returns_class() -> None:
    state = _CreationState(name="Test", difficulty="normal")
    assert back_step_from_feats(state) == "class"


def test_back_step_from_feats_with_subclass_offered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _CreationState(
        name="Test",
        difficulty="normal",
        class_id="fighter",
    )
    monkeypatch.setattr(
        "ui.menus._creation_navigation.subclass_offered_at_creation",
        lambda _difficulty, _class_id: True,
    )
    assert back_step_from_feats(state) == "subclass"


def test_back_step_from_proficiencies_via_feats_step(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = _CreationState(
        name="Test",
        difficulty="normal",
        race_id="human",
        subrace_id="variant_human",
        class_id="fighter",
    )
    monkeypatch.setattr(
        "ui.menus._creation_navigation.feats_step_required",
        lambda _state: True,
    )
    assert back_step_from_proficiencies(state) == "feats"


def test_handle_feats_without_class_id_advances_to_class() -> None:
    state = _CreationState(
        name="Test",
        difficulty="normal",
        race_id="human",
        stats=_flat_stats(),
    )
    result = _handle_feats({}, state, "ru")
    assert result.next_step == "class"
    assert result.character is None


def test_handle_skills_without_class_id_advances_to_proficiencies() -> None:
    state = _CreationState(
        name="Test",
        difficulty="normal",
        race_id="human",
    )
    result = _handle_skills({}, state, "ru")
    assert result.next_step == "proficiencies"
    assert result.character is None


def test_handle_class_advances_to_proficiencies_without_feats_step(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ui.menus._creation_handlers import _handle_class

    state = _CreationState(
        name="Test",
        difficulty="normal",
        race_id="human",
        subrace_id="standard",
        stats=_flat_stats(),
        languages=["common"],
    )
    monkeypatch.setattr(
        "ui.menus._creation_steps.select_class",
        lambda _strings, _language: {"id": "fighter", "name": "Fighter"},
    )
    monkeypatch.setattr(
        "ui.menus._creation_handlers.subclass_offered_at_creation",
        lambda _difficulty, _class_id: False,
    )
    monkeypatch.setattr(
        "ui.menus._creation_navigation.feats_step_required",
        lambda _state: False,
    )

    result = _handle_class({}, state, "ru")

    assert result.next_step == "proficiencies"
    assert result.character is None
    assert state.class_id == "fighter"


def test_handle_expertise_completes_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from core.models import Character
    from ui.menus._creation_handlers import _handle_expertise

    expected = Character(
        name="RogueHero",
        race="human",
        class_id="rogue",
        level=1,
        stats=_flat_stats(),
    )
    monkeypatch.setattr(
        "ui.menus._creation_steps.select_creation_expertise",
        lambda *_args, **_kwargs: (["stealth"], []),
    )
    monkeypatch.setattr(
        "ui.menus._creation_steps.finalize_creation",
        lambda _strings, _state: expected,
    )
    state = _CreationState(
        name="RogueHero",
        difficulty="normal",
        class_id="rogue",
        skills=["stealth", "acrobatics"],
    )

    result = _handle_expertise({}, state, "ru")

    assert result.character is expected
    assert result.next_step is None
