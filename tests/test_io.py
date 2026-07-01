"""Тесты общих функций чтения YAML и JSON."""

from pathlib import Path

import pytest

from core.io import CatalogLoadError, load_json, load_yaml


def test_load_yaml_and_json_happy_path(tmp_path: Path) -> None:
    yaml_path = tmp_path / "data.yaml"
    yaml_path.write_text("key: value\n", encoding="utf-8")
    assert load_yaml(yaml_path)["key"] == "value"
    json_path = tmp_path / "settings.json"
    json_path.write_text('{"language": "en"}', encoding="utf-8")
    assert load_json(json_path)["language"] == "en"


def test_load_corrupt_files_return_default(tmp_path: Path) -> None:
    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text(":\n  bad: [unclosed", encoding="utf-8")
    assert load_yaml(yaml_path, {"fallback": True}) == {"fallback": True}
    json_path = tmp_path / "bad.json"
    json_path.write_text("{not json", encoding="utf-8")
    assert load_json(json_path, {"language": "ru"}) == {"language": "ru"}


def test_load_yaml_strict_raises_on_corrupt_file(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(":\n  bad: [unclosed", encoding="utf-8")
    with pytest.raises(CatalogLoadError):
        load_yaml(path, strict=True)
