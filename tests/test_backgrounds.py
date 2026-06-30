"""Тесты загрузки предысторий."""

from core.backgrounds import (
    get_background_skills,
    load_backgrounds,
)
from core.skills import PHB_SKILL_IDS


def test_background_skills_valid() -> None:
    """Навыки предысторий — валидные PHB skill id."""
    for bg in load_backgrounds("ru"):
        bg_id = str(bg["id"])
        for skill_id in get_background_skills(bg_id):
            assert skill_id in PHB_SKILL_IDS


def test_acolyte_russian_name() -> None:
    """Прислужник — каноничное имя PHB."""
    names = {bg["id"]: bg["name"] for bg in load_backgrounds("ru")}
    assert names["acolyte"] == "Прислужник"
