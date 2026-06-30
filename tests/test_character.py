"""Тесты персонажей: бонусы, генерация stats, save/load."""

import json
from pathlib import Path
from typing import Literal

import pytest

import core.character as character_mod
from core.character_storage import load_characters
from core.progression import max_hp_for_level


@pytest.mark.parametrize(
    "race_id,subrace_id,expected_bonuses,mechanics",
    [
        (
            "human",
            "variant_human",
            {},
            {
                "count": 2,
                "value": 1,
                "choice": True,
                "allow_duplicates": False,
            },
        ),
        (
            "human",
            None,
            {
                "strength": 1,
                "dexterity": 1,
                "constitution": 1,
                "intelligence": 1,
                "wisdom": 1,
                "charisma": 1,
            },
            None,
        ),
        ("elf", None, None, None),
    ],
)
def test_race_bonus_and_choice_mechanics(
    race_id: str,
    subrace_id: str | None,
    expected_bonuses: dict[str, int] | None,
    mechanics: dict[str, object] | None,
) -> None:
    if race_id == "human" and subrace_id is None:
        assert character_mod.get_race_bonuses("human") == expected_bonuses
        return
    if expected_bonuses is not None:
        assert (
            character_mod.get_race_bonuses(race_id, subrace_id)
            == expected_bonuses
        )
    choice = character_mod.get_choice_ability_bonus_mechanics(
        race_id, subrace_id
    )
    if mechanics is None:
        assert choice is None
    else:
        assert choice is not None
        for key, value in mechanics.items():
            assert choice[key] == value


def test_generate_stats_and_point_buy() -> None:
    values = [15, 14, 13, 12, 10, 8]
    assert (
        character_mod.generate_stats_standard_array(values, "elf")["dexterity"]
        == 16
    )
    stats = dict.fromkeys(character_mod.STAT_NAMES, 8)
    assert character_mod.can_assign_point_buy_value(stats, "strength", 15)
    stats["strength"] = stats["dexterity"] = stats["constitution"] = 15
    assert (
        character_mod.can_assign_point_buy_value(stats, "intelligence", 15)
        is False
    )


@pytest.mark.parametrize(
    "difficulty,level,subclass_id",
    [("easy", 3, "champion"), ("normal", 1, "champion")],
)
def test_save_character_start_level(
    characters_dir: Path,
    difficulty: Literal["easy", "normal", "hardcore"],
    level: int,
    subclass_id: str,
) -> None:
    stats = dict.fromkeys(character_mod.STAT_NAMES, 12)
    saved = character_mod.save_character(
        name="Hero",
        race_id="human",
        class_id="fighter",
        difficulty=difficulty,
        stats=stats,
        subclass_id=subclass_id,
    )
    assert saved.level == level
    if difficulty == "easy":
        assert saved.max_hp > max_hp_for_level("fighter", stats, 1)


def test_save_and_load_character(characters_dir: Path) -> None:
    saved = character_mod.save_character(
        name="Hero",
        race_id="human",
        class_id="fighter",
        stats=dict.fromkeys(character_mod.STAT_NAMES, 12),
        skills=["athletics"],
        languages=["common"],
        background_id="soldier",
        feat_ids=["resilient"],
        feat_choices={"resilient": {"ability": "constitution"}},
    )
    assert saved.save_slug == "hero"
    assert saved.stats["constitution"] == 13
    loaded = character_mod.load_characters().characters[0]
    assert loaded.skills == ["athletics"]
    with open(characters_dir / "hero.json", encoding="utf-8") as f:
        assert json.load(f)["background"] == "soldier"


def test_slug_collision_and_delete(characters_dir: Path) -> None:
    first = character_mod.save_character(
        name="Hero", race_id="human", class_id="fighter"
    )
    second = character_mod.save_character(
        name="Hero", race_id="elf", class_id="rogue"
    )
    assert first.save_slug == "hero"
    assert second.save_slug == "hero_2"
    assert character_mod.delete_character("hero") is True
    assert len(character_mod.load_characters().characters) == 1


def test_hardcore_creation_uses_rolls(
    characters_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stats = dict.fromkeys(character_mod.STAT_NAMES, 10)
    stats["constitution"] = 14
    monkeypatch.setattr(
        "core.progression.roll",
        lambda count, sides, modifier=0: 5 + modifier,
    )
    saved = character_mod.save_character(
        name="HardHero",
        race_id="human",
        class_id="fighter",
        difficulty="hardcore",
        stats=stats,
    )
    assert saved.max_hp == 7


def test_load_characters_skips_invalid_saves(characters_dir: Path) -> None:
    characters_dir.mkdir(parents=True, exist_ok=True)
    (characters_dir / "bad.json").write_text("{not json", encoding="utf-8")
    result = load_characters()
    assert result.characters == ()
    assert result.corrupt_save_warnings == ("bad",)


def test_save_character_derives_proficiencies(characters_dir: Path) -> None:
    saved = character_mod.save_character(
        name="AutoProf",
        race_id="human",
        class_id="fighter",
        stats=dict.fromkeys(character_mod.STAT_NAMES, 10),
    )
    assert "simple" in saved.weapon_proficiencies
    assert saved.armor_proficiencies
