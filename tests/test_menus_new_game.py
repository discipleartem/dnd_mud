"""Тесты UI меню — новая игра."""

from core.character_storage import LoadCharactersResult
from core.models import Adventure, Character
from ui.menus import (
    _creation_steps,
    _deps,
    new_game,
)


def test_select_character_create_via_enter(monkeypatch, capsys, ru_strings):
    """Enter без ввода на пункте «Создать» возвращает 'create'."""
    character = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    monkeypatch.setattr(
        _deps,
        "load_characters",
        lambda: LoadCharactersResult(characters=(character,)),
    )

    from ui.input_handler import get_int_input

    monkeypatch.setattr(_deps, "get_int_input", get_int_input)
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    assert new_game._select_character(ru_strings, [character]) == "create"
    output = capsys.readouterr().out
    assert "[Enter]" in output
    assert "Создать нового персонажа" in output
    assert "2. Создать" not in output


def test_select_adventure_filters_by_character_difficulty(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    """Недоступные приключения показываются отдельным блоком."""
    character = Character(
        name="Normal Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    available = Adventure(
        id="tutorial",
        name={"ru": "Обучение"},
        description="desc",
    )
    blocked = Adventure(
        id="hc_only",
        name={"ru": "HardCore Quest"},
        description="desc",
        hardcore_only=True,
    )

    monkeypatch.setattr(_deps, "load_adventures", lambda: [available, blocked])
    patch_int_input(monkeypatch, [0])

    result = new_game._select_adventure(ru_strings, "ru", character)
    output = capsys.readouterr().out

    assert result is None
    assert "Обучение" in output
    assert "HardCore Quest" in output
    assert "Недоступные приключения" in output
    assert "требуется режим HardCore" in output


def test_select_adventure_choice_returns_adventure(
    monkeypatch, ru_strings, patch_int_input
):
    """Выбор доступного приключения возвращает объект Adventure."""
    character = Character(
        name="Normal Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    tutorial = Adventure(
        id="tutorial",
        name={"ru": "Обучение"},
        description="desc",
    )

    monkeypatch.setattr(_deps, "load_adventures", lambda: [tutorial])
    patch_int_input(monkeypatch, [1])

    result = new_game._select_adventure(ru_strings, "ru", character)

    assert result is not None
    assert result.id == "tutorial"


def test_new_game_corrupt_warning_shown_once_per_visit(
    monkeypatch, capsys, ru_strings
):
    """Предупреждение о битых сейвах — один раз за визит new game."""
    monkeypatch.setattr(
        _deps,
        "load_characters",
        lambda: LoadCharactersResult(
            characters=(), corrupt_save_warnings=("Broken",)
        ),
    )
    monkeypatch.setattr(
        _creation_steps,
        "show_create_character_flow",
        lambda _strings, _language: None,
    )

    new_game.show_new_game_flow(ru_strings, {"language": "ru"})
    output = capsys.readouterr().out

    assert output.count("Не удалось загрузить сохранения") == 1
    assert "Broken" in output


def test_new_game_no_characters_goes_to_create(monkeypatch):
    """Без персонажей — сразу создание."""
    calls = {"select": 0, "create": 0}

    def create_flow(strings, language="ru"):
        calls["create"] += 1

    monkeypatch.setattr(
        _deps, "load_characters", lambda: LoadCharactersResult.empty()
    )
    monkeypatch.setattr(
        _creation_steps, "show_create_character_flow", create_flow
    )

    new_game.show_new_game_flow({}, {"language": "ru"})

    assert calls == {"select": 0, "create": 1}


def test_new_game_back_navigation_and_cached_list(monkeypatch):
    """Назад из приключения; список персонажей не перечитывается."""
    calls = {"load": 0, "character": 0, "adventure": 0}
    character = Character(
        name="Test Hero",
        race="human",
        class_id="fighter",
    )

    def load_characters():
        calls["load"] += 1
        return LoadCharactersResult(characters=(character,))

    def select_character(strings, characters, language="ru"):
        calls["character"] += 1
        return character if calls["character"] == 1 else None

    def select_adventure(strings, language, char):
        calls["adventure"] += 1
        return None

    monkeypatch.setattr(_deps, "load_characters", load_characters)
    monkeypatch.setattr(new_game, "_select_character", select_character)
    monkeypatch.setattr(new_game, "_select_adventure", select_adventure)

    new_game.show_new_game_flow({}, {"language": "ru"})

    assert calls == {"load": 1, "character": 2, "adventure": 1}
