"""Тесты mod gating и reload каталогов."""

import pytest

from core.catalog_loader import reload_catalogs
from core.mod_loader import (
    _enabled_mod_ids,
    _mod_allowed_for_difficulty,
    save_mods_state,
    set_mod_gating_difficulty,
)

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_mod_allowed_for_difficulty() -> None:
    manifest = {"requires_game_difficulty": "hardcore"}
    assert _mod_allowed_for_difficulty(manifest, "hardcore")
    assert not _mod_allowed_for_difficulty(manifest, "normal")
    assert _mod_allowed_for_difficulty(manifest, None)


def test_enabled_mod_ids_respects_gating(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
