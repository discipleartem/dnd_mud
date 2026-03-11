"""Интерфейсы репозиториев.

Следует Clean Architecture - интерфейсы для доступа к данным.
"""

from .character_repository import CharacterRepository, RepositoryError
from .welcome_repository import WelcomeRepository

__all__ = ["CharacterRepository", "WelcomeRepository", "RepositoryError"]
