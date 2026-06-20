"""Smoke-тест точки входа."""

from importlib.metadata import version

import main


def test_main_imports_and_version():
    assert version("dnd_mud") == main.VERSION
    assert callable(main.main)
