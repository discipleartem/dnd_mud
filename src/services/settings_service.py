"""Сервис настроек игры.

Следует Clean Architecture - реализация в слое Services.
Обеспечивает сохранение и загрузку настроек.
"""

import json
from pathlib import Path
from typing import Any

from src.entities.settings_entity import GameSettings, Setting, SettingType
from src.interfaces.services.settings_service_interface import (
    SettingsServiceInterface,
)


class FileSettingsService(SettingsServiceInterface):
    """Файловый сервис настроек.

    Сохраняет настройки в JSON файл.
    """

    def __init__(self, settings_file: str = "data/settings.json") -> None:
        """Инициализация сервиса.

        Args:
            settings_file: Путь к файлу настроек
        """
        self.settings_file = Path(settings_file)
        self._ensure_settings_directory()

    def _ensure_settings_directory(self) -> None:
        """Создать директорию для настроек."""
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)

    def load_settings(self) -> GameSettings:
        """Загрузить настройки из файла.

        Returns:
            Загруженные настройки
        """
        if not self.settings_file.exists():
            # Если файла нет, создаем настройки по умолчанию
            default_settings = self._create_default_settings()
            self.save_settings(default_settings)
            return default_settings

        try:
            with open(self.settings_file, encoding="utf-8") as f:
                data = json.load(f)

            settings = GameSettings()

            for key, setting_data in data.items():
                setting = self._create_setting_from_data(key, setting_data)
                if setting:
                    settings.add_setting(setting)

            return settings

        except (OSError, json.JSONDecodeError):
            # При ошибке загрузки возвращаем настройки по умолчанию
            default_settings = self._create_default_settings()
            self.save_settings(default_settings)
            return default_settings

    def save_settings(self, settings: GameSettings) -> bool:
        """Сохранить настройки в файл.

        Args:
            settings: Настройки для сохранения

        Returns:
            True если настройки сохранены
        """
        try:
            settings_data = settings.to_dict()

            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)

            return True

        except OSError:
            return False

    def get_setting(self, key: str) -> Setting | None:
        """Получить настройку по ключу.

        Args:
            key: Ключ настройки

        Returns:
            Настройка или None
        """
        settings = self.load_settings()
        return settings.get_setting(key)

    def set_setting(self, key: str, value: Any) -> bool:
        """Установить значение настройки.

        Args:
            key: Ключ настройки
            value: Новое значение

        Returns:
            True если значение установлено
        """
        settings = self.load_settings()
        return settings.set_value(key, value)

    def get_value(self, key: str, default: Any = None) -> Any:
        """Получить значение настройки.

        Args:
            key: Ключ настройки
            default: Значение по умолчанию

        Returns:
            Значение настройки или default
        """
        settings = self.load_settings()
        return settings.get_value(key, default)

    def get_all_settings(self) -> list[Setting]:
        """Получить все настройки.

        Returns:
            Список всех настроек
        """
        settings = self.load_settings()
        return list(settings.settings.values())

    def reset_to_defaults(self) -> bool:
        """Сбросить настройки к умолчанию.

        Returns:
            True если настройки сброшены
        """
        default_settings = self._create_default_settings()
        return self.save_settings(default_settings)

    def export_settings(self) -> dict[str, Any] | None:
        """Экспортировать настройки.

        Returns:
            Словарь с настройками или None
        """
        try:
            settings = self.load_settings()
            return {
                key: setting.get_value()
                for key, setting in settings.settings.items()
            }
        except Exception:
            return None

    def import_settings(self, settings_data: dict[str, Any]) -> bool:
        """Импортировать настройки.

        Args:
            settings_data: Данные настроек

        Returns:
            True если настройки импортированы
        """
        try:
            settings = self.load_settings()

            for key, value in settings_data.items():
                if not settings.set_value(key, value):
                    return False

            return self.save_settings(settings)

        except Exception:
            return False

    def _create_default_settings(self) -> GameSettings:
        """Создать настройки по умолчанию.

        Returns:
            Настройки по умолчанию
        """
        settings = GameSettings()

        # Хардкор режим
        hardcore_setting = Setting(
            key="hardcore_mode",
            title="Хардкор режим",
            description="Включить повышенную сложность игры",
            setting_type=SettingType.INTEGER,
            default_value=False,
        )
        settings.add_setting(hardcore_setting)

        return settings

    def _create_setting_from_data(
        self, key: str, data: dict[str, Any]
    ) -> Setting | None:
        """Создать настройку из данных.

        Args:
            key: Ключ настройки
            data: Данные настройки

        Returns:
            Настройка или None если данные невалидны
        """
        try:
            setting_type = SettingType(data.get("type", "string"))

            return Setting(
                key=key,
                title=data.get("title", ""),
                description=data.get("description", ""),
                setting_type=setting_type,
                default_value=data.get("default_value"),
                min_value=data.get("min_value"),
                max_value=data.get("max_value"),
                options=data.get("options"),
                requires_restart=data.get("requires_restart", False),
            )
        except (ValueError, TypeError):
            return None
