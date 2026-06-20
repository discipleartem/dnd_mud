"""Smoke-тест точки входа."""

import main


def test_main_imports_and_version():
    assert main.VERSION == "0.1.0"
    assert callable(main.main)
