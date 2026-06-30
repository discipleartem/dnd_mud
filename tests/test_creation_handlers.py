"""Тесты навигации и guard-clauses обработчиков создания персонажа."""

import pytest

from core.stats import STAT_NAMES
from ui.menus._creation_handlers import (
    _handle_feats,
    _handle_skills,
)
from ui.menus._creation_navigation import (
    back_step_from_feats,
    back_step_from_proficiencies,
    back_step_from_skills,
)
from ui.menus._creation_state import _CreationState


def _flat_stats(value: int = 10) -> dict[str, int]:
    return dict.fromkeys(STAT_NAMES, value)


def test_back_step_from_skills_and_feats_without_class() -> None:
    state = _CreationState(name="Test", difficulty="normal")
    assert back_step_from_skills(state) == "proficiencies"
    assert back_step_from_feats(state) == "class"


def test_back_step_from_feats_with_subclass(
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


def test_handlers_without_class_id() -> None:
    state = _CreationState(
        name="Test",
        difficulty="normal",
        race_id="human",
        stats=_flat_stats(),
    )
    assert _handle_feats({}, state, "ru").next_step == "class"
    assert _handle_skills({}, state, "ru").next_step == "proficiencies"


def test_back_step_from_proficiencies_via_feats(
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
