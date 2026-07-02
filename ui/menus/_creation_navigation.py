"""Навигация «назад» и ветвление шагов создания персонажа."""

from core.expertise import expertise_step_required
from core.feats import race_feat_step_required
from core.subclasses import subclass_offered_at_creation
from ui.menus._creation_state import CreationStep, _CreationState


def feats_step_required(state: _CreationState) -> bool:
    """Нужен ли шаг выбора черт (вариант человека и т.п.)."""
    if state.race_id is None:
        return False
    return race_feat_step_required(state.race_id, state.subrace_id)


def back_step_from_equipment(state: _CreationState) -> CreationStep:
    """Куда вернуться с шага снаряжения."""
    if state.class_id and expertise_step_required(
        state.class_id, state.start_level
    ):
        return "expertise"
    return "skills"


def back_step_from_skills(state: _CreationState) -> CreationStep:
    """Куда вернуться с шага навыков."""
    return "proficiencies"


def step_after_class_choice(state: _CreationState) -> CreationStep:
    """Следующий шаг после выбора класса/подкласса."""
    if feats_step_required(state):
        return "feats"
    return "proficiencies"


def back_step_from_feats(state: _CreationState) -> CreationStep:
    """Куда вернуться с шага черт (сразу после класса/подкласса)."""
    if state.class_id is None:
        return "class"
    if subclass_offered_at_creation(state.difficulty, state.class_id):
        return "subclass"
    return "class"


def back_step_from_proficiencies(state: _CreationState) -> CreationStep:
    """Куда вернуться с шага владений."""
    if feats_step_required(state):
        return "feats"
    if state.class_id is None:
        return "class"
    if subclass_offered_at_creation(state.difficulty, state.class_id):
        return "subclass"
    return "class"
