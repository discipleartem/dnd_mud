"""Data Transfer Objects.

DTO используются для передачи данных между слоями архитектуры.
Следуют Clean Architecture - не содержат бизнес-логики.
"""

from .welcome_dto import (
    WelcomeControllerRequest,
    WelcomeControllerResponse,
    WelcomeRequest,
    WelcomeResponse
)

__all__ = [
    "WelcomeControllerRequest",
    "WelcomeControllerResponse", 
    "WelcomeRequest",
    "WelcomeResponse"
]
