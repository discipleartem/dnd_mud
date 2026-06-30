"""Тесты моделей Character и Adventure."""

import core.adventure as adventure_mod
from core.models import Adventure, Character


def test_character_round_trip_with_subrace():
    """Character.to_dict/from_dict сохраняет subrace и class."""
    original = Character(
        name="Test",
        race="human",
        class_id="fighter",
        subrace="variant_human",
        stats={"strength": 10},
        current_hp=12,
        save_slug="test",
    )
    restored = Character.from_dict(original.to_dict())

    assert restored.subrace == "variant_human"
    assert restored.class_id == "fighter"
    assert restored.name == "Test"
    assert restored.save_slug == "test"


def test_character_from_dict_reads_class_id():
    """from_dict читает class_id; legacy-ключ class — fallback."""
    from_class_id = Character.from_dict(
        {"name": "X", "race": "human", "class_id": "wizard"}
    )
    from_legacy = Character.from_dict(
        {"name": "Y", "race": "elf", "class": "rogue"}
    )

    assert from_class_id.class_id == "wizard"
    assert from_legacy.class_id == "rogue"


def test_character_from_dict_defaults():
    """from_dict подставляет значения по умолчанию."""
    character = Character.from_dict({})

    assert character.name == ""
    assert character.race == ""
    assert character.class_id == ""
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


def test_load_adventures_from_yaml(tmp_path, monkeypatch):
    """load_adventures читает список из YAML."""
    adventures_file = tmp_path / "adventures.yaml"
    adventures_file.write_text(
        """
adventures:
  - id: tutorial
    name:
      ru: Обучение
      en: Tutorial
    description: desc
    hardcore_only: false
  - id: hc_only
    name: HardCore Quest
    hardcore_only: true
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(adventure_mod, "ADVENTURES_FILE", adventures_file)

    adventures = adventure_mod.load_adventures()

    assert len(adventures) == 2
    assert adventures[0].id == "tutorial"
    assert adventures[0].get_name("ru") == "Обучение"
    assert adventures[1].hardcore_only is True


def test_load_adventures_missing_file_returns_empty(tmp_path, monkeypatch):
    """Отсутствующий файл — пустой список."""
    missing = tmp_path / "missing.yaml"
    monkeypatch.setattr(adventure_mod, "ADVENTURES_FILE", missing)

    assert adventure_mod.load_adventures() == []
