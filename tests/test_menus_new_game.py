"""Тесты UI меню — новая игра."""

from core.character_storage import LoadCharactersResult
from core.models import Adventure, Character
from ui.menus import _creation_steps, _deps, new_game


def test_select_adventure_filters_and_choice(
    monkeypatch, capsys, ru_strings, patch_int_input
):
    character = Character(
        name="Normal Hero",
        race="human",
        class_id="fighter",
        difficulty="normal",
    )
    available = Adventure(
        id="tutorial", name={"ru": "Обучение"}, description="desc"
    )
    blocked = Adventure(
        id="hc_only",
        name={"ru": "HardCore Quest"},
        description="desc",
        hardcore_only=True,
    )
    monkeypatch.setattr(_deps, "load_adventures", lambda: [available, blocked])
    patch_int_input(monkeypatch, [0])
    assert new_game._select_adventure(ru_strings, "ru", character) is None
    output = capsys.readouterr().out
    assert "Недоступные приключения" in output

    patch_int_input(monkeypatch, [1])
    monkeypatch.setattr(_deps, "load_adventures", lambda: [available])
    result = new_game._select_adventure(ru_strings, "ru", character)
    assert result is not None
    assert result.id == "tutorial"


def test_new_game_no_characters_goes_to_create(monkeypatch):
    calls = {"create": 0}

    def create_flow(strings, language="ru"):
        calls["create"] += 1

    monkeypatch.setattr(
        _deps, "load_characters", lambda: LoadCharactersResult.empty()
    )
    monkeypatch.setattr(
        _creation_steps, "show_create_character_flow", create_flow
    )
    new_game.show_new_game_flow({}, {"language": "ru"})
    assert calls["create"] == 1


def test_new_game_back_navigation_and_cached_list(monkeypatch):
    calls = {"load": 0, "character": 0, "adventure": 0}
    character = Character(name="Test Hero", race="human", class_id="fighter")

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
