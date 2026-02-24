"""Интерфейсы сервисов проекта.

Определяет абстрактные интерфейсы для всех сервисов бизнес-логики,
обеспечивая разделение ответственности и тестируемость.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional


class ILanguageService(ABC):
    """Интерфейс сервиса работы с языками.

    Предоставляет высокоуровневые операции для работы с языками,
    скрывая детали реализации репозитория.
    """

    @abstractmethod
    def get_all_languages(self) -> dict[str, "Language"]:
        """Получить все языки.

        Returns:
            Словарь языков с их кодами
        """
        pass

    @abstractmethod
    def get_language_by_code(self, code: str) -> Optional["Language"]:
        """Получить язык по коду.

        Args:
            code: Код языка

        Returns:
            Язык или None если не найден
        """
        pass

    @abstractmethod
    def get_available_languages_for_race(
        self, race_code: str
    ) -> list["Language"]:
        """Получить языки доступные для расы.

        Args:
            race_code: Код расы

        Returns:
            Список доступных языков
        """
        pass

    @abstractmethod
    def get_default_language(self) -> Optional["Language"]:
        """Получить язык по умолчанию.

        Returns:
            Язык по умолчанию или None
        """
        pass


class ILocalizationService(ABC):
    """Интерфейс сервиса локализации.

    Предоставляет унифицированный доступ к локализованным строкам.
    """

    @abstractmethod
    def translate(self, key: str, **kwargs: Any) -> str:
        """Перевести ключ с параметрами.

        Args:
            key: Ключ перевода
            **kwargs: Параметры для подстановки

        Returns:
            Локализованная строка
        """
        pass

    @abstractmethod
    def get_available_languages(self) -> list[str]:
        """Получить список доступных языков локализации.

        Returns:
            Список кодов языков
        """
        pass

    @abstractmethod
    def set_language(self, language_code: str) -> None:
        """Установить текущий язык локализации.

        Args:
            language_code: Код языка
        """
        pass


class IDisplayService(ABC):
    """Интерфейс сервиса отображения.

    Определяет контракт для форматирования и вывода данных пользователю.
    """

    @abstractmethod
    def format_race_info(self, race: "Race") -> str:
        """Отформатировать информацию о расе.

        Args:
            race: Раса для отображения

        Returns:
            Отформатированная строка
        """
        pass

    @abstractmethod
    def format_language_info(self, language: "Language") -> str:
        """Отформатировать информацию о языке.

        Args:
            language: Язык для отображения

        Returns:
            Отформатированная строка
        """
        pass

    @abstractmethod
    def format_character_info(self, character: "Character") -> str:
        """Отформатировать информацию о персонаже.

        Args:
            character: Персонаж для отображения

        Returns:
            Отформатированная строка
        """
        pass


class IValidationService(ABC):
    """Интерфейс сервиса валидации.

    Предоставляет методы для валидации бизнес-правил.
    """

    @abstractmethod
    def validate_character_creation(
        self, character_data: dict[str, Any]
    ) -> list[str]:
        """Валидировать данные создания персонажа.

        Args:
            character_data: Данные персонажа

        Returns:
            Список ошибок валидации (пустой если всё в порядке)
        """
        pass

    @abstractmethod
    def validate_race_selection(
        self, race: "Race", character: "Character"
    ) -> list[str]:
        """Валидировать выбор расы.

        Args:
            race: Выбранная раса
            character: Персонаж

        Returns:
            Список ошибок валидации
        """
        pass


# Импорты для аннотаций
if TYPE_CHECKING:
    from src.domain.entities.character import Character
    from src.domain.entities.language import Language
    from src.domain.entities.race import Race
