"""Репозиторий для работы с навыками."""

from pathlib import Path

from src.core.yaml_utils import load_yaml_file
from src.domain.entities.abilities import AbilityEnum, Skill


class SkillRepository:
    """Репозиторий для хранения и доступа к навыкам."""

    def __init__(self, data_dir: str = "data") -> None:
        """Инициализация репозитория.

        Args:
            data_dir: Директория с данными
        """
        self._data_dir = Path(data_dir)
        self._skills: dict[str, Skill] = {}
        self._load_skills()

    def _load_skills(self) -> None:
        """Загрузить навыки из YAML файла."""
        try:
            skills_data = load_yaml_file(self._data_dir / "abilities.yaml")
            for skill_id, skill_info in skills_data.items():
                if skill_info.get("type") == "skill":
                    # Преобразуем строку в AbilityEnum
                    ability_str = skill_info.get("ability", "intelligence")
                    try:
                        ability = AbilityEnum(ability_str)
                    except ValueError:
                        ability = AbilityEnum.INTELLIGENCE

                    skill = Skill(
                        name=skill_info.get("name", skill_id),
                        description=skill_info.get("description", ""),
                        ability=ability,
                        requires_training=skill_info.get(
                            "requires_training", True
                        ),
                    )
                    self._skills[skill_id] = skill
        except FileNotFoundError:
            print(
                "⚠️ Файл навыков не найден: "
                f"{self._data_dir / 'abilities.yaml'}"
            )

    def get_all_skills(self) -> list[Skill]:
        """Получить все навыки.

        Returns:
            Список всех навыков
        """
        return list(self._skills.values())

    def get_skill(self, skill_id: str) -> Skill | None:
        """Получить навык по ID.

        Args:
            skill_id: ID навыка

        Returns:
            Навык или None если не найден
        """
        return self._skills.get(skill_id)

    def get_skills_by_ability(self, ability: AbilityEnum) -> list[Skill]:
        """Получить навыки, связанные с характеристикой.

        Args:
            ability: Характеристика

        Returns:
            Список навыков характеристики
        """
        return [
            skill
            for skill in self._skills.values()
            if skill.ability == ability
        ]

    def validate_data_consistency(self) -> list[str]:
        """Проверить согласованность данных.

        Returns:
            Список найденных проблем
        """
        issues = []
        for skill_id, skill in self._skills.items():
            if not isinstance(skill.ability, AbilityEnum):
                issues.append(
                    f"Навык '{skill_id}' имеет неверный тип характеристики"
                )
        return issues
