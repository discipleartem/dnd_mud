"""Модуль конфигурации игры.

Этот модуль предоставляет управление настройками игры
и конфигурацией системы.
"""

from .settings_manager import SettingsManager, get_settings_manager

__all__ = ["SettingsManager", "get_settings_manager"]
