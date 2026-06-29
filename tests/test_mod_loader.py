"""Тесты загрузки модов."""

import json

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
