"""Тесты загрузки приключений."""

import core.adventure as adventure_mod


def test_load_adventures_from_yaml(tmp_path, monkeypatch):
    """load_adventures читает список из YAML."""
    adventures_file = tmp_path / "adventures.yaml"
    adventures_file.write_text(
        """
adventures:
  - id: tutorial
    name:
      ru: Обучение
      en: Tutorial
    description: desc
    hardcore_only: false
  - id: hc_only
    name: HardCore Quest
    hardcore_only: true
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(adventure_mod, "ADVENTURES_FILE", adventures_file)

    adventures = adventure_mod.load_adventures()

    assert len(adventures) == 2
    assert adventures[0].id == "tutorial"
    assert adventures[0].get_name("ru") == "Обучение"
    assert adventures[1].hardcore_only is True


def test_load_adventures_missing_file_returns_empty(tmp_path, monkeypatch):
    """Отсутствующий файл — пустой список."""
    missing = tmp_path / "missing.yaml"
    monkeypatch.setattr(adventure_mod, "ADVENTURES_FILE", missing)

    assert adventure_mod.load_adventures() == []
