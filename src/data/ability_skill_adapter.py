"""Адаптер для работы с характеристиками и навыками."""

from src.data.ability_repository import AbilityRepository
from src.data.skill_repository import SkillRepository
from src.domain.entities.abilities import Ability, AbilityEnum, Skill


class AbilitySkillAdapter:
    """Адаптер для связывания характеристик и навыков."""

    def __init__(self, data_dir: str = "data") -> None:
        """Инициализация адаптера.

        Args:
            data_dir: Директория с данными
        """
        self._ability_repo = AbilityRepository(data_dir)
        self._skill_repo = SkillRepository(data_dir)

    def get_all_abilities(self) -> list[Ability]:
        """Получить все характеристики.

        Returns:
            Список всех характеристик
        """
        return self._ability_repo.get_all_abilities()

    def get_all_skills(self) -> list[Skill]:
        """Получить все навыки.

        Returns:
            Список всех навыков
        """
        return self._skill_repo.get_all_skills()

    def get_ability_for_skill(self, skill_id: str) -> Ability | None:
        """Получить характеристику для навыка.

        Args:
            skill_id: ID навыка

        Returns:
            Характеристика или None если не найдена
        """
        skill = self._skill_repo.get_skill(skill_id)
        if skill and isinstance(skill.ability, AbilityEnum):
            # Ищем характеристику по enum значению
            for ability in self._ability_repo.get_all_abilities():
                if ability.name.lower() == skill.ability.value:
                    return ability
        return None

    def validate_skill_ability_consistency(self) -> list[str]:
        """Проверить согласованность связей навыков и характеристик.

        Returns:
            Список найденных проблем
        """
        issues = []

        # Проверяем, что у всех навыков есть существующие характеристики
        for skill in self._skill_repo.get_all_skills():
            if not isinstance(skill.ability, AbilityEnum):
                issues.append(
                    f"Навык '{skill.name}' имеет неверный тип характеристики"
                )
            else:
                # Проверяем, что характеристика существует в репозитории
                ability_found = False
                for ability in self._ability_repo.get_all_abilities():
                    if ability.name.lower() == skill.ability.value:
                        ability_found = True
                        break

                if not ability_found:
                    issues.append(
                        f"Навык '{skill.name}' ссылается на несуществующую "
                        f"характеристику '{skill.ability.value}'"
                    )

        return issues

    def get_abilities_summary(self) -> str:
        """Получить сводку по характеристикам.

        Returns:
            Текстовая сводка
        """
        abilities = self.get_all_abilities()
        skills = self.get_all_skills()

        summary = f"Характеристики: {len(abilities)}\n"
        summary += f"Навыки: {len(skills)}\n\n"

        # Группируем навыки по характеристикам
        for ability_enum in AbilityEnum:
            ability_name = ability_enum.value.title()
            ability_skills = [
                skill for skill in skills if skill.ability == ability_enum
            ]
            summary += f"{ability_name}: {len(ability_skills)} навыков\n"

        return summary
