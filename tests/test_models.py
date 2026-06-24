"""Тесты моделей Character и Adventure."""

from core.models import Adventure, Character


def test_character_round_trip_with_subrace():
    """Character.to_dict/from_dict сохраняет subrace и class."""
    original = Character(
        name="Test",
        race="human",
        class_name="fighter",
        subrace="variant_human",
        stats={"strength": 10},
        current_hp=12,
        save_slug="test",
    )
    restored = Character.from_dict(original.to_dict())

    assert restored.subrace == "variant_human"
    assert restored.class_name == "fighter"
    assert restored.name == "Test"
    assert restored.save_slug == "test"


def test_character_from_dict_defaults():
    """from_dict подставляет значения по умолчанию."""
    character = Character.from_dict({})

    assert character.name == ""
    assert character.race == ""
    assert character.class_name == ""
    assert character.level == 1
    assert character.stats == {}
    assert character.difficulty == "normal"
    assert character.subrace is None


def test_adventure_get_name_localized():
    """get_name возвращает имя на нужном языке или fallback."""
    localized = Adventure(id="a1", name={"ru": "Обучение", "en": "Tutorial"})
    plain = Adventure(id="a2", name="Plain Name")

    assert localized.get_name("ru") == "Обучение"
    assert localized.get_name("en") == "Tutorial"
    assert localized.get_name("de") == "Tutorial"
    assert plain.get_name("ru") == "Plain Name"


def test_adventure_from_dict_restrictions():
    """from_dict читает ограничения сложности."""
    adventure = Adventure.from_dict(
        {
            "id": "hc",
            "name": "HC",
            "hardcore_only": True,
            "allowed_game_difficulties": ["normal"],
            "min_level": 3,
        }
    )

    assert adventure.hardcore_only is True
    assert adventure.allowed_game_difficulties == ["normal"]
    assert adventure.min_level == 3
