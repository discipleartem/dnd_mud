"""Сущность приветственного экрана.

Следует KISS и Zen Python - просто и явно.
"""

from dataclasses import dataclass

from src.value_objects.ascii_art import AsciiArt
from src.value_objects.language import Language
from src.value_objects.welcome_content import WelcomeContent


@dataclass
class WelcomeScreen:
    """Сущность приветственного экрана.

    Следует KISS - просто и понятно.
    """

    content: WelcomeContent
    ascii_art: AsciiArt | None = None
    language: Language = Language.create_default()
    press_enter_text: str = "Нажмите Enter для продолжения..."

    def __post_init__(self) -> None:
        """Базовая валидация после инициализации."""
        if not self.press_enter_text.strip():
            self.press_enter_text = "Нажмите Enter для продолжения..."

    def has_ascii_art(self) -> bool:
        """Проверить наличие ASCII-арта."""
        return self.ascii_art is not None and not self.ascii_art.is_empty()

    def __str__(self) -> str:
        """Строковое представление сущности."""
        return (
            f"WelcomeScreen(title='{self.content.get_title()}', "
            f"language='{self.language.get_code()}', "
            f"has_ascii={self.has_ascii_art()})"
        )
