"""Тесты mod gating и reload каталогов."""

from pathlib import Path

import pytest

from core.catalog_loader import load_catalog, reload_catalogs
from core.mod_loader import (
    _enabled_mod_ids,
    _mod_allowed_for_difficulty,
    get_enabled_mod_ids,
    get_mod_gating_difficulty,
    list_available_mods,
    save_mods_state,
    set_mod_enabled,
    set_mod_gating_difficulty,
)
from core.races import RACES_FILE
from core.types import GameDifficulty

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_get_enabled_mod_ids_reads_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    state_file = tmp_path / "mods_state.json"
    monkeypatch.setattr("core.mod_loader.MODS_STATE_FILE", state_file)
    assert get_enabled_mod_ids() == frozenset()
    save_mods_state(["dragonborn_pack"])
    assert get_enabled_mod_ids() == frozenset({"dragonborn_pack"})
    set_mod_enabled("dragonborn_pack", False)
    assert get_enabled_mod_ids() == frozenset()


def test_get_mod_gating_difficulty() -> None:
    set_mod_gating_difficulty("hardcore")
    assert get_mod_gating_difficulty() == "hardcore"
    set_mod_gating_difficulty(None)


def test_mod_allowed_for_difficulty() -> None:
    manifest = {"requires_game_difficulty": "hardcore"}
    assert _mod_allowed_for_difficulty(manifest, "hardcore")
    assert not _mod_allowed_for_difficulty(manifest, "normal")
    assert _mod_allowed_for_difficulty(manifest, None)


def test_enabled_mod_ids_respects_gating(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    state_file = tmp_path / "mods_state.json"
    monkeypatch.setattr("core.mod_loader.MODS_STATE_FILE", state_file)
    save_mods_state(["dragonborn_pack"])
    set_mod_gating_difficulty("normal")
    monkeypatch.setattr(
        "core.mod_loader._load_mod_manifest",
        lambda mod_id: {"requires_game_difficulty": "hardcore"},
    )
    assert _enabled_mod_ids() == []
    set_mod_gating_difficulty("hardcore")
    assert _enabled_mod_ids() == ["dragonborn_pack"]
    set_mod_gating_difficulty(None)


def test_reload_catalogs_clears_cache() -> None:
    reload_catalogs()


def test_load_catalog_passes_mod_gating_difficulty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pathlib import Path

    seen: list[GameDifficulty | None] = []
    from core.mod_loader import load_merged_yaml as original_yaml

    def spy_yaml(
        path: Path,
        *,
        game_difficulty: GameDifficulty | None = None,
    ) -> dict[str, object]:
        seen.append(game_difficulty)
        return original_yaml(path, game_difficulty=game_difficulty)

    monkeypatch.setattr("core.mod_loader.load_merged_yaml", spy_yaml)
    set_mod_gating_difficulty("hardcore")
    reload_catalogs()
    load_catalog(RACES_FILE, "races")
    assert seen[-1] == "hardcore"
    set_mod_gating_difficulty(None)


def test_list_available_mods_includes_dragonborn_pack() -> None:
    ids = {str(mod.get("id", "")) for mod in list_available_mods()}
    assert "dragonborn_pack" in ids


def test_set_mod_enabled_persists_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    state_file = tmp_path / "mods_state.json"
    monkeypatch.setattr("core.mod_loader.MODS_STATE_FILE", state_file)
    set_mod_enabled("dragonborn_pack", True)
    assert get_enabled_mod_ids() == frozenset({"dragonborn_pack"})
    set_mod_enabled("dragonborn_pack", False)
    assert get_enabled_mod_ids() == frozenset()
