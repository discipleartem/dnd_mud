"""Factory для создания репозиториев.

Реализует Factory Pattern для изоляции создания
инфраструктурных компонентов от бизнес-логики.
"""

from typing import Any, TypeVar

from src.infrastructure.repositories.yaml_character_repository import (
    YamlCharacterRepository,
)
from src.infrastructure.repositories.yaml_language_repository import (
    YamlLanguageRepository,
)
from src.infrastructure.repositories.yaml_race_repository import (
    YamlRaceRepository,
)
from src.interfaces.repositories import (
    ICharacterRepository,
    ILanguageRepository,
    IRaceRepository,
)

T = TypeVar("T", bound=Any)


class RepositoryFactory:
    """Фабрика для создания репозиториев.

    Реализует Factory Pattern для изоляции создания
    инфраструктурных компонентов от бизнес-логики.
    """

    @staticmethod
    def create_race_repository(data_dir: str = "data") -> IRaceRepository:
        """Создать репозиторий рас.

        Args:
            data_dir: Директория с данными

        Returns:
            YAML репозиторий рас
        """
        return YamlRaceRepository(data_dir)

    @staticmethod
    def create_language_repository(
        data_dir: str = "data",
    ) -> ILanguageRepository:
        """Создать репозиторий языков.

        Args:
            data_dir: Директория с данными

        Returns:
            YAML репозиторий языков
        """
        return YamlLanguageRepository(data_dir)

    @staticmethod
    def create_character_repository(
        data_dir: str = "data", characters_file: str = "characters.yaml"
    ) -> ICharacterRepository:
        """Создать репозиторий персонажей.

        Args:
            data_dir: Директория с данными
            characters_file: Имя файла с персонажами

        Returns:
            YAML репозиторий персонажей
        """
        return YamlCharacterRepository(data_dir, characters_file)

    @staticmethod
    def create_repository(
        repository_type: type[T], data_dir: str = "data", **kwargs: Any
    ) -> T:
        """Создать репозиторий по типу.

        Args:
            repository_type: Тип репозитория
            data_dir: Директория с данными
            **kwargs: Дополнительные параметры

        Returns:
            Созданный репозиторий
        """
        repositories: dict[type[Any], Any] = {
            IRaceRepository: RepositoryFactory.create_race_repository,
            ILanguageRepository: RepositoryFactory.create_language_repository,
            ICharacterRepository: (
                RepositoryFactory.create_character_repository
            ),
        }

        repository_class = repositories.get(repository_type)
        if not repository_class:
            raise ValueError(f"Неизвестный тип репозитория: {repository_type}")

        return repository_class(data_dir, **kwargs)  # type: ignore
