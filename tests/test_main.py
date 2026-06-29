"""Smoke-тест точки входа."""

from importlib.metadata import PackageNotFoundError, version

import main


def test_main_imports_and_version():
    assert isinstance(main.VERSION, str) and main.VERSION
    assert callable(main.main)
    try:
        assert version("dnd_mud") == main.VERSION
    except PackageNotFoundError:
        assert main._read_version_from_pyproject() == main.VERSION


def test_main_exits_on_menu_choice_zero(monkeypatch, capsys):
    """choice == 0 завершает главный цикл меню."""
    monkeypatch.setattr(main, "load_settings", lambda: {"language": "ru"})
    monkeypatch.setattr(
        main,
        "load_strings",
        lambda lang: {"info": {"goodbye": "Bye"}},
    )
    monkeypatch.setattr(main, "show_welcome_screen", lambda *args: None)
    monkeypatch.setattr(main, "show_main_menu", lambda strings: 0)
    monkeypatch.setattr(main, "init", lambda **kwargs: None)

    assert main.main() == 0
    assert "Bye" in capsys.readouterr().out
