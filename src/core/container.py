"""Простой контейнер зависимостей.

Реализует базовый Dependency Injection контейнер следуя
принципу Dependency Inversion из SOLID.
"""

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class DIContainer:
    """Простой контейнер зависимостей.

    Управляет созданием и жизненным циклом объектов.
    Поддерживает синглтоны и фабрики.
    """

    def __init__(self) -> None:
        """Инициализация контейнера."""
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {}
        self._singletons: dict[str, Any] = {}

    def register_singleton(
        self, interface: type[T], implementation: type[T]
    ) -> None:
        """Зарегистрировать синглтон.

        Args:
            interface: Интерфейс или базовый класс
            implementation: Реализация
        """
        key = self._get_key(interface)
        self._services[key] = implementation

    def register_factory(
        self, interface: type[T], factory: Callable[[], T]
    ) -> None:
        """Зарегистрировать фабрику.

        Args:
            interface: Интерфейс или базовый класс
            factory: Фабричная функция
        """
        key = self._get_key(interface)
        self._factories[key] = factory

    def register_instance(self, interface: type[T], instance: T) -> None:
        """Зарегистрировать экземпляр.

        Args:
            interface: Интерфейс или базовый класс
            instance: Экземпляр
        """
        key = self._get_key(interface)
        self._singletons[key] = instance

    def get(self, interface: type[T]) -> T:
        """Получить зависимость.

        Args:
            interface: Интерфейс или базовый класс

        Returns:
            Экземпляр зависимости

        Raises:
            ValueError: Если зависимость не зарегистрирована
        """
        key = self._get_key(interface)

        # Проверяем синглтоны
        if key in self._singletons:
            return self._singletons[key]  # type: ignore

        # Проверяем фабрики
        if key in self._factories:
            instance = self._factories[key]()
            self._singletons[key] = instance
            return instance  # type: ignore

        # Проверяем сервисы
        if key in self._services:
            implementation = self._services[key]
            instance = implementation()
            self._singletons[key] = instance
            return instance  # type: ignore

        raise ValueError(f"Зависимость не зарегистрирована: {interface}")

    def get_optional(self, interface: type[T]) -> T | None:
        """Получить опциональную зависимость.

        Args:
            interface: Интерфейс или базовый класс

        Returns:
            Экземпляр зависимости или None
        """
        try:
            return self.get(interface)
        except ValueError:
            return None

    def has(self, interface: type[T]) -> bool:
        """Проверить наличие зависимости.

        Args:
            interface: Интерфейс или базовый класс

        Returns:
            True если зависимость зарегистрирована
        """
        key = self._get_key(interface)
        return (
            key in self._services
            or key in self._factories
            or key in self._singletons
        )

    def clear(self) -> None:
        """Очистить контейнер."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()

    def _get_key(self, interface: type[T]) -> str:
        """Получить ключ для интерфейса.

        Args:
            interface: Интерфейс или класс

        Returns:
            Ключ в виде строки
        """
        return f"{interface.__module__}.{interface.__name__}"


# Глобальный контейнер для простого использования
_global_container: DIContainer | None = None


def get_container() -> DIContainer:
    """Получить глобальный контейнер.

    Returns:
        Экземпляр DI контейнера
    """
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container


def configure_container(container: DIContainer) -> None:
    """Настроить контейнер зависимостями проекта.

    Args:
        container: Контейнер для настройки
    """
    from pathlib import Path

    # Регистрация загрузчиков
    from src.infrastructure.loaders.yaml_loader import YamlLoader

    container.register_singleton(YamlLoader, YamlLoader)

    # Регистрация путей к данным
    base_path = Path(__file__).parent.parent.parent
    races_file = base_path / "data" / "races.yaml"
    languages_file = base_path / "data" / "languages.yaml"

    container.register_instance(Path, races_file)
    container.register_instance(Path, languages_file)

    # TODO: Добавить регистрацию других сервисов при их создании
    # from infrastructure.repositories.race_repository import (
    #     YamlRaceRepository
    # )
    # from interfaces.repositories import IRaceRepository
    # container.register_factory(
    #     IRaceRepository,
    #     lambda: YamlRaceRepository(races_file)
    # )
