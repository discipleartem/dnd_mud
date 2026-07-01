"""Тесты core.scenario_actions."""

from pathlib import Path

from core.models import Character
from core.scenario_actions import apply_scenario_action, load_scenario


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
