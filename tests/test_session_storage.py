"""Тесты сохранения сессий приключений."""

from pathlib import Path

import pytest

from core.character.models import Adventure, Character
from core.engine.game_engine import GameEngine, GameSession
from core.engine.session_storage import (
    SessionSnapshot,
    delete_session,
    list_sessions,
    load_character_for_session,
    load_session,
    save_session,
)
from core.types import CharacterClass


@pytest.fixture
def sessions_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Изолированный каталог saves/sessions."""
    path = tmp_path / "sessions"
    monkeypatch.setattr("core.engine.session_storage.SESSIONS_DIR", path)
    return path


def test_session_save_load_roundtrip(sessions_dir: Path) -> None:
    snapshot = SessionSnapshot(
        save_slug="hero_tutorial",
        character_save_slug="hero",
        adventure_id="tutorial",
        current_node_id="training",
        difficulty="normal",
        flags={"visited": True},
        script_file="adventures/tutorial.yaml",
    )
    save_session(snapshot)
    loaded = load_session("hero_tutorial")
    assert loaded is not None
    assert loaded.save_slug == "hero_tutorial"
    assert loaded.current_node_id == "training"
    assert loaded.flags == {"visited": True}
    assert loaded.difficulty == "normal"


def test_load_scenario_preserves_resumed_node_id() -> None:
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
        current_node_id="training",
        difficulty="normal",
    )
    engine = GameEngine(session)
    graph = engine.load_scenario(adventure)
    assert graph.start_node_id == "welcome"
    assert engine.session.current_node_id == "training"


def test_load_character_for_session_skips_invalid_save(
    characters_dir: Path,
) -> None:
    characters_dir.mkdir(parents=True, exist_ok=True)
    (characters_dir / "hero.json").write_text("{not json", encoding="utf-8")
    snapshot = SessionSnapshot(
        save_slug="hero_tutorial",
        character_save_slug="hero",
        adventure_id="tutorial",
        current_node_id=None,
        difficulty="normal",
    )
    assert load_character_for_session(snapshot, characters_dir) is None


def test_list_sessions_orders_by_updated_at(
    sessions_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = SessionSnapshot(
        save_slug="first",
        character_save_slug="hero",
        adventure_id="tutorial",
        current_node_id="welcome",
        difficulty="normal",
        updated_at="2020-01-01T00:00:00+00:00",
    )
    second = SessionSnapshot(
        save_slug="second",
        character_save_slug="hero",
        adventure_id="tutorial",
        current_node_id="training",
        difficulty="normal",
        updated_at="2021-01-01T00:00:00+00:00",
    )
    save_session(first)
    save_session(second)
    slugs = [item.save_slug for item in list_sessions()]
    assert slugs == ["first", "second"]


def test_delete_session_removes_file(sessions_dir: Path) -> None:
    save_session(
        SessionSnapshot(
            save_slug="gone",
            character_save_slug="hero",
            adventure_id="tutorial",
            current_node_id=None,
            difficulty="normal",
        )
    )
    assert delete_session("gone") is True
    assert load_session("gone") is None
    assert delete_session("missing") is False
