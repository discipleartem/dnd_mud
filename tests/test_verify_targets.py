"""Тесты scripts/verify_targets.py — маппинг source → pytest/lint."""

from __future__ import annotations

import scripts.verify_targets as vt


def test_core_and_ui_mapping() -> None:
    assert vt.source_to_tests("core/difficulty.py") == [
        "tests/test_difficulty.py"
    ]
    assert vt.source_to_tests("core/feat_visibility.py") == [
        "tests/test_feats.py"
    ]
    assert vt.source_to_tests("core/scenario_actions.py") == [
        "tests/test_class_features.py"
    ]
    assert vt.source_to_tests("ui/menus/class_features.py") == [
        "tests/test_class_features.py"
    ]
    assert vt.source_to_tests("ui/menus/scenario_flow.py") == [
        "tests/test_scenario.py"
    ]
    assert vt.source_to_tests("ui/menus/stats/stats_flow.py") == [
        "tests/test_menus_stats.py"
    ]
    assert vt.source_to_tests("ui/menus/characters_menu.py") == [
        "tests/test_menus_character.py"
    ]


def test_database_and_infra_fallbacks() -> None:
    tests = vt.source_to_tests("database/races/races.yaml")
    assert "tests/test_mod_loader.py" in tests
    assert vt.requires_full_suite(["tests/conftest.py"]) is True
    lint, full = vt.resolve_lint_paths(["core/types.py"])
    assert full is True
    tests, full = vt.resolve_test_paths(["tools/unknown_helper.py"])
    assert full is True
