"""Игровой движок приключений: state machine поверх YAML-сценариев."""

from dataclasses import dataclass, field
from typing import Any, Literal

from core.models import Adventure, Character
from core.scenario_actions import (
    ScenarioActionResult,
    apply_scenario_action,
    load_scenario,
)
from core.types import GameDifficulty

UiActionKind = Literal[
    "level_up",
    "pick_subclass",
    "apply_class_features",
]


@dataclass
class UiAction:
    """UI-действие, которое engine не выполняет сам."""

    kind: UiActionKind
    message_key: str | None = None


@dataclass
class EngineResult:
    """Результат шага движка."""

    character: Character
    next_node_id: str | None = None
    message_key: str | None = None
    message_params: dict[str, Any] | None = None
    pending_ui: list[UiAction] = field(default_factory=list)
    exit_scenario: bool = False


@dataclass
class GameSession:
    """Снимок сессии приключения."""

    character: Character
    adventure_id: str
    current_node_id: str | None
    difficulty: GameDifficulty
    flags: dict[str, Any] = field(default_factory=dict)
    script_file: str = ""


@dataclass
class ScenarioGraph:
    """Загруженный сценарий."""

    nodes: dict[str, Any]
    start_node_id: str | None


class GameEngine:
    """Минимальный движок: узлы YAML, actions без боя."""

    def __init__(self, session: GameSession) -> None:
        self._session = session
        self._graph: ScenarioGraph | None = None

    @property
    def rule_mode(self) -> GameDifficulty:
        """Режим правил из сложности персонажа."""
        return self._session.difficulty

    @property
    def session(self) -> GameSession:
        return self._session

    def load_scenario(self, adventure: Adventure) -> ScenarioGraph:
        """Загрузить граф сценария из приключения."""
        scenario = load_scenario(adventure.script_file)
        nodes = scenario.get("nodes", {})
        if not isinstance(nodes, dict):
            nodes = {}
        start = scenario.get("start_node")
        start_id = str(start) if isinstance(start, str) else None
        self._graph = ScenarioGraph(nodes=nodes, start_node_id=start_id)
        if start_id and not self._session.current_node_id:
            self._session.current_node_id = start_id
        self._session.script_file = adventure.script_file
        return self._graph

    def current_node(self) -> dict[str, Any] | None:
        """Текущий узел сценария."""
        if self._graph is None or not self._session.current_node_id:
            return None
        node = self._graph.nodes.get(self._session.current_node_id)
        return node if isinstance(node, dict) else None

    def apply_action(
        self,
        action: str,
        action_data: dict[str, Any],
    ) -> EngineResult:
        """Выполнить action узла (чистая логика + UI hooks)."""
        result = apply_scenario_action(
            action,
            action_data,
            self._session.character,
        )
        return self._to_engine_result(result, action)

    def step_choice(self, choice: dict[str, Any]) -> EngineResult:
        """Обработать выбор игрока: action + переход."""
        action = choice.get("action")
        message_key: str | None = None
        message_params: dict[str, Any] | None = None
        if isinstance(action, str):
            engine_result = self.apply_action(action, choice)
            if engine_result.exit_scenario:
                return engine_result
            self._session.character = engine_result.character
            message_key = engine_result.message_key
            message_params = engine_result.message_params
            if engine_result.pending_ui:
                return engine_result
        next_id = choice.get("next")
        if next_id:
            self._session.current_node_id = str(next_id)
        return EngineResult(
            character=self._session.character,
            next_node_id=self._session.current_node_id,
            message_key=message_key,
            message_params=message_params,
        )

    def step_auto_node(self, node: dict[str, Any]) -> EngineResult:
        """Узел с единственным action и next."""
        message_key: str | None = None
        message_params: dict[str, Any] | None = None
        action = node.get("action")
        if isinstance(action, str):
            engine_result = self.apply_action(action, node)
            self._session.character = engine_result.character
            message_key = engine_result.message_key
            message_params = engine_result.message_params
            if engine_result.pending_ui or engine_result.exit_scenario:
                return engine_result
        next_id = node.get("next")
        if next_id:
            self._session.current_node_id = str(next_id)
        else:
            self._session.current_node_id = None
        return EngineResult(
            character=self._session.character,
            next_node_id=self._session.current_node_id,
            message_key=message_key,
            message_params=message_params,
        )

    def _to_engine_result(
        self,
        result: ScenarioActionResult,
        action: str,
    ) -> EngineResult:
        pending: list[UiAction] = []
        if result.level_up_pending:
            pending.append(UiAction(kind="level_up"))
        if result.pick_subclass:
            pending.append(
                UiAction(
                    kind="pick_subclass",
                    message_key=result.message_key,
                )
            )
        if result.apply_class_features:
            pending.append(UiAction(kind="apply_class_features"))
        return EngineResult(
            character=result.character,
            message_key=result.message_key,
            message_params=result.message_params,
            pending_ui=pending,
            exit_scenario=action == "exit",
        )
