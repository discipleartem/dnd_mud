"""DTO для передачи данных настроек между слоями.

Следует Clean Architecture - объекты для передачи данных.
Используются для коммуникации между Controller и Use Case.
"""

from dataclasses import dataclass
from typing import Any

from src.entities.settings_entity import Setting, SettingType


@dataclass
class SettingDTO:
    """DTO для настройки."""

    key: str
    title: str
    description: str
    setting_type: SettingType
    default_value: Any
    min_value: Any | None = None
    max_value: Any | None = None
    options: list[str] | None = None
    requires_restart: bool = False

    @classmethod
    def from_setting(cls, setting: Setting) -> "SettingDTO":
        """Создать DTO из сущности.

        Args:
            setting: Сущность настройки

        Returns:
            DTO настройки
        """
        return cls(
            key=setting.key,
            title=setting.title,
            description=setting.description,
            setting_type=setting.setting_type,
            default_value=setting.default_value,
            min_value=setting.min_value,
            max_value=setting.max_value,
            options=list(setting.options.keys()) if setting.options else None,
            requires_restart=setting.requires_restart,
        )


@dataclass
class SettingsControllerRequest:
    """Запрос к контроллеру настроек."""

    action: str  # "get", "set", "reset", "export", "import"
    key: str | None = None
    value: Any | None = None
    settings_data: dict[str, Any] | None = None


@dataclass
class SettingsControllerResponse:
    """Ответ контроллера настроек."""

    success: bool
    message: str
    setting: SettingDTO | None = None
    all_settings: list[SettingDTO] | None = None
    value: Any | None = None
    data: dict[str, Any] | None = None


@dataclass
class SettingsStateDTO:
    """DTO для состояния настроек."""

    settings: list[SettingDTO]
    language: str
    hardcore_mode: bool
    auto_save_interval: int
    volume: int

    @classmethod
    def from_settings(cls, settings) -> "SettingsStateDTO":
        """Создать DTO из настроек.

        Args:
            settings: Настройки игры

        Returns:
            DTO состояния настроек
        """
        setting_dtos = []
        for setting in settings.settings.values():
            setting_dtos.append(SettingDTO.from_setting(setting))

        return cls(
            settings=setting_dtos,
            language=settings.get_value("language", "ru"),
            hardcore_mode=settings.get_value("hardcore_mode", False),
            auto_save_interval=settings.get_value("auto_save_interval", 10),
            volume=settings.get_value("volume", 80),
        )
