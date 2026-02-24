"""YAML репозиторий рас согласно Clean Architecture.

Реализует Repository Pattern для работы с YAML файлами,
изолируя бизнес-логику от инфраструктуры.
"""

from pathlib import Path
from typing import Any

from src.core.yaml_utils import load_yaml_file
from src.domain.entities.race import Race, SubRace
from src.domain.value_objects.size import Size, SizeCategory
from src.interfaces.repositories import IRaceRepository


class YamlRaceRepository(IRaceRepository):
    """YAML репозиторий рас.

    Infrastructure слой - реализует доступ к данным
    через YAML файлы следуя Clean Architecture.
    """

    def __init__(self, data_dir: str = "data") -> None:
        """Инициализировать репозиторий.

        Args:
            data_dir: Директория с YAML файлами
        """
        self._data_dir = Path(data_dir)
        self._races: dict[str, Race] = {}
        self._subraces: dict[str, SubRace] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Загрузить данные из YAML файлов."""
        try:
            # Загружаем расы
            races_data = load_yaml_file(self._data_dir / "races.yaml")
            for race_id, race_info in races_data.items():
                race = self._create_race(race_id, race_info)
                self._races[race.name] = race

            # Загружаем подрасы
            subraces_data = load_yaml_file(self._data_dir / "subraces.yaml")
            for subrace_id, subrace_info in subraces_data.items():
                subrace = self._create_subrace(subrace_id, subrace_info)
                self._subraces[subrace.name] = subrace

        except FileNotFoundError as e:
            print(f"⚠️ Файл рас не найден: {e.filename}")

    def _create_race(self, race_id: str, race_info: dict[str, Any]) -> Race:
        """Создать доменную расу из YAML данных.

        Args:
            race_id: ID расы
            race_info: Данные расы из YAML

        Returns:
            Доменная сущность Race
        """
        return Race(
            name=race_info.get("name", race_id),
            description=race_info.get("description", ""),
            ability_bonuses=race_info.get("ability_bonuses", {}),
            ability_bonuses_description=race_info.get(
                "ability_bonuses_description", ""
            ),
            size=Size.from_category(SizeCategory.MEDIUM),  # Default
            speed=race_info.get("speed", 30),
            age=race_info.get("age", {}),
            languages=race_info.get("languages", []),
            features=race_info.get("features", []),
            subraces=race_info.get("subraces", {}),
            allow_base_race_choice=race_info.get(
                "allow_base_race_choice", True
            ),
        )

    def _create_subrace(
        self, subrace_id: str, subrace_info: dict[str, Any]
    ) -> SubRace:
        """Создать доменную подрасу из YAML данных.

        Args:
            subrace_id: ID подрасы
            subrace_info: Данные подрасы из YAML

        Returns:
            Доменная сущность SubRace
        """
        return SubRace(
            name=subrace_info.get("name", subrace_id),
            description=subrace_info.get("description", ""),
            ability_bonuses=subrace_info.get("ability_bonuses", {}),
            ability_bonuses_description=subrace_info.get(
                "ability_bonuses_description", ""
            ),
            features=subrace_info.get("features", []),
        )

    def save(self, entity: Race) -> Race:
        """Сохранить расу (заглушка).

        Args:
            entity: Раса для сохранения

        Returns:
            Сохраненная раса
        """
        # В реальной реализации здесь была бы запись в YAML файл
        print(f"💾 Сохранение расы {entity.name} (заглушка)")
        return entity

    def find_by_name(self, name: str) -> Race | None:
        """Найти расу по названию.

        Args:
            name: Название расы

        Returns:
            Раса или None если не найдена
        """
        return self._races.get(name)

    def get_all_race_names(self) -> list[str]:
        """Получить список всех названий рас.

        Returns:
            Список названий рас
        """
        return list(self._races.keys())

    def get_languages_by_race(self, race_name: str) -> list[str]:
        """Получить языки доступные для расы.

        Args:
            race_name: Название расы

        Returns:
            Список кодов языков
        """
        race = self.find_by_name(race_name)
        if not race:
            return []
        return race.languages

    def get_subraces_by_race(self, race_name: str) -> list[str]:
        """Получить список подрас для расы.

        Args:
            race_name: Название расы

        Returns:
            Список названий подрас
        """
        race = self.find_by_name(race_name)
        if not race:
            return []
        return list(race.subraces.keys())

    def find_by_id(self, entity_id: str) -> Race | None:
        """Найти расу по ID.

        Args:
            entity_id: ID расы

        Returns:
            Раса или None если не найдена
        """
        # В текущей реализации ID совпадает с названием
        return self.find_by_name(entity_id)

    def find_all(self) -> list[Race]:
        """Получить все расы.

        Returns:
            Список всех рас
        """
        return list(self._races.values())

    def delete(self, entity_id: str) -> bool:
        """Удалить расу (заглушка).

        Args:
            entity_id: ID расы для удаления

        Returns:
            True если удалена
        """
        print(f"🗑️ Удаление расы с ID {entity_id} (заглушка)")
        return True

    def find_subrace_by_name(
        self, race_name: str, subrace_name: str
    ) -> SubRace | None:
        """Найти подрасу по названию.

        Args:
            race_name: Название основной расы
            subrace_name: Название подрасы

        Returns:
            Подраса или None если не найдена
        """
        # Ищем подрасу по названию среди всех подрас
        for subrace in self._subraces.values():
            if subrace.name == subrace_name:
                # Проверяем что подраса принадлежит указанной расе
                if subrace.race_name == race_name:
                    return subrace
        return None
