"""Smoke-тест точки входа."""

from importlib.metadata import PackageNotFoundError, version

import main


def test_main_imports_and_version() -> None:
    assert isinstance(main.VERSION, str) and main.VERSION
    assert callable(main.main)
    try:
        assert version("dnd_mud") == main.VERSION
    except PackageNotFoundError:
        assert main._read_version_from_pyproject() == main.VERSION
