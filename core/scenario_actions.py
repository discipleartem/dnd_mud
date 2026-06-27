"""Чистая логика действий YAML-сценариев (без UI)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.io import load_yaml
from core.models import Character
from core.progression import grant_experience, has_pending_level_up
from core.subclasses import needs_subclass_npc


@dataclass(frozen=True)
class ScenarioActionResult:
    """Результат action узла сценария для UI."""

    character: Character
    level_up_pending: bool = False
    pick_subclass: bool = False
    message_key: str | None = None


def load_scenario(script_file: str) -> dict[str, Any]:
    """Загрузить YAML сценария по пути из каталога приключений."""
    path = Path(script_file)
    data = load_yaml(path)
    scenario = data.get("scenario", {})
    if isinstance(scenario, dict):
        return scenario
    return {}


def apply_scenario_action(
    action: str,
    action_data: dict[str, Any],
    character: Character,
) -> ScenarioActionResult:
    """Выполнить action узла сценария без ввода/вывода."""
    if action == "grant_xp":
        amount = int(action_data.get("amount", 0))
        updated = grant_experience(character, amount)
        return ScenarioActionResult(
            character=updated,
            level_up_pending=has_pending_level_up(updated),
        )

    if action == "subclass_training":
        if character.subclass_id is not None:
            return ScenarioActionResult(
                character=character,
                message_key="characters_menu.subclass_trainer_already",
            )
        if needs_subclass_npc(character):
            return ScenarioActionResult(
                character=character, pick_subclass=True
            )
        key = str(
            action_data.get("message_key", "scenario.subclass_not_ready")
        )
        return ScenarioActionResult(character=character, message_key=key)

    return ScenarioActionResult(character=character)
