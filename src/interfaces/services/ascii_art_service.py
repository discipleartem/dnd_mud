"""Интерфейс сервиса ASCII art.

Следует Clean Architecture - Use Case зависит от абстракции.
Определяет контракт для работы с ASCII искусством.
"""

from abc import ABC, abstractmethod


class AsciiArtService(ABC):
    """Интерфейс сервиса ASCII art.

    Следует Clean Architecture - Use Case работает с интерфейсом,
    а конкретная реализация может быть любой (файлы, генератор).
    """

    @abstractmethod
    def get_dnd_logo(self) -> str:
        """Получить ASCII логотип D&D.

        Returns:
            ASCII логотип

        Raises:
            AsciiArtError: Ошибка получения логотипа
        """
        pass

    @abstractmethod
    def get_dice_art(self, dice_type: int) -> str:
        """Получить ASCII изображение кубика.

        Args:
            dice_type: Тип кубика (4, 6, 8, 10, 12, 20)

        Returns:
            ASCII изображение кубика

        Raises:
            AsciiArtError: Ошибка получения изображения
        """
        pass

    @abstractmethod
    def get_character_frame(self, character_name: str) -> str:
        """Получить рамку для персонажа.

        Args:
            character_name: Имя персонажа

        Returns:
            ASCII рамка с именем

        Raises:
            AsciiArtError: Ошибка получения рамки
        """
        pass

    @abstractmethod
    def get_separator(self, length: int, char: str = "=") -> str:
        """Получить разделитель.

        Args:
            length: Длина разделителя
            char: Символ разделителя

        Returns:
            ASCII разделитель

        Raises:
            AsciiArtError: Ошибка получения разделителя
        """
        pass


class AsciiArtError(Exception):
    """Ошибка сервиса ASCII art."""

    pass
