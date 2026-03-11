"""DTO для приветственного экрана."""

from dataclasses import dataclass


@dataclass
class WelcomeScreenRequest:
    """Запрос на отображение приветственного экрана."""
    language: str | None = None
    show_ascii_art: bool = True


@dataclass
class WelcomeScreenResponse:
    """Ответ с данными приветственного экрана."""
    title: str
    subtitle: str
    description: str
    ascii_art: str | None
    language: str
    press_enter_text: str
