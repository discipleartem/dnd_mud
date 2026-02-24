"""Фабрика для создания доменных сущностей.

Изолирует UI слой от прямого создания доменных сущностей,
предоставляя удобный интерфейс для работы с доменом.
"""

from src.domain.entities.character import Character as DomainCharacter
from src.domain.entities.race import Race as DomainRace
from src.domain.entities.race import SubRace as DomainSubRace
from src.domain.value_objects.ability_scores import (
    AbilityScores as DomainAbilityScores,
)
from src.infrastructure.factories.repository_factory import RepositoryFactory
from src.ui.adapters.character_adapter import Character, Race, SubRace
from src.ui.adapters.updated_adapters import Race as UpdatedRace
from src.ui.adapters.updated_adapters import SubRace as UpdatedSubRace


class DomainFactory:
    """Фабрика для создания доменных сущностей."""

    @staticmethod
    def create_character(
        name: str,
        race: DomainRace | None = None,
        character_class: str = "",
        level: int = 1,
        subrace: DomainSubRace | None = None,
        sub_class: str | None = None,
        ability_scores: DomainAbilityScores | None = None,
    ) -> Character:
        """Создать UI адаптер персонажа на основе доменных данных.

        Args:
            name: Имя персонажа
            race: Раса
            character_class: Класс персонажа
            level: Уровень
            subrace: Подраса
            sub_class: Подкласс
            ability_scores: Характеристики

        Returns:
            UI адаптер персонажа
        """
        domain_character = DomainCharacter(
            name=name,
            race=race,
            character_class=character_class,
            level=level,
            subrace=subrace,
            sub_class=sub_class,
            ability_scores=ability_scores,
        )
        return Character(domain_character)

    @staticmethod
    def create_race_adapter(domain_race: DomainRace) -> Race:
        """Создать UI адаптер расы.

        Args:
            domain_race: Доменная раса

        Returns:
            UI адаптер расы
        """
        return Race(domain_race)

    @staticmethod
    def create_subrace_adapter(domain_subrace: DomainSubRace) -> SubRace:
        """Создать UI адаптер подрасы.

        Args:
            domain_subrace: Доменная подраса

        Returns:
            UI адаптер подрасы
        """
        return SubRace(domain_subrace)

    @staticmethod
    def create_updated_race_adapter(domain_race: DomainRace) -> UpdatedRace:
        """Создать обновленный UI адаптер расы.

        Args:
            domain_race: Доменная раса

        Returns:
            Обновленный UI адаптер расы
        """
        return UpdatedRace.from_domain(domain_race)

    @staticmethod
    def create_updated_subrace_adapter(
        domain_subrace: DomainSubRace,
    ) -> UpdatedSubRace:
        """Создать обновленный UI адаптер подрасы.

        Args:
            domain_subrace: Доменная подраса

        Returns:
            Обновленный UI адаптер подрасы
        """
        # Создаем DTO из доменной подрасы
        from src.ui.dto.character_dto import RaceDTO

        subrace_dto = RaceDTO.from_domain(domain_subrace)
        return UpdatedSubRace(subrace_dto)


class RaceFactory:
    """Фабрика для работы с расами."""

    def __init__(self, data_dir: str = "data") -> None:
        """Инициализировать фабрику с репозиторием.

        Args:
            data_dir: Директория с данными
        """
        self._race_repository = RepositoryFactory.create_race_repository(
            data_dir
        )

    def get_all_races(self) -> dict[str, UpdatedRace]:
        """Получить все доступные расы.

        Returns:
            Словарь рас с обновленными UI адаптерами
        """
        domain_races = self._race_repository.find_all()
        return {
            race.name: DomainFactory.create_updated_race_adapter(race)
            for race in domain_races
        }

    def get_race_by_name(self, name: str) -> UpdatedRace | None:
        """Получить расу по названию.

        Args:
            name: Название расы

        Returns:
            Обновленный UI адаптер расы или None
        """
        domain_race = self._race_repository.find_by_name(name)
        if domain_race:
            return DomainFactory.create_updated_race_adapter(domain_race)
        return None
