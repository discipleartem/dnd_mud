"""Сущность приветственного экрана.

Следует Clean Architecture - простая бизнес-сущность
только с данными, без внешних зависимостей и бизнес-логики.
"""

from dataclasses import dataclass


@dataclass
class WelcomeScreen:
    """Бизнес-сущность приветственного экрана.

    Следует Clean Architecture - содержит только данные.
    Вся бизнес-логика вынесена в Use Cases.
    """

    title: str
    subtitle: str
    description: str
    ascii_art: str | None = None
    language: str = "ru"
    press_enter_text: str = "Нажмите Enter для продолжения..."

    def has_ascii_art(self) -> bool:
        """Проверить наличие ASCII-арта."""
        return self.ascii_art is not None and self.ascii_art.strip() != ""

    def __str__(self) -> str:
        """Строковое представление сущности."""
        return (
            f"WelcomeScreen(title='{self.title}', "
            f"language='{self.language}', "
            f"has_ascii={self.has_ascii_art()})"
        )
