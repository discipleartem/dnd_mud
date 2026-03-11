"""Сущность настроек игры.

Следует Clean Architecture - бизнес-сущность в слое Entities.
Определяет структуру и валидацию настроек.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SettingType(Enum):
    """Тип настройки."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LANGUAGE = "language"


@dataclass
class Setting:
    """Настройка игры.

    Определяет отдельную настройку с валидацией.
    """

    key: str
    title: str
    description: str
    setting_type: SettingType
    default_value: Any
    current_value: Any = field(init=False)
    min_value: float | None = None
    max_value: float | None = None
    options: dict[str, str] | None = None
    requires_restart: bool = False

    def __post_init__(self) -> None:
        """Пост-инициализация с валидацией."""
        # Устанавливаем текущее значение как значение по умолчанию
        if not hasattr(self, "current_value") or self.current_value is None:
            self.current_value = self.default_value

        # Валидация
        self._validate_setting()

    def _validate_setting(self) -> None:
        """Валидировать настройку.

        Raises:
            ValueError: Если настройка невалидна
        """
        if not self.key:
            raise ValueError("Ключ настройки не может быть пустым")

        if not self.title:
            raise ValueError("Заголовок настройки не может быть пустым")

        if self.setting_type == SettingType.INTEGER:
            if self.min_value is not None and self.max_value is not None:
                if self.min_value >= self.max_value:
                    raise ValueError("min_value должен быть меньше max_value")

        elif self.setting_type == SettingType.LANGUAGE:
            if not self.options:
                raise ValueError("Для языковой настройки нужны опции")

    def set_value(self, value: Any) -> bool:
        """Установить значение настройки.

        Args:
            value: Новое значение

        Returns:
            True если значение установлено, False если невалидно
        """
        if self._is_valid_value(value):
            self.current_value = value
            return True
        return False

    def get_value(self) -> Any:
        """Получить текущее значение настройки.

        Returns:
            Текущее значение
        """
        return self.current_value

    def reset_to_default(self) -> None:
        """Сбросить значение к умолчанию."""
        self.current_value = self.default_value

    def _is_valid_value(self, value: Any) -> bool:
        """Проверить валидность значения.

        Args:
            value: Значение для проверки

        Returns:
            True если значение валидно
        """
        if self.setting_type == SettingType.STRING:
            return isinstance(value, str)

        elif self.setting_type == SettingType.INTEGER:
            if not isinstance(value, int):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
            return True

        elif self.setting_type == SettingType.FLOAT:
            if not isinstance(value, (int, float)):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
            return True

        elif self.setting_type == SettingType.BOOLEAN:
            return isinstance(value, bool)

        elif self.setting_type == SettingType.LANGUAGE:
            if not isinstance(value, str):
                return False
            if self.options:
                return value in self.options
            return True

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать в словарь.

        Returns:
            Словарь с данными настройки
        """
        return {
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "type": self.setting_type.value,
            "default_value": self.default_value,
            "current_value": self.current_value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "options": self.options,
            "requires_restart": self.requires_restart,
        }


@dataclass
class GameSettings:
    """Настройки игры.

    Содержит все настройки игры с методами управления.
    """

    settings: dict[str, Setting] = field(default_factory=dict)

    def add_setting(self, setting: Setting) -> None:
        """Добавить настройку.

        Args:
            setting: Настройка для добавления
        """
        self.settings[setting.key] = setting

    def get_setting(self, key: str) -> Setting | None:
        """Получить настройку по ключу.

        Args:
            key: Ключ настройки

        Returns:
            Настройка или None если не найдена
        """
        return self.settings.get(key)

    def set_value(self, key: str, value: Any) -> bool:
        """Установить значение настройки.

        Args:
            key: Ключ настройки
            value: Новое значение

        Returns:
            True если значение установлено
        """
        setting = self.get_setting(key)
        if setting:
            return setting.set_value(value)
        return False

    def get_value(self, key: str, default: Any = None) -> Any:
        """Получить значение настройки.

        Args:
            key: Ключ настройки
            default: Значение по умолчанию

        Returns:
            Значение настройки или default
        """
        setting = self.get_setting(key)
        if setting:
            return setting.get_value()
        return default

    def reset_all(self) -> None:
        """Сбросить все настройки к умолчанию."""
        for setting in self.settings.values():
            setting.reset_to_default()

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать все настройки в словарь.

        Returns:
            Словарь со всеми настройками
        """
        return {
            key: setting.to_dict() for key, setting in self.settings.items()
        }
