"""Тесты UI повышения уровня."""

from dataclasses import replace

import pytest

from core.models import Character
from ui.menus import level_up as level_up_menu


def _fighter_level_three() -> Character:
    return Character(
        name="Hero",
        race="human",
        class_id="fighter",
        level=3,
        stats={"constitution": 14, "strength": 16},
        current_hp=28,
        max_hp=28,
        experience=2700,
        difficulty="normal",
    )


def test_run_pending_level_ups_tough_retroactive_on_new_acquire(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ретроактивный HP от Tough — только при первом получении черты."""
    char = _fighter_level_three()

    def fake_asi(strings, character, new_level, language="ru"):
        new_feats = list(character.feat_ids) + ["tough"]
        updated = replace(
            character,
            stats=character.stats.copy(),
            feat_ids=new_feats,
        )
        return updated, updated.stats, new_feats, {}, "feat:tough"

    monkeypatch.setattr(level_up_menu, "select_level_up_feat_or_asi", fake_asi)
    monkeypatch.setattr(level_up_menu, "_press_enter", lambda strings: None)
    monkeypatch.setattr(
        level_up_menu, "_print_screen_header", lambda strings: None
    )

    result = level_up_menu.run_pending_level_ups({}, char)

    assert result.level == 4
    assert result.feat_ids == ["tough"]
    # +8 за ур. 4 (d10+CON) + 8 ретроактивно от Tough
    assert result.max_hp == 44


def test_run_pending_level_ups_preview_matches_applied_hp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Превью max HP учитывает con_bonus и tough_bonus."""
    char = _fighter_level_three()
    preview_gain: list[int] = []

    def capture_screen(strings, character, new_level, breakdown, extra_hp=0):
        preview_gain.append(breakdown.total + extra_hp)

    def fake_asi(strings, character, new_level, language="ru"):
        stats = character.stats.copy()
        stats["constitution"] = 16
        new_feats = list(character.feat_ids) + ["tough"]
        updated = replace(character, stats=stats, feat_ids=new_feats)
        return updated, stats, new_feats, {}, "feat:tough"

    monkeypatch.setattr(level_up_menu, "select_level_up_feat_or_asi", fake_asi)
    monkeypatch.setattr(level_up_menu, "_press_enter", lambda strings: None)
    monkeypatch.setattr(
        level_up_menu, "_print_screen_header", lambda strings: None
    )
    monkeypatch.setattr(
        level_up_menu, "_print_level_up_screen", capture_screen
    )

    result = level_up_menu.run_pending_level_ups({}, char)

    assert preview_gain == [result.max_hp - char.max_hp]


def test_run_pending_level_ups_no_tough_retroactive_if_already_had(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Уже имея Tough, ASI не даёт повторный ретроактивный бонус."""
    char = replace(_fighter_level_three(), feat_ids=["tough"])

    def fake_asi(strings, character, new_level, language="ru"):
        stats = character.stats.copy()
        stats["strength"] = 18
        updated = replace(character, stats=stats)
        return (
            updated,
            stats,
            list(character.feat_ids),
            {},
            "asi",
        )

    monkeypatch.setattr(level_up_menu, "select_level_up_feat_or_asi", fake_asi)
    monkeypatch.setattr(level_up_menu, "_press_enter", lambda strings: None)
    monkeypatch.setattr(
        level_up_menu, "_print_screen_header", lambda strings: None
    )

    result = level_up_menu.run_pending_level_ups({}, char)

    assert result.level == 4
    assert result.asi_choices.get("4") == "asi"
    # +8 за уровень 4, без ретроактивных +8 от Tough
    assert result.max_hp == 38
