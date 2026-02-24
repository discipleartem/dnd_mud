"""Контейнер зависимостей для D&D MUD.

Реализует Dependency Injection паттерн для управления
зависимостями между компонентами системы.
Следует принципам Clean Architecture.
"""

from collections.abc import Callable
from typing import Any, TypeVar

from src.infrastructure.factories.repository_factory import RepositoryFactory
from src.interfaces.repositories import (
    ICharacterRepository,
    ILanguageRepository,
    IRaceRepository,
)
from src.ui.controllers.character_controller import (
    CharacterController,
    RaceController,
)

T = TypeVar("T")


class DIContainer:
    """Контейнер для внедрения зависимостей."""

    def __init__(self):
        """Инициализировать контейнер."""
        self._services: dict[type, Any] = {}
        self._singletons: dict[type, Any] = {}
        self._factory: RepositoryFactory = None

    def register_singleton(
        self, interface: type[T], implementation: T
    ) -> None:
        """Зарегистрировать singleton.

        Args:
            interface: Интерфейс
            implementation: Реализация
        """
        self._singletons[interface] = implementation

    def register_factory(
        self, interface: type[T], factory: Callable[[], T]
    ) -> None:
        """Зарегистрировать фабрику.

        Args:
            interface: Интерфейс
            factory: Фабричная функция
        """
        self._services[interface] = factory

    def register_transient(
        self, interface: type[T], implementation: type[T]
    ) -> None:
        """Зарегистрировать transient сервис.

        Args:
            interface: Интерфейс
            implementation: Класс реализации
        """
        self._services[interface] = implementation

    def get(self, interface: type[T]) -> T:
        """Получить сервис из контейнера.

        Args:
            interface: Интерфейс сервиса

        Returns:
            Экземпляр сервиса

        Raises:
            ValueError: Если сервис не зарегистрирован
        """
        # Проверяем singleton
        if interface in self._singletons:
            return self._singletons[interface]

        # Проверяем зарегистрированные сервисы
        if interface in self._services:
            service = self._services[interface]

            # Если это фабричная функция
            if callable(service) and not isinstance(service, type):
                return service()

            # Если это класс
            if isinstance(service, type):
                return service()

            return service

        raise ValueError(f"Сервис {interface} не зарегистрирован в контейнере")

    def get_repository_factory(self) -> RepositoryFactory:
        """Получить фабрику репозиториев.

        Returns:
            Фабрика репозиториев
        """
        if self._factory is None:
            self._factory = RepositoryFactory()
        return self._factory

    def register_repositories(self) -> None:
        """Зарегистрировать все репозитории."""
        factory = self.get_repository_factory()

        self.register_singleton(
            ICharacterRepository, factory.create_character_repository()
        )
        self.register_singleton(
            IRaceRepository, factory.create_race_repository()
        )
        self.register_singleton(
            ILanguageRepository, factory.create_language_repository()
        )

    def register_controllers(self) -> None:
        """Зарегистрировать все контроллеры."""
        character_repo = self.get(ICharacterRepository)
        race_repo = self.get(IRaceRepository)

        self.register_singleton(
            CharacterController, CharacterController(character_repo, race_repo)
        )

        self.register_singleton(RaceController, RaceController(race_repo))

    def initialize(self) -> None:
        """Инициализировать контейнер зависимостей."""
        self.register_repositories()
        self.register_controllers()


class ServiceLocator:
    """Локатор сервисов для глобального доступа к зависимостям."""

    _instance: "ServiceLocator" = None
    _container: DIContainer = None

    def __new__(cls) -> "ServiceLocator":
        """Создать singleton экземпляр."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._container = DIContainer()
        return cls._instance

    @property
    def container(self) -> DIContainer:
        """Получить контейнер зависимостей.

        Returns:
            Контейнер зависимостей
        """
        return self._container

    def initialize(self) -> None:
        """Инициализировать сервис локатор."""
        self._container.initialize()

    def get(self, interface: type[T]) -> T:
        """Получить сервис.

        Args:
            interface: Интерфейс сервиса

        Returns:
            Экземпляр сервиса
        """
        return self._container.get(interface)

    def get_character_controller(self) -> CharacterController:
        """Получить контроллер персонажей.

        Returns:
            Контроллер персонажей
        """
        return self.get(CharacterController)

    def get_race_controller(self) -> RaceController:
        """Получить контроллер рас.

        Returns:
            Контроллер рас
        """
        return self.get(RaceController)

    def get_character_repository(self) -> ICharacterRepository:
        """Получить репозиторий персонажей.

        Returns:
            Репозиторий персонажей
        """
        return self.get(ICharacterRepository)

    def get_race_repository(self) -> IRaceRepository:
        """Получить репозиторий рас.

        Returns:
            Репозиторий рас
        """
        return self.get(IRaceRepository)

    def get_language_repository(self) -> ILanguageRepository:
        """Получить репозиторий языков.

        Returns:
            Репозиторий языков
        """
        return self.get(ILanguageRepository)


# Глобальный экземпляр сервис локатора
service_locator = ServiceLocator()


def get_service_locator() -> ServiceLocator:
    """Получить глобальный сервис локатор.

    Returns:
        Сервис локатор
    """
    return service_locator


def initialize_dependencies() -> None:
    """Инициализировать все зависимости приложения."""
    locator = get_service_locator()
    locator.initialize()
