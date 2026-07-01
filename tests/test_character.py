"""Тесты персонажей: бонусы, генерация stats, save/load."""

import json
from pathlib import Path
from typing import Any

import pytest

import core.character as character_mod
from core.character_storage import load_characters
from core.models import Character
from core.slug import make_save_slug


@pytest.mark.parametrize(
    "race_id,subrace_id,expected_bonuses,mechanics",
    [
        (
            "human",
            "variant_human",
            {},
            {
                "count": 2,
                "amount": 1,
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
    full_pool = [15, 14, 13, 12, 10, 8]
    assert character_mod.remaining_standard_array_pool([]) == full_pool
    assert character_mod.remaining_standard_array_pool([15, 14]) == [
        13,
        12,
        10,
        8,
    ]
    assert character_mod.point_buy_total_cost([8, 8, 8, 8, 8, 8]) == 0
    assert character_mod.point_buy_total_cost([15, 15, 15, 8, 8, 8]) == 27
    stats = dict.fromkeys(character_mod.STAT_NAMES, 8)
    assert character_mod.can_assign_point_buy_value(stats, "strength", 15)
    stats["strength"] = stats["dexterity"] = stats["constitution"] = 15
    assert (
        character_mod.can_assign_point_buy_value(stats, "intelligence", 15)
        is False
    )


def test_save_character_start_level(characters_dir: Path) -> None:
    stats = dict.fromkeys(character_mod.STAT_NAMES, 12)
    saved = character_mod.save_character(
        name="Hero",
        race_id="human",
        class_id="fighter",
        difficulty="normal",
        stats=stats,
        subclass_id="champion",
    )
    assert saved.level == 1


@pytest.mark.parametrize(
    "name,class_id,extra_kwargs,json_checks,load_checks",
    [
        (
            "Hero",
            "fighter",
            {
                "skills": ["athletics"],
                "languages": ["common"],
                "background_id": "soldier",
                "feat_ids": ["resilient"],
                "feat_choices": {"resilient": {"ability": "constitution"}},
            },
            {"background_id": "soldier"},
            {"skills": ["athletics"], "slug": "hero", "con": 13},
        ),
        (
            "RogueHero",
            "rogue",
            {
                "skills": [
                    "stealth",
                    "perception",
                    "athletics",
                    "deception",
                ],
                "skill_expertise": ["stealth", "athletics"],
                "tool_expertise": [],
            },
            {},
            {
                "skill_expertise": ["stealth", "athletics"],
                "slug": "roguehero",
            },
        ),
        (
            "AutoProf",
            "fighter",
            {},
            {},
            {"weapon_prof": "simple"},
        ),
    ],
)
def test_save_character_persists_fields(
    characters_dir: Path,
    name: str,
    class_id: str,
    extra_kwargs: dict[str, Any],
    json_checks: dict[str, object],
    load_checks: dict[str, object],
) -> None:
    """Save/load сохраняет поля персонажа в JSON."""
    stat_value = 10 if name == "AutoProf" else 12
    stats = dict.fromkeys(character_mod.STAT_NAMES, stat_value)
    saved = character_mod.save_character(
        name=name,
        race_id="human",
        class_id=class_id,
        stats=stats,
        **extra_kwargs,
    )
    slug = str(load_checks.get("slug", saved.save_slug))
    if "con" in load_checks:
        assert saved.stats["constitution"] == load_checks["con"]
    if "skill_expertise" in load_checks:
        assert saved.skill_expertise == load_checks["skill_expertise"]
    if "weapon_prof" in load_checks:
        assert load_checks["weapon_prof"] in saved.weapon_proficiencies
        assert saved.armor_proficiencies
    loaded = character_mod.load_characters().characters[-1]
    if "skills" in load_checks:
        assert loaded.skills == load_checks["skills"]
    if "skill_expertise" in load_checks:
        assert loaded.skill_expertise == saved.skill_expertise
    with open(characters_dir / f"{slug}.json", encoding="utf-8") as f:
        data = json.load(f)
    for key, value in json_checks.items():
        assert data[key] == value
    if "skills" in extra_kwargs:
        assert data["skills"] == saved.skills


def test_starting_max_hp_floor_and_max_hp_field(characters_dir: Path) -> None:
    """HP на 1 уровне (normal): max(1, кость + CON), current_hp == max_hp."""
    stats = {
        "strength": 10,
        "dexterity": 10,
        "constitution": 8,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
    }
    saved = character_mod.save_character(
        name="LowCon",
        race_id="human",
        class_id="bard",
        stats=stats,
        difficulty="normal",
    )
    assert saved.max_hp == 7
    assert saved.current_hp == saved.max_hp
    assert saved.max_hp >= 1


def test_make_save_slug_transliterates_cyrillic() -> None:
    assert make_save_slug("Герой") == "geroy"


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
