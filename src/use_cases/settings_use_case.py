"""Use Case для управления настройками.

Следует Clean Architecture - бизнес-логика в слое Use Cases.
Оркестрирует операции с настройками.
"""

from typing import Any

from src.entities.settings_entity import GameSettings, Setting, SettingType
from src.interfaces.services.settings_service_interface import (
    SettingsServiceInterface,
)


class SettingsUseCase:
    """Use Case для управления настройками.

    Следует Clean Architecture - инкапсулирует бизнес-логику
    работы с настройками игры.
    """

    def __init__(self, settings_service: SettingsServiceInterface) -> None:
        """Инициализация Use Case.

        Args:
            settings_service: Сервис настроек
        """
        self._settings_service = settings_service
        self._game_settings: GameSettings | None = None

    def initialize_settings(self) -> GameSettings:
        """Инициализировать настройки.

        Returns:
            Инициализированные настройки
        """
        if self._game_settings is None:
            self._game_settings = self._settings_service.load_settings()
            self._ensure_default_settings()
        return self._game_settings

    def get_all_settings(self) -> list[Setting]:
        """Получить все настройки.

        Returns:
            Список всех настроек
        """
        self._ensure_settings_loaded()
        return self._settings_service.get_all_settings()

    def get_setting(self, key: str) -> Setting | None:
        """Получить настройку по ключу.

        Args:
            key: Ключ настройки

        Returns:
            Настройка или None
        """
        self._ensure_settings_loaded()
        return self._settings_service.get_setting(key)

    def get_value(self, key: str, default: Any = None) -> Any:
        """Получить значение настройки.

        Args:
            key: Ключ настройки
            default: Значение по умолчанию

        Returns:
            Значение настройки или default
        """
        self._ensure_settings_loaded()
        return self._settings_service.get_value(key, default)

    def set_setting(self, key: str, value: Any) -> bool:
        """Установить значение настройки.

        Args:
            key: Ключ настройки
            value: Новое значение

        Returns:
            True если значение установлено
        """
        self._ensure_settings_loaded()

        setting = self._settings_service.get_setting(key)
        if not setting:
            return False

        if setting._is_valid_value(value):
            success = self._settings_service.set_setting(key, value)
            if success and self._game_settings:
                # Сохраняем изменения
                self._settings_service.save_settings(self._game_settings)
            return success
        return False

    def reset_to_defaults(self) -> bool:
        """Сбросить настройки к умолчанию.

        Returns:
            True если настройки сброшены
        """
        self._ensure_settings_loaded()
        if self._game_settings:
            self._game_settings.reset_all()
            success = self._settings_service.save_settings(self._game_settings)
        else:
            success = False
        return success

    def export_settings(self) -> dict[str, Any] | None:
        """Экспортировать настройки.

        Returns:
            Словарь с настройками или None
        """
        self._ensure_settings_loaded()
        return self._settings_service.export_settings()

    def import_settings(self, settings_data: dict[str, Any]) -> bool:
        """Импортировать настройки.

        Args:
            settings_data: Данные настроек

        Returns:
            True если настройки импортированы
        """
        self._ensure_settings_loaded()

        # Валидация импортируемых данных
        if not self._validate_import_data(settings_data):
            return False

        success = self._settings_service.import_settings(settings_data)
        if success:
            # Перезагружаем настройки
            self._game_settings = self._settings_service.load_settings()
        return success

    def _ensure_settings_loaded(self) -> None:
        """Убедиться что настройки загружены."""
        if self._game_settings is None:
            self._game_settings = self._settings_service.load_settings()
            self._ensure_default_settings()

    def _ensure_default_settings(self) -> None:
        """Убедиться что все настройки по умолчанию существуют."""
        if not self._game_settings:
            return

        default_settings = self._create_default_settings()

        for setting in default_settings:
            if self._game_settings.get_setting(setting.key) is None:
                self._game_settings.add_setting(setting)

    def _create_default_settings(self) -> list[Setting]:
        """Создать настройки по умолчанию.

        Returns:
            Список настроек по умолчанию
        """
        return [
            Setting(
                key="hardcore_mode",
                title="Хардкор режим",
                description="Включить повышенную сложность игры",
                setting_type=SettingType.BOOLEAN,
                default_value=False,
            )
        ]

    def _validate_import_data(self, settings_data: dict[str, Any]) -> bool:
        """Валидировать импортируемые данные.

        Args:
            settings_data: Данные для валидации

        Returns:
            True если данные валидны
        """
        # Проверяем что все ключи известны
        if not self._game_settings:
            return False

        known_keys = {
            setting.key for setting in self._game_settings.settings.values()
        }
        for key in settings_data.keys():
            if key not in known_keys:
                return False

        return True
