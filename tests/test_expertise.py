"""Тесты компетентности (экспертизы) при создании."""

from core.expertise import (
    ExpertiseGrant,
    expertise_step_required,
    get_expertise_grants,
    validate_expertise_selection,
)


def test_rogue_has_expertise_grant_at_level_one():
    """Плут получает компетентность на 1 уровне."""
    grants = get_expertise_grants("rogue", 1)
    assert len(grants) == 1
    assert grants[0].pick == 2
    assert grants[0].alternatives


def test_bard_no_expertise_at_level_one():
    """Бард: компетентность только с 3 уровня."""
    assert not expertise_step_required("bard", 1)
    assert expertise_step_required("bard", 3)


def test_fighter_no_expertise_step():
    """Воин не имеет шага компетентности."""
    assert not expertise_step_required("fighter", 3)


def test_validate_rogue_two_skills_mode():
    """Плут: два навыка из владений."""
    grant = ExpertiseGrant(
        feature_id="expertise",
        feature_name="Компетентность",
        level=1,
        pick=2,
        pool="proficient_skills",
    )
    proficiencies = ["stealth", "perception", "athletics"]
    selected = ["stealth", "athletics"]
    assert validate_expertise_selection(grant, proficiencies, selected, [])


def test_validate_rogue_skill_and_tools_mode():
    """Плут: один навык и воровские инструменты."""
    from core.expertise import ExpertiseAlternative

    grant = ExpertiseGrant(
        feature_id="expertise",
        feature_name="Компетентность",
        level=1,
        pick=2,
        pool="proficient_skills",
        alternatives=[
            ExpertiseAlternative(pick=1, pool="proficient_skills"),
            ExpertiseAlternative(
                pick=1, pool="tools", options=["thieves_tools"]
            ),
        ],
    )
    assert validate_expertise_selection(
        grant,
        ["stealth", "perception"],
        ["stealth"],
        ["thieves_tools"],
        used_alternative=True,
    )
