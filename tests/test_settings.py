"""Тесты настроек."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_settings(tmp_path, monkeypatch):
    """Тест сохранения и загрузки настроек."""
    import core.settings as settings_mod

    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_mod, "SETTINGS_PATH", settings_file)

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


def test_settings_ignores_legacy_difficulty(tmp_path, monkeypatch):
    """Старое поле difficulty в JSON игнорируется."""
    import core.settings as settings_mod

    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(settings_mod, "SETTINGS_PATH", settings_file)

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
