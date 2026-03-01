"""Интерфейсы для пользовательского интерфейса."""

from abc import ABC, abstractmethod


class UserInterface(ABC):
    """Абстрактный интерфейс пользовательского интерфейса.

    Определяет контракт для всех реализаций UI.
    Следует принципу Dependency Inversion - высокоуровневые модули
    зависят от абстракции, а не от конкретных реализаций.
    """

    @abstractmethod
    def clear(self) -> None:
        """Очистить экран."""
        pass

    @abstractmethod
    def print_info(self, text: str) -> None:
        """Напечатать информационное сообщение."""
        pass

    @abstractmethod
    def print_error(self, text: str) -> None:
        """Напечатать ошибку."""
        pass

    @abstractmethod
    def print_success(self, text: str) -> None:
        """Напечатать успешное сообщение."""
        pass

    @abstractmethod
    def get_input(self, prompt: str = "") -> str:
        """Получить ввод пользователя."""
        pass

    @abstractmethod
    def get_int_input(self, prompt: str = "", min_val: int | None = None,
                   max_val: int | None = None) -> int:
        """Получить числовой ввод с валидацией."""
        pass

    @abstractmethod
    def print_title(self, text: str) -> None:
        """Напечатать заголовок."""
        pass

    @abstractmethod
    def print_menu_item(self, number: int, text: str) -> None:
        """Напечатать пункт меню."""
        pass

    @abstractmethod
    def print_separator(self, length: int = 50, char: str = "=") -> None:
        """Напечатать разделитель."""
        pass
