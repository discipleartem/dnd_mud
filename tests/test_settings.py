"""Тесты настроек."""

import json

import core.settings as settings_mod


def test_settings_save_and_load(settings_file):
    """save_settings и load_settings сохраняют язык."""
    settings_mod.save_settings("en")

    loaded = settings_mod.load_settings()
    assert loaded["language"] == "en"
    assert "difficulty" not in loaded

    settings_mod.save_settings("ru")

    loaded = settings_mod.load_settings()
    assert loaded["language"] == "ru"

    with open(settings_file, encoding="utf-8") as f:
        saved = json.load(f)
    assert saved["schema_version"] == 1
    assert "difficulty" not in saved
    assert "hardcore" not in saved


def test_settings_ignores_unknown_keys(settings_file):
    """Неизвестные поля в JSON настроек игнорируются."""
    settings_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "language": "ru",
                "hardcore": True,
                "difficulty": "hardcore",
            }
        ),
        encoding="utf-8",
    )

    loaded = settings_mod.load_settings()
    assert loaded == {"language": "ru"}
