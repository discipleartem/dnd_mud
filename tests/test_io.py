"""Тесты общих функций чтения YAML и JSON."""

from pathlib import Path

from core.io import CatalogLoadError, load_json, load_yaml


def test_load_yaml_missing_file_returns_default(tmp_path: Path) -> None:
    path = tmp_path / "missing.yaml"
    assert load_yaml(path, {"key": "value"}) == {"key": "value"}


def test_load_yaml_reads_valid_file(tmp_path: Path) -> None:
    path = tmp_path / "data.yaml"
    path.write_text("races:\n  human:\n    name: Human\n", encoding="utf-8")
    data = load_yaml(path)
    assert data["races"]["human"]["name"] == "Human"


def test_load_yaml_corrupt_file_returns_default(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(":\n  bad: [unclosed", encoding="utf-8")
    assert load_yaml(path, {"fallback": True}) == {"fallback": True}


def test_load_yaml_strict_raises_on_corrupt_file(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(":\n  bad: [unclosed", encoding="utf-8")
    try:
        load_yaml(path, strict=True)
        raised = False
    except CatalogLoadError:
        raised = True
    assert raised


def test_load_json_missing_file_returns_default(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"
    assert load_json(path, {"language": "ru"}) == {"language": "ru"}


def test_load_json_reads_valid_file(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text('{"language": "en"}', encoding="utf-8")
    assert load_json(path)["language"] == "en"


def test_load_json_corrupt_file_returns_default(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    assert load_json(path, {"language": "ru"}) == {"language": "ru"}
