"""DTO для приветственного экрана.

Следует Clean Architecture - DTO для передачи данных между слоями.
"""

from dataclasses import dataclass
from typing import Optional


# Controller Layer DTO
@dataclass
class WelcomeControllerRequest:
    """Запрос контроллера приветствия."""
    
    language: Optional[str] = None
    show_ascii_art: Optional[bool] = None


@dataclass
class WelcomeControllerResponse:
    """Ответ контроллера приветствия."""
    
    success: bool
    message: str
    data: Optional[dict] = None


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
    ascii_art: Optional[str]
    language: str
    press_enter_text: str
