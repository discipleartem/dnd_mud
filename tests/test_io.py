"""Тесты общих функций чтения YAML и JSON."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from core.io import CatalogLoadError, load_json, load_yaml


@pytest.mark.parametrize(
    "loader,filename,content,default,expected_key",
    [
        (
            load_yaml,
            "data.yaml",
            "key: value\n",
            None,
            ("key", "value"),
        ),
        (
            load_json,
            "settings.json",
            '{"language": "en"}',
            None,
            ("language", "en"),
        ),
    ],
)
def test_load_valid_file(
    loader: Callable[..., dict[str, Any]],
    filename: str,
    content: str,
    default: dict[str, str] | None,
    expected_key: tuple[str, str],
    tmp_path: Path,
) -> None:
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
    data = loader(path, default) if default is not None else loader(path)
    assert data[expected_key[0]] == expected_key[1]


@pytest.mark.parametrize(
    "loader,filename,bad_content,default",
    [
        (load_yaml, "bad.yaml", ":\n  bad: [unclosed", {"fallback": True}),
        (load_json, "bad.json", "{not json", {"language": "ru"}),
    ],
)
def test_load_corrupt_file_returns_default(
    loader: Callable[..., dict[str, Any]],
    filename: str,
    bad_content: str,
    default: dict[str, object],
    tmp_path: Path,
) -> None:
    path = tmp_path / filename
    path.write_text(bad_content, encoding="utf-8")
    assert loader(path, default) == default


def test_load_yaml_strict_raises_on_corrupt_file(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(":\n  bad: [unclosed", encoding="utf-8")
    with pytest.raises(CatalogLoadError):
        load_yaml(path, strict=True)
