"""Тесты моделей, приключений, сценариев и предысторий."""

from pathlib import Path

import pytest

import core.adventure as adventure_mod
from core.backgrounds import get_background_skills, load_backgrounds
from core.models import Adventure, Character
from core.scenario_actions import apply_scenario_action, load_scenario
from core.skills import PHB_SKILL_IDS

pytestmark = pytest.mark.usefixtures("catalog_caches_cleared")


def test_character_round_trip_with_subrace() -> None:
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
    assert restored.save_slug == "test"


def test_character_and_adventure_from_dict() -> None:
    character = Character.from_dict(
        {"name": "X", "race": "human", "class_id": "wizard"}
    )
    assert character.class_id == "wizard"
    assert Character.from_dict({}).level == 1

    localized = Adventure(id="a1", name={"ru": "Обучение", "en": "Tutorial"})
    assert localized.get_name("ru") == "Обучение"
    adventure = Adventure.from_dict(
        {
            "id": "hc",
            "name": "HC",
            "hardcore_only": True,
            "min_level": 3,
        }
    )
    assert adventure.hardcore_only is True
    assert adventure.min_level == 3


def test_load_adventures_from_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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
    assert adventures[0].get_name("ru") == "Обучение"
    assert adventures[1].hardcore_only is True


def test_load_scenario_reads_yaml(tmp_path: Path) -> None:
    script = tmp_path / "demo.yaml"
    yaml_text = (
        "scenario:\n"
        "  start_node: intro\n"
        "  nodes:\n"
        "    intro:\n"
        "      description: Hi\n"
    )
    script.write_text(yaml_text, encoding="utf-8")
    data = load_scenario(str(script))
    assert data["start_node"] == "intro"
    assert "intro" in data["nodes"]


def test_apply_scenario_action_unknown_returns_unchanged() -> None:
    char = Character(name="Hero", race="human", class_id="fighter")
    result = apply_scenario_action("unknown", {}, char)
    assert result.character is char
    assert result.level_up_pending is False


def test_background_skills_valid_and_acolyte_name() -> None:
    names = {bg["id"]: bg["name"] for bg in load_backgrounds("ru")}
    assert names["acolyte"] == "Прислужник"
    for bg in load_backgrounds("ru"):
        for skill_id in get_background_skills(str(bg["id"])):
            assert skill_id in PHB_SKILL_IDS
