"""Интерфейсы для пользовательского интерфейса."""

from abc import ABC, abstractmethod
from typing import Final


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
        """Напечатать информационное сообщение.
        
        Args:
            text: Текст для вывода
        """
        pass

    @abstractmethod
    def print_error(self, text: str) -> None:
        """Напечатать ошибку.
        
        Args:
            text: Текст ошибки
        """
        pass

    @abstractmethod
    def print_success(self, text: str) -> None:
        """Напечатать успешное сообщение.
        
        Args:
            text: Текст успешного сообщения
        """
        pass

    @abstractmethod
    def get_input(self, prompt: str = "") -> str:
        """Получить ввод пользователя.
        
        Args:
            prompt: Приглашение для ввода
            
        Returns:
            Строка введенная пользователем
        """
        pass

    @abstractmethod
    def get_int_input(self, prompt: str = "", min_val: int | None = None,
                   max_val: int | None = None) -> int:
        """Получить числовой ввод с валидацией.
        
        Args:
            prompt: Приглашение для ввода
            min_val: Минимальное допустимое значение
            max_val: Максимальное допустимое значение
            
        Returns:
            Целое число введенное пользователем
            
        Raises:
            ValueError: При некорректном вводе
        """
        pass

    # Дополнительные методы для улучшения интерфейса
    @abstractmethod
    def print_title(self, text: str) -> None:
        """Напечатать заголовок.
        
        Args:
            text: Текст заголовка
        """
        pass

    @abstractmethod
    def print_menu_item(self, number: int, text: str) -> None:
        """Напечатать пункт меню.
        
        Args:
            number: Номер пункта меню
            text: Текст пункта меню
        """
        pass

    @abstractmethod
    def print_separator(self, length: int = 50, char: str = "=") -> None:
        """Напечатать разделитель.
        
        Args:
            length: Длина разделителя
            char: Символ разделителя
        """
        pass
