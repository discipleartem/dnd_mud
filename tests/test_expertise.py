"""Тесты компетентности (экспертизы) при создании."""

from core.expertise import (
    ExpertiseGrant,
    expertise_step_required,
    get_expertise_grants,
    pending_expertise_grants,
    validate_expertise_selection,
)
from core.models import Character


def test_rogue_and_bard_expertise_grants() -> None:
    grants = get_expertise_grants("rogue", 1)
    assert len(grants) == 1 and grants[0].pick == 2
    assert not expertise_step_required("bard", 1)
    assert expertise_step_required("bard", 3)
    assert not expertise_step_required("fighter", 3)


def test_bard_expertise_pending_at_level_three() -> None:
    char = Character(
        name="Hero",
        race="elf",
        class_id="bard",
        level=3,
        subclass_id="lore_college",
        skills=["arcana", "history", "performance"],
    )
    pending = pending_expertise_grants(char)
    assert len(pending) == 1
    assert pending[0].pick == 2


def test_validate_rogue_expertise_selection() -> None:
    grant = ExpertiseGrant(
        feature_id="expertise",
        feature_name="Компетентность",
        level=1,
        pick=2,
        pool="proficient_skills",
    )
    assert validate_expertise_selection(
        grant,
        ["stealth", "perception", "athletics"],
        ["stealth", "athletics"],
        [],
    )
