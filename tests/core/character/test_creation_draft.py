"""Тесты черновика создания персонажа."""

from pathlib import Path

from core.character.creation_draft import (
    CreationDraft,
    clear_creation_draft,
    has_creation_draft,
    load_creation_draft,
    save_creation_draft,
)


def test_creation_draft_save_load_clear(tmp_path: Path) -> None:
    path = tmp_path / "creation_draft.json"
    draft = CreationDraft(
        current_step="stats",
        name="Aragorn",
        difficulty="normal",
        race_id="human",
        subrace_id="standard",
        stats={
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8,
        },
    )
    save_creation_draft(draft, path)
    assert has_creation_draft(path) is True
    loaded = load_creation_draft(path)
    assert loaded is not None
    assert loaded.current_step == "stats"
    assert loaded.name == "Aragorn"
    assert loaded.race_id == "human"
    assert loaded.stats is not None
    assert loaded.stats["strength"] == 15
    clear_creation_draft(path)
    assert has_creation_draft(path) is False
    assert load_creation_draft(path) is None


def test_creation_draft_corrupt_cleared(tmp_path: Path) -> None:
    path = tmp_path / "creation_draft.json"
    path.write_text("{not-json", encoding="utf-8")
    assert load_creation_draft(path) is None
    assert not path.exists()


def test_creation_draft_rejects_short_stat_keys(tmp_path: Path) -> None:
    path = tmp_path / "creation_draft.json"
    draft = CreationDraft(
        current_step="background",
        name="Hero",
        difficulty="normal",
        race_id="human",
        stats={
            "str": 15,
            "dex": 14,
            "con": 13,
            "int": 12,
            "wis": 10,
            "cha": 8,
        },
    )
    save_creation_draft(draft, path)
    loaded = load_creation_draft(path)
    assert loaded is not None
    assert loaded.stats is None
