"""DTO для приветственного экрана.

Следует Clean Architecture - DTO для передачи данных между слоями.
"""

from dataclasses import dataclass


# Controller Layer DTO
@dataclass
class WelcomeControllerRequest:
    """Запрос контроллера приветствия."""

    language: str | None = None
    show_ascii_art: bool | None = None


@dataclass
class WelcomeControllerResponse:
    """Ответ контроллера приветствия."""

    success: bool
    message: str
    data: dict | None = None


# Use Case Layer DTO
@dataclass
class WelcomeRequest:
    """Запрос на приветствие."""

    language: str = "ru"
    show_ascii_art: bool = True


@dataclass
class WelcomeResponse:
    """Ответ с данными приветствия."""

    title: str
    subtitle: str
    description: str
    ascii_art: str | None
    language: str
    press_enter_text: str
