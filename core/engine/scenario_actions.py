"""Чистая логика действий YAML-сценариев (без UI)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.character.models import Character
from core.platform.io import load_yaml
from core.progression.class_progression import (
    needs_class_feature_picks,
    needs_subclass_npc,
)
from core.progression.xp_levels import (
    grant_experience,
    has_pending_level_up,
)
from core.types import GameDifficulty


@dataclass(frozen=True)
class ScenarioActionResult:
    """Результат action узла сценария для UI."""

    character: Character
    level_up_pending: bool = False
    pick_subclass: bool = False
    apply_class_features: bool = False
    message_key: str | None = None
    message_params: dict[str, Any] | None = None


def load_scenario(script_file: str) -> dict[str, Any]:
    """Загрузить YAML сценария по пути из каталога приключений."""
    path = Path(script_file)
    data = load_yaml(path)
    scenario = data.get("scenario", {})
    if isinstance(scenario, dict):
        return scenario
    return {}


def _check_message(
    *,
    prefix: str,
    check: dict[str, object],
    dc: int | None,
) -> tuple[str, dict[str, object]]:
    bonus = check["modifier"]
    if dc is not None:
        success = bool(check.get("success"))
        key = f"{prefix}_success" if success else f"{prefix}_failure"
        return key, {
            "roll": check["roll"],
            "bonus": bonus,
            "total": check["total"],
            "dc": dc,
        }
    return f"{prefix}_roll", {
        "roll": check["roll"],
        "bonus": bonus,
        "total": check["total"],
    }


def apply_scenario_action(
    action: str,
    action_data: dict[str, Any],
    character: Character,
    *,
    difficulty: GameDifficulty = "normal",
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
        if needs_subclass_npc(character):
            return ScenarioActionResult(
                character=character, pick_subclass=True
            )
        if needs_class_feature_picks(character):
            return ScenarioActionResult(
                character=character, apply_class_features=True
            )
        if character.subclass_id is not None:
            return ScenarioActionResult(
                character=character,
                message_key="characters_menu.subclass_trainer_already",
            )
        key = str(
            action_data.get("message_key", "scenario.subclass_not_ready")
        )
        return ScenarioActionResult(character=character, message_key=key)

    if action in ("skill_check", "ability_check"):
        from core.engine.engine_rules import check_roll_flags
        from core.mechanics.checks import ability_check, skill_check

        is_skill = action == "skill_check"
        field = "skill" if is_skill else "ability"
        subject_id = str(action_data.get(field, ""))
        dc_raw = action_data.get("dc")
        dc = int(dc_raw) if isinstance(dc_raw, int) else None
        if not subject_id:
            return ScenarioActionResult(character=character)
        advantage, disadvantage = check_roll_flags(difficulty)
        check_fn = skill_check if is_skill else ability_check
        check = check_fn(
            character,
            subject_id,
            dc=dc,
            advantage=advantage,
            disadvantage=disadvantage,
        )
        key, params = _check_message(
            prefix=f"scenario.{action}",
            check=check,
            dc=dc,
        )
        params[field] = subject_id
        return ScenarioActionResult(
            character=character,
            message_key=key,
            message_params=params,
        )

    if action == "exit":
        return ScenarioActionResult(character=character)

    return ScenarioActionResult(character=character)
