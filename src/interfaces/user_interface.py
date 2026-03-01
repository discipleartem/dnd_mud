"""Интерфейсы для пользовательского интерфейса."""

from abc import ABC, abstractmethod

from interfaces.i18n_api import I18nTranslator


class UserInterface(ABC):
    """Абстрактный интерфейс пользовательского интерфейса.

    Определяет контракт для всех реализаций UI.
    Следует принципу Dependency Inversion - высокоуровневые модули
    зависят от абстракции, а не от конкретных реализаций.
    """

    def __init__(self, translator: I18nTranslator | None = None) -> None:
        """Инициализировать интерфейс с переводчиком.

        Args:
            translator: Переводчик для локализации
        """
        self._translator = translator

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
    def get_int_input(
        self,
        prompt: str = "",
        min_val: int | None = None,
        max_val: int | None = None,
    ) -> int:
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
    def print_separator(
        self, length: int = 50, char: str = "="
    ) -> None:
        """Напечатать разделитель."""
        pass

    @abstractmethod
    def show_message_and_wait(self, message: str) -> None:
        """Показать сообщение и ждать ввода."""
        pass

    def t(self, key: str, context: str | None = None, **kwargs) -> str:
        """Перевести строку.

        Args:
            key: Ключ перевода
            context: Контекст перевода
            **kwargs: Параметры для форматирования

        Returns:
            Переведенная строка или ключ если переводчик не доступен
        """
        if self._translator:
            return self._translator.translate(key, context, **kwargs)
        return key

    def set_translator(self, translator: I18nTranslator) -> None:
        """Установить переводчик.

        Args:
            translator: Переводчик
        """
        self._translator = translator
