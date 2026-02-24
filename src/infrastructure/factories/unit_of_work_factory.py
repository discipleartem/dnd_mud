"""Factory для создания Unit of Work.

Реализует Factory Pattern для создания Unit of Work
с необходимыми репозиториями.
"""

from src.infrastructure.factories.repository_factory import RepositoryFactory
from src.infrastructure.unit_of_work import UnitOfWork
from src.interfaces.repositories import (
    ICharacterRepository,
    ILanguageRepository,
    IRaceRepository,
)


class UnitOfWorkFactory:
    """Фабрика для создания Unit of Work.

    Реализует Factory Pattern для изоляции создания
    Unit of Work с необходимыми репозиториями.
    """

    @staticmethod
    def create_unit_of_work(data_dir: str = "data") -> UnitOfWork:
        """Создать Unit of Work с репозиториями.

        Args:
            data_dir: Директория с данными

        Returns:
            Unit of Work с настроенными репозиториями
        """
        # Создаем репозитории через фабрику
        race_repository: IRaceRepository = (
            RepositoryFactory.create_race_repository(data_dir)
        )
        language_repository: ILanguageRepository = (
            RepositoryFactory.create_language_repository(data_dir)
        )
        character_repository: ICharacterRepository = (
            RepositoryFactory.create_character_repository(data_dir)
        )

        # Создаем Unit of Work
        return UnitOfWork(
            race_repository=race_repository,
            language_repository=language_repository,
            character_repository=character_repository,
        )

    @staticmethod
    def create_unit_of_work_with_custom_repositories(
        race_repository: IRaceRepository,
        language_repository: ILanguageRepository,
        character_repository: ICharacterRepository,
    ) -> UnitOfWork:
        """Создать Unit of Work с кастомными репозиториями.

        Args:
            race_repository: Репозиторий рас
            language_repository: Репозиторий языков
            character_repository: Репозиторий персонажей

        Returns:
            Unit of Work с указанными репозиториями
        """
        return UnitOfWork(
            race_repository=race_repository,
            language_repository=language_repository,
            character_repository=character_repository,
        )
