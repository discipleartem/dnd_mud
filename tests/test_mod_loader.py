"""Тесты загрузки модов."""

import json
from pathlib import Path

import pytest

from core.mod_loader import (
    clear_mod_loader_cache,
    load_merged_catalog,
)
from core.races import clear_races_cache


def test_dragonborn_mod_overlay(tmp_path, monkeypatch):
    """Включённый mod добавляет расу dragonborn."""
    state_path = tmp_path / "mods_state.json"
    state_path.write_text(
        json.dumps({"enabled": ["dragonborn_pack"]}), encoding="utf-8"
    )
    monkeypatch.setattr(
        "core.mod_loader.MODS_STATE_FILE",
        state_path,
    )
    clear_mod_loader_cache()
    clear_races_cache()

    races = load_merged_catalog("database/races/races.yaml", "races")
    assert "dragonborn" in races
    subraces = races["dragonborn"].get("subraces", {})
    assert "dragonborn" in subraces

    clear_mod_loader_cache()
    clear_races_cache()


def test_corrupt_mod_manifest_skips_overlay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Битый manifest.yaml включённого мода не роняет загрузку каталога."""
    mod_id = "broken_pack"
    mod_dir = tmp_path / "mods" / mod_id
    mod_dir.mkdir(parents=True)
    (mod_dir / "manifest.yaml").write_text(
        ":\n  bad: [unclosed", encoding="utf-8"
    )

    state_path = tmp_path / "mods_state.json"
    state_path.write_text(json.dumps({"enabled": [mod_id]}), encoding="utf-8")
    monkeypatch.setattr("core.mod_loader.MODS_DIR", tmp_path / "mods")
    monkeypatch.setattr("core.mod_loader.MODS_STATE_FILE", state_path)
    clear_mod_loader_cache()
    clear_races_cache()

    races = load_merged_catalog("database/races/races.yaml", "races")
    assert "human" in races
