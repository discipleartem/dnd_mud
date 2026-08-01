"""Тесты единого загрузчика каталогов."""

from pathlib import Path

import pytest

from core.catalogs.races import RACES_FILE
from core.platform.catalog_loader import load_catalog, reload_catalogs
from core.platform.io import CatalogLoadError

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_load_catalog_returns_races() -> None:
    reload_catalogs()
    races = load_catalog(RACES_FILE, "races")
    assert "human" in races


def test_reload_catalogs_resets_load_catalog() -> None:
    first = load_catalog(RACES_FILE, "races")
    reload_catalogs()
    second = load_catalog(RACES_FILE, "races")
    assert first is not second


def test_load_catalog_raises_on_corrupt_yaml(tmp_path: Path) -> None:
    path = tmp_path / "races.yaml"
    path.write_text(":\n  bad: [unclosed", encoding="utf-8")
    reload_catalogs()
    with pytest.raises(CatalogLoadError):
        load_catalog(path, "races")


def test_dragonborn_mod_overlay(tmp_path, monkeypatch):
    """Включённый mod добавляет расу dragonborn."""
    import json

    from core.platform.mod_loader import (
        clear_mod_loader_cache,
        load_merged_catalog,
    )

    state_path = tmp_path / "mods_state.json"
    state_path.write_text(
        json.dumps({"enabled": ["dragonborn_pack"]}), encoding="utf-8"
    )
    monkeypatch.setattr("core.platform.mod_loader.MODS_STATE_FILE", state_path)
    clear_mod_loader_cache()
    reload_catalogs()
    races = load_merged_catalog("database/races/races.yaml", "races")
    assert "dragonborn" in races


def test_corrupt_mod_manifest_skips_overlay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Битый manifest.yaml включённого мода не роняет загрузку каталога."""
    import json

    from core.platform.mod_loader import (
        clear_mod_loader_cache,
        load_merged_catalog,
    )

    mod_id = "broken_pack"
    mod_dir = tmp_path / "mods" / mod_id
    mod_dir.mkdir(parents=True)
    (mod_dir / "manifest.yaml").write_text(
        ":\n  bad: [unclosed", encoding="utf-8"
    )

    state_path = tmp_path / "mods_state.json"
    state_path.write_text(json.dumps({"enabled": [mod_id]}), encoding="utf-8")
    monkeypatch.setattr("core.platform.mod_loader.MODS_DIR", tmp_path / "mods")
    monkeypatch.setattr("core.platform.mod_loader.MODS_STATE_FILE", state_path)
    clear_mod_loader_cache()
    reload_catalogs()

    races = load_merged_catalog("database/races/races.yaml", "races")
    assert "human" in races
