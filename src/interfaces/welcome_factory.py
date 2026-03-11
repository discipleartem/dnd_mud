"""Интерфейс фабрики приветственных экранов.

Следует Clean Architecture - Use Case зависит от абстракции, а не от реализации.
"""

from abc import ABC, abstractmethod
from typing import Final

from src.dto.welcome_dto import WelcomeControllerRequest
from src.entities.welcome_screen import WelcomeScreen


class WelcomeScreenFactory(ABC):
    """Абстракция для создания приветственных экранов.

    Следует принципу инверсии зависимостей - Use Case работает с интерфейсом,
    а конкретная реализация может быть любой (файлы, база данных, API).
    """

    @abstractmethod
    def create_screen(
        self, request: WelcomeControllerRequest
    ) -> WelcomeScreen:
        """Создать приветственный экран на основе запроса.

        Args:
            request: Параметры создания экрана

        Returns:
            Созданный приветственный экран
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """Получить список поддерживаемых языков.

        Returns:
            Список кодов поддерживаемых языков
        """
        pass


# Константы для значений по умолчанию
DEFAULT_REQUEST: Final[WelcomeControllerRequest] = WelcomeControllerRequest(
    language="ru",
    show_ascii_art=True,
)
