"""Тесты единого загрузчика каталогов."""

from pathlib import Path

import pytest

from core.catalog_loader import (
    clear_all_catalog_caches,
    clear_catalog_cache,
    load_catalog,
)
from core.io import CatalogLoadError
from core.races import RACES_FILE

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_load_catalog_returns_races() -> None:
    clear_catalog_cache()
    races = load_catalog(RACES_FILE, "races")
    assert "human" in races


def test_clear_all_catalog_caches_resets_load_catalog() -> None:
    first = load_catalog(RACES_FILE, "races")
    clear_all_catalog_caches()
    second = load_catalog(RACES_FILE, "races")
    assert first is not second


def test_load_catalog_raises_on_corrupt_yaml(tmp_path: Path) -> None:
    path = tmp_path / "races.yaml"
    path.write_text(":\n  bad: [unclosed", encoding="utf-8")
    clear_catalog_cache()
    with pytest.raises(CatalogLoadError):
        load_catalog(path, "races")


def test_dragonborn_mod_overlay(tmp_path, monkeypatch):
    """Включённый mod добавляет расу dragonborn."""
    import json

    from core.mod_loader import clear_mod_loader_cache, load_merged_catalog

    state_path = tmp_path / "mods_state.json"
    state_path.write_text(
        json.dumps({"enabled": ["dragonborn_pack"]}), encoding="utf-8"
    )
    monkeypatch.setattr("core.mod_loader.MODS_STATE_FILE", state_path)
    clear_mod_loader_cache()
    clear_all_catalog_caches()
    races = load_merged_catalog("database/races/races.yaml", "races")
    assert "dragonborn" in races
