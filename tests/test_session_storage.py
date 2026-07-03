"""Тесты сохранения сессий приключений."""

from pathlib import Path

import pytest

from core.game_engine import GameEngine, GameSession
from core.models import Adventure, Character
from core.session_storage import (
    SessionSnapshot,
    load_character_for_session,
    load_session,
    save_session,
)


@pytest.fixture
def sessions_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Изолированный каталог saves/sessions."""
    path = tmp_path / "sessions"
    monkeypatch.setattr("core.session_storage.SESSIONS_DIR", path)
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
        class_id="fighter",
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
