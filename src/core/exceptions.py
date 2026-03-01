"""Пользовательские исключения D&D Text MUD."""

from typing import Any


class DnDMudError(Exception):
    """Базовое исключение игры.
    
    Наследуется всеми специфическими исключениями проекта.
    Позволяет единообразно обрабатывать ошибки игрового процесса.
    """
    
    def __init__(self, message: str, details: Any = None) -> None:
        """Инициализация исключения.
        
        Args:
            message: Сообщение об ошибке
            details: Дополнительные детали ошибки (опционально)
        """
        super().__init__(message)
        self.message = message
        self.details = details


class ConfigError(DnDMudError):
    """Ошибка конфигурации.
    
    Возникает при проблемах с загрузкой или сохранением настроек.
    """
    pass


class UIError(DnDMudError):
    """Ошибка пользовательского интерфейса.
    
    Возникает при проблемах с отображением или вводом данных.
    """
    pass


class GameError(DnDMudError):
    """Ошибка игрового процесса.
    
    Возникает при нарушениях игровой логики или состояния.
    """
    pass
