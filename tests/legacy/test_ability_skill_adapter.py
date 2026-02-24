"""Тесты для адаптера характеристик и навыков."""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.ability_repository import AbilityRepository
from src.data.ability_skill_adapter import AbilitySkillAdapter
from src.data.skill_repository import SkillRepository


def test_adapter():
    """Тестирование адаптера."""
    print("🧪 Тестирование AbilitySkillAdapter")

    adapter = AbilitySkillAdapter("data")

    # Проверка загрузки характеристик
    abilities = adapter.get_all_abilities()
    print(f"✓ Загружено характеристик: {len(abilities)}")

    # Проверка загрузки навыков
    skills = adapter.get_all_skills()
    print(f"✓ Загружено навыков: {len(skills)}")

    # Проверка связей навыков с характеристиками
    test_skill = "athletics"
    ability = adapter.get_ability_for_skill(test_skill)
    if ability:
        print(
            f"✓ Навык '{test_skill}' привязан к характеристике "
            f"'{ability.name}' ({ability.id})"
        )
    else:
        print(f"❌ Не найдена характеристика для навыка '{test_skill}'")

    # Проверка согласованности данных
    issues = adapter.validate_skill_ability_consistency()
    if issues:
        print("⚠️ Найдены несоответствия:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✓ Данные согласованы")

    # Вывод сводки
    print("\n" + adapter.get_abilities_summary())


def test_repositories():
    """Тестирование репозиториев."""
    print("\n🧪 Тестирование репозиториев")

    # Тест репозитория характеристик
    ability_repo = AbilityRepository("data")
    abilities = ability_repo.get_all_abilities()
    print(f"✓ AbilityRepository: {len(abilities)} характеристик")

    # Тест репозитория навыков
    skill_repo = SkillRepository("data")
    skills = skill_repo.get_all_skills()
    print(f"✓ SkillRepository: {len(skills)} навыков")

    # Проверка получения навыков по характеристике
    strength_skills = skill_repo.get_skills_by_ability("strength")
    print(f"✓ Навыков Силы: {len(strength_skills)}")
    for skill in strength_skills:
        print(f"  • {skill.name}")

    # Проверка согласованности через репозиторий
    issues = skill_repo.validate_data_consistency()
    if issues:
        print("⚠️ Найдены несоответствия в репозитории:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print("✓ Данные в репозитории согласованы")


if __name__ == "__main__":
    test_adapter()
    test_repositories()
    print("\n🎉 Все тесты завершены!")
