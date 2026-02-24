"""Тесты для адаптера характеристик и навыков."""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.data.ability_repository import AbilityRepository
from src.data.ability_skill_adapter import AbilitySkillAdapter
from src.data.skill_repository import SkillRepository
from src.ui.entities.race import RaceLoader


def test_adapter() -> None:
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


def test_repositories() -> None:
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


def demonstrate_race_usage() -> None:
    """Демонстрация использования рас в игре."""
    print("🎮 D&D MUD - Демонстрация работы с расами\n")

    # Загружаем все доступные расы
    loader = RaceLoader()
    races = loader.load_races()

    # Показываем меню выбора расы
    print("📋 Доступные расы:")
    race_list = list(races.keys())
    for i, race_id in enumerate(race_list, 1):
        race = races[race_id]
        print(f"{i}. {race.name} - {race.description[:50]}...")

    # Симуляция выбора расы (для примера выберем эльфа)
    selected_race_id = "elf"
    selected_race = races[selected_race_id]

    print(f"\n🎯 Выбрана раса: {selected_race.name}")
    print(f"📝 Описание: {selected_race.description}")
    print(
        f"💪 Бонусы характеристик: {selected_race.ability_bonuses_description}"
    )
    print(f"📏 Размер: {selected_race.size}")
    print(f"🏃 Скорость: {selected_race.speed} футов")
    print(f"🗣️ Языки: {', '.join(selected_race.languages)}")

    # Показываем черты расы
    print("\n✨ Черты расы:")
    for feature in selected_race.features:
        print(f"  • {feature.name}: {feature.description}")

    # Показываем доступные подрасы
    if selected_race.subraces:
        print("\n🔸 Доступные подрасы:")
        for _subrace_id, subrace in selected_race.subraces.items():
            print(
                f"  • {subrace.name}: "
                f"{subrace.ability_bonuses_description}"
            )

        # Симуляция выбора подрасы
        selected_subrace_id = "high_elf"
        selected_subrace = selected_race.get_subrace(selected_subrace_id)

        if selected_subrace:
            print(f"\n🎯 Выбрана подраса: {selected_subrace.name}")

            # Показываем общие бонусы
            total_bonuses = selected_race.get_total_ability_bonuses(
                selected_subrace_id
            )
            print("💪 Общие бонусы характеристик:")
            for ability, bonus in total_bonuses.items():
                print(f"  • {ability}: +{bonus}")

            # Показываем дополнительные черты подрасы
            if selected_subrace.features:
                print("\n✨ Дополнительные черты подрасы:")
                for feature in selected_subrace.features:
                    print(f"  • {feature.name}: {feature.description}")

    print(f"\n🎮 Раса {selected_race.name} готова к использованию в игре!")


if __name__ == "__main__":
    test_adapter()
    test_repositories()
    demonstrate_race_usage()
    print("\n🎉 Все тесты завершены!")
