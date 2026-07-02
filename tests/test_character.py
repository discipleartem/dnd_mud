"""Тесты персонажей: бонусы, генерация stats, save/load."""

import json
from pathlib import Path

import pytest

import core.character as character_mod
from core.character_storage import load_characters
from core.models import Character
from core.slug import make_save_slug


@pytest.mark.parametrize(
    "race_id,subrace_id,expected_bonuses",
    [
        (
            "human",
            "standard",
            dict.fromkeys(
                [
                    "strength",
                    "dexterity",
                    "constitution",
                    "intelligence",
                    "wisdom",
                    "charisma",
                ],
                1,
            ),
        ),
        ("elf", None, None),
    ],
)
def test_race_bonuses(
    race_id: str,
    subrace_id: str | None,
    expected_bonuses: dict[str, int] | None,
) -> None:
    if expected_bonuses is not None:
        assert (
            character_mod.get_race_bonuses(race_id, subrace_id)
            == expected_bonuses
        )
    else:
        assert character_mod.get_race_bonuses(race_id, subrace_id)


def test_generate_stats_and_point_buy() -> None:
    values = [15, 14, 13, 12, 10, 8]
    assert (
        character_mod.generate_stats_standard_array(values, "elf")["dexterity"]
        == 16
    )
    assert character_mod.point_buy_total_cost([8, 8, 8, 8, 8, 8]) == 0
    stats = dict.fromkeys(character_mod.STAT_NAMES, 8)
    assert character_mod.can_assign_point_buy_value(stats, "strength", 15)


def test_save_character_roundtrip(characters_dir: Path) -> None:
    stats = dict.fromkeys(character_mod.STAT_NAMES, 12)
    saved = character_mod.save_character(
        name="Hero",
        race_id="human",
        class_id="fighter",
        difficulty="normal",
        stats=stats,
        subclass_id="champion",
        skills=["athletics"],
        background_id="soldier",
        feat_ids=["resilient"],
        feat_choices={"resilient": {"ability": "constitution"}},
    )
    assert saved.level == 1
    assert saved.experience == 0
    loaded = character_mod.load_characters().characters[-1]
    assert loaded.skills == ["athletics"]
    with open(
        characters_dir / f"{saved.save_slug}.json", encoding="utf-8"
    ) as f:
        data = json.load(f)
    assert data["background_id"] == "soldier"


def test_save_character_easy_start_level_xp(characters_dir: Path) -> None:
    stats = dict.fromkeys(character_mod.STAT_NAMES, 12)
    saved = character_mod.save_character(
        name="EasyHero",
        race_id="human",
        class_id="fighter",
        difficulty="easy",
        stats=stats,
    )
    assert saved.level == 3
    assert saved.experience == 900


def test_character_json_uses_canonical_field_names() -> None:
    char = Character(
        name="Hero",
        race="human",
        class_id="fighter",
        subclass_id="champion",
        background_id="soldier",
    )
    data = char.to_dict()
    assert "subclass_id" in data
    assert "background_id" in data
    assert "subclass" not in data
    assert "background" not in data
    restored = Character.from_dict(data)
    assert restored.subclass_id == "champion"
    assert restored.background_id == "soldier"


def test_starting_max_hp_and_hardcore(
    characters_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stats = dict.fromkeys(character_mod.STAT_NAMES, 10)
    stats["constitution"] = 8
    saved = character_mod.save_character(
        name="LowCon",
        race_id="human",
        class_id="bard",
        stats=stats,
        difficulty="normal",
    )
    assert saved.max_hp == 7
    assert saved.current_hp == saved.max_hp
    stats["constitution"] = 14
    monkeypatch.setattr(
        "core.progression.roll",
        lambda count, sides, modifier=0: 5 + modifier,
    )
    hard = character_mod.save_character(
        name="HardHero",
        race_id="human",
        class_id="fighter",
        difficulty="hardcore",
        stats=stats,
    )
    assert hard.max_hp == 7


def test_hardcore_l1_hp_floor_on_create(
    characters_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """HardCore на 1 ур.: save_character применяет пол max(1, бросок + CON)."""
    stats = dict.fromkeys(character_mod.STAT_NAMES, 10)
    stats["constitution"] = 8  # модификатор −1
    monkeypatch.setattr(
        "core.progression.roll",
        lambda count, sides, modifier=0: 1 + modifier,
    )
    saved = character_mod.save_character(
        name="HardLow",
        race_id="human",
        class_id="bard",
        stats=stats,
        difficulty="hardcore",
    )
    assert saved.max_hp == 1
    assert saved.current_hp == 1


def test_make_save_slug_and_slug_collision(characters_dir: Path) -> None:
    assert make_save_slug("Герой") == "geroy"
    first = character_mod.save_character(
        name="Hero", race_id="human", class_id="fighter"
    )
    second = character_mod.save_character(
        name="Hero", race_id="elf", class_id="rogue"
    )
    assert first.save_slug == "hero"
    assert second.save_slug == "hero_2"
    assert character_mod.delete_character("hero") is True


def test_load_characters_skips_invalid_saves(characters_dir: Path) -> None:
    characters_dir.mkdir(parents=True, exist_ok=True)
    (characters_dir / "bad.json").write_text("{not json", encoding="utf-8")
    result = load_characters()
    assert result.characters == ()
    assert result.corrupt_save_warnings == ("bad",)
