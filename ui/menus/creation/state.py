"""Состояние и типы flow создания персонажа."""

from dataclasses import dataclass, field
from typing import Any

from core.character.build import build_new_character
from core.character.creation_draft import CreationDraft, CreationStep
from core.character.models import Character
from core.character.storage import unique_save_slug
from core.progression.class_progression import (
    class_features_applied_at_creation,
    start_level_for_difficulty,
)
from core.types import CharacterBuildParams, GameDifficulty, StatMap

__all__ = [
    "CreationStep",
    "_CreationState",
    "draft_from_state",
    "state_from_draft",
]


@dataclass
class _CreationState:
    """Состояние пошагового создания персонажа."""

    name: str
    difficulty: GameDifficulty
    race_id: str | None = None
    subrace_id: str | None = None
    languages: list[str] | None = None
    stats: StatMap | None = None
    background_id: str | None = None
    background_skills: list[str] = field(default_factory=list)
    class_id: str | None = None
    subclass_id: str | None = None
    skills: list[str] | None = None
    skill_expertise: list[str] | None = None
    tool_expertise: list[str] | None = None
    weapon_proficiencies: list[str] | None = None
    armor_proficiencies: list[str] | None = None
    tool_proficiencies: list[str] | None = None
    background_tool_picks: list[str] = field(default_factory=list)
    equipment_choices: dict[str, str] = field(default_factory=dict)
    feat_ids: list[str] = field(default_factory=list)
    feat_choices: dict[str, dict[str, Any]] = field(default_factory=dict)
    hardcore_rolls: list[int] = field(default_factory=list)

    @property
    def start_level(self) -> int:
        """Стартовый уровень по сложности (вычисляется один раз на чтение)."""
        return start_level_for_difficulty(self.difficulty)

    def to_character(self) -> Character | None:
        """Собрать модель персонажа из состояния создания."""
        if self.race_id is None or self.stats is None or self.class_id is None:
            return None
        start_level = self.start_level
        features_applied = class_features_applied_at_creation(
            self.class_id, self.subclass_id, start_level
        )
        return build_new_character(
            CharacterBuildParams(
                name=self.name,
                race_id=str(self.race_id),
                class_id=str(self.class_id),
                difficulty=self.difficulty,
                subrace_id=str(self.subrace_id) if self.subrace_id else None,
                stats=self.stats,
                subclass_id=self.subclass_id,
                languages=self.languages,
                background_id=self.background_id,
                skills=self.skills,
                skill_expertise=self.skill_expertise,
                tool_expertise=self.tool_expertise,
                weapon_proficiencies=self.weapon_proficiencies,
                armor_proficiencies=self.armor_proficiencies,
                tool_proficiencies=self.tool_proficiencies,
                background_tool_picks=self.background_tool_picks or None,
                equipment_choices=self.equipment_choices or None,
                feat_ids=self.feat_ids or None,
                feat_choices=self.feat_choices or None,
                class_features_applied=features_applied,
                apply_feat_stat_bonuses=False,
                unique_save_slug=unique_save_slug,
            )
        )


def draft_from_state(
    state: _CreationState, current_step: CreationStep
) -> CreationDraft:
    """Собрать черновик из UI-состояния и текущего шага."""
    return CreationDraft(
        current_step=current_step,
        name=state.name,
        difficulty=state.difficulty,
        race_id=state.race_id,
        subrace_id=state.subrace_id,
        languages=state.languages,
        stats=state.stats,
        background_id=state.background_id,
        background_skills=list(state.background_skills),
        class_id=state.class_id,
        subclass_id=state.subclass_id,
        skills=state.skills,
        skill_expertise=state.skill_expertise,
        tool_expertise=state.tool_expertise,
        weapon_proficiencies=state.weapon_proficiencies,
        armor_proficiencies=state.armor_proficiencies,
        tool_proficiencies=state.tool_proficiencies,
        background_tool_picks=list(state.background_tool_picks),
        equipment_choices=dict(state.equipment_choices),
        feat_ids=list(state.feat_ids),
        feat_choices={
            key: dict(value) for key, value in state.feat_choices.items()
        },
        hardcore_rolls=list(state.hardcore_rolls),
    )


def state_from_draft(draft: CreationDraft) -> _CreationState:
    """Восстановить UI-состояние из черновика."""
    return _CreationState(
        name=draft.name,
        difficulty=draft.difficulty,
        race_id=draft.race_id,
        subrace_id=draft.subrace_id,
        languages=draft.languages,
        stats=draft.stats,
        background_id=draft.background_id,
        background_skills=list(draft.background_skills),
        class_id=draft.class_id,
        subclass_id=draft.subclass_id,
        skills=draft.skills,
        skill_expertise=draft.skill_expertise,
        tool_expertise=draft.tool_expertise,
        weapon_proficiencies=draft.weapon_proficiencies,
        armor_proficiencies=draft.armor_proficiencies,
        tool_proficiencies=draft.tool_proficiencies,
        background_tool_picks=list(draft.background_tool_picks),
        equipment_choices=dict(draft.equipment_choices),
        feat_ids=list(draft.feat_ids),
        feat_choices={
            key: dict(value) for key, value in draft.feat_choices.items()
        },
        hardcore_rolls=list(draft.hardcore_rolls),
    )
