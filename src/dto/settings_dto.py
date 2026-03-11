"""DTO для передачи данных настроек между слоями.

Следует Clean Architecture - объекты для передачи данных.
Используются для коммуникации между Controller и Use Case.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from src.entities.settings_entity import Setting, SettingType


@dataclass
class SettingsControllerRequest:
    """Запрос к контроллеру настроек."""
    action: str  # "get", "set", "reset", "export", "import"
    key: Optional[str] = None
    value: Optional[Any] = None
    settings_data: Optional[Dict[str, Any]] = None


@dataclass
class SettingsControllerResponse:
    """Ответ контроллера настроек."""
    success: bool
    message: str
    setting: Optional[Setting] = None
    all_settings: Optional[List[Setting]] = None
    value: Optional[Any] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class SettingDTO:
    """DTO для настройки."""
    key: str
    title: str
    description: str
    setting_type: SettingType
    default_value: Any
    current_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[Dict[str, str]] = None
    requires_restart: bool = False
    
    @classmethod
    def from_entity(cls, setting: Setting) -> 'SettingDTO':
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
            current_value=setting.current_value,
            min_value=setting.min_value,
            max_value=setting.max_value,
            options=setting.options,
            requires_restart=setting.requires_restart
        )


@dataclass
class SettingsStateDTO:
    """DTO для состояния настроек."""
    settings: List[SettingDTO]
    language: str
    hardcore_mode: bool
    auto_save_interval: int
    volume: int
    
    @classmethod
    def from_settings(cls, settings) -> 'SettingsStateDTO':
        """Создать DTO из настроек.
        
        Args:
            settings: Настройки игры
            
        Returns:
            DTO состояния настроек
        """
        setting_dtos = []
        for setting in settings.settings.values():
            setting_dtos.append(SettingDTO.from_entity(setting))
        
        return cls(
            settings=setting_dtos,
            language=settings.get_value("language", "ru"),
            hardcore_mode=settings.get_value("hardcore_mode", False),
            auto_save_interval=settings.get_value("auto_save_interval", 10),
            volume=settings.get_value("volume", 80)
        )
