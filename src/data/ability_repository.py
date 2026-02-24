"""Репозиторий для работы с характеристиками."""

from pathlib import Path

from src.core.yaml_utils import load_yaml_file
from src.domain.entities.abilities import Ability


class AbilityRepository:
    """Репозиторий для хранения и доступа к характеристикам."""

    def __init__(self, data_dir: str = "data") -> None:
        """Инициализация репозитория.

        Args:
            data_dir: Директория с данными
        """
        self._data_dir = Path(data_dir)
        self._abilities: dict[str, Ability] = {}
        self._load_abilities()

    def _load_abilities(self) -> None:
        """Загрузить характеристики из YAML файла."""
        try:
            abilities_data = load_yaml_file(self._data_dir / "abilities.yaml")
            for ability_id, ability_info in abilities_data.items():
                ability = Ability(
                    name=ability_info.get("name", ability_id),
                    description=ability_info.get("description", ""),
                    abbreviation=ability_info.get("abbreviation", ""),
                )
                self._abilities[ability_id] = ability
        except FileNotFoundError:
            print(
                "⚠️ Файл характеристик не найден: "
                f"{self._data_dir / 'abilities.yaml'}"
            )

    def get_all_abilities(self) -> list[Ability]:
        """Получить все характеристики.

        Returns:
            Список всех характеристик
        """
        return list(self._abilities.values())

    def get_ability(self, ability_id: str) -> Ability | None:
        """Получить характеристику по ID.

        Args:
            ability_id: ID характеристики

        Returns:
            Характеристика или None если не найдена
        """
        return self._abilities.get(ability_id)
