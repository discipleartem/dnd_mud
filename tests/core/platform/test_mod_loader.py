"""Тесты mod gating и reload каталогов."""

from pathlib import Path

import pytest

from core.catalogs.races import RACES_FILE
from core.platform.catalog_loader import load_catalog, reload_catalogs
from core.platform.mod_loader import (
    _enabled_mod_ids,
    _mod_allowed_for_difficulty,
    get_enabled_mod_ids,
    get_mod_gating_difficulty,
    list_available_mods,
    mod_enable_error,
    save_mods_state,
    set_mod_enabled,
    set_mod_gating_difficulty,
)
from core.types import GameDifficulty

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_get_enabled_mod_ids_reads_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    state_file = tmp_path / "mods_state.json"
    monkeypatch.setattr("core.platform.mod_loader.MODS_STATE_FILE", state_file)
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
    monkeypatch.setattr("core.platform.mod_loader.MODS_STATE_FILE", state_file)
    save_mods_state(["dragonborn_pack"])
    set_mod_gating_difficulty("normal")
    monkeypatch.setattr(
        "core.platform.mod_loader._load_mod_manifest",
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
    from core.platform.mod_loader import load_merged_yaml as original_yaml

    def spy_yaml(
        path: Path,
        *,
        game_difficulty: GameDifficulty | None = None,
    ) -> dict[str, object]:
        seen.append(game_difficulty)
        return original_yaml(path, game_difficulty=game_difficulty)

    monkeypatch.setattr("core.platform.mod_loader.load_merged_yaml", spy_yaml)
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
    monkeypatch.setattr("core.platform.mod_loader.MODS_STATE_FILE", state_file)
    set_mod_enabled("dragonborn_pack", True)
    assert get_enabled_mod_ids() == frozenset({"dragonborn_pack"})
    set_mod_enabled("dragonborn_pack", False)
    assert get_enabled_mod_ids() == frozenset()


def test_mod_enable_conflict_blocks_second_mod(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    for mod_id, conflicts in (
        ("mod_a", []),
        ("mod_b", ["mod_a"]),
    ):
        mod_path = mods_dir / mod_id
        mod_path.mkdir()
        lines = [f"id: {mod_id}", "name: {ru: Test}", "version: '1.0'"]
        if conflicts:
            lines.append(f"conflicts: {conflicts}")
        (mod_path / "manifest.yaml").write_text("\n".join(lines) + "\n")
    monkeypatch.setattr("core.platform.mod_loader.MODS_DIR", mods_dir)
    state_file = tmp_path / "mods_state.json"
    monkeypatch.setattr("core.platform.mod_loader.MODS_STATE_FILE", state_file)

    assert set_mod_enabled("mod_a", True) is None
    error = set_mod_enabled("mod_b", True)
    assert error is not None
    assert error.get("key") == "mods.error_conflicts"
    assert get_enabled_mod_ids() == frozenset({"mod_a"})


def test_mod_enable_requires_dependency(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    for mod_id, requires in (
        ("base_pack", []),
        ("addon_pack", ["base_pack"]),
    ):
        mod_path = mods_dir / mod_id
        mod_path.mkdir()
        lines = [f"id: {mod_id}", "name: {ru: Test}", "version: '1.0'"]
        if requires:
            lines.append(f"requires: {requires}")
        (mod_path / "manifest.yaml").write_text("\n".join(lines) + "\n")
    monkeypatch.setattr("core.platform.mod_loader.MODS_DIR", mods_dir)
    state_file = tmp_path / "mods_state.json"
    monkeypatch.setattr("core.platform.mod_loader.MODS_STATE_FILE", state_file)

    error = mod_enable_error("addon_pack")
    assert error is not None
    assert error.get("key") == "mods.error_requires"

    assert set_mod_enabled("base_pack", True) is None
    assert set_mod_enabled("addon_pack", True) is None
    assert get_enabled_mod_ids() == frozenset({"base_pack", "addon_pack"})


def test_mod_overlay_delete_and_replace_entity(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import json

    from core.platform.mod_loader import load_merged_yaml

    catalog = tmp_path / "database" / "races" / "races.yaml"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(
        "\n".join(
            [
                "races:",
                "  human:",
                "    name:",
                "      ru: Человек",
                "  remove_me:",
                "    name:",
                "      ru: Удалить",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    mod_id = "homebrew_races"
    mod_dir = tmp_path / "mods" / mod_id
    mod_dir.mkdir(parents=True)
    (mod_dir / "manifest.yaml").write_text(
        "\n".join(
            [
                f"id: {mod_id}",
                "name: {ru: Homebrew}",
                "version: '1.0'",
                "overlays:",
                f"  - target: {catalog.as_posix()}",
                "    path: overlay.yaml",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (mod_dir / "overlay.yaml").write_text(
        "\n".join(
            [
                "delete:",
                "  races:",
                "    - remove_me",
                "replace_entity:",
                "  races:",
                "    human:",
                "      name:",
                "        ru: Люди",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    state_path = tmp_path / "mods_state.json"
    state_path.write_text(json.dumps({"enabled": [mod_id]}), encoding="utf-8")
    monkeypatch.setattr("core.platform.mod_loader.MODS_DIR", tmp_path / "mods")
    monkeypatch.setattr("core.platform.mod_loader.MODS_STATE_FILE", state_path)

    merged = load_merged_yaml(catalog)
    races = merged.get("races", {})
    assert "remove_me" not in races
    assert races["human"]["name"]["ru"] == "Люди"
