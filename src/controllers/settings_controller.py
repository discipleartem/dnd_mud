"""Контроллер настроек.

Следует Clean Architecture - преобразует данные между слоями.
Управляет настройками игры.
"""

from typing import Optional, Dict, Any, List

from src.dto.settings_dto import (
    SettingsControllerRequest,
    SettingsControllerResponse,
    SettingsStateDTO,
    SettingDTO
)
from src.use_cases.settings_use_case import SettingsUseCase
from src.entities.settings_entity import Setting


class SettingsController:
    """Контроллер настроек.
    
    Следует Clean Architecture - управляет настройками игры,
    преобразуя пользовательский ввод в действия.
    """
    
    def __init__(self, settings_use_case: SettingsUseCase) -> None:
        """Инициализация контроллера.
        
        Args:
            settings_use_case: Use Case настроек
        """
        self._settings_use_case = settings_use_case
        self._current_settings: Optional[SettingsStateDTO] = None
    
    def initialize_settings(self) -> SettingsControllerResponse:
        """Инициализировать настройки.
        
        Returns:
            Ответ контроллера с состоянием настроек
        """
        try:
            settings = self._settings_use_case.initialize_settings()
            self._current_settings = SettingsStateDTO.from_settings(settings)
            
            return SettingsControllerResponse(
                success=True,
                message="Настройки инициализированы",
                all_settings=self._current_settings.settings
            )
            
        except Exception as e:
            return SettingsControllerResponse(
                success=False,
                message=f"Ошибка инициализации настроек: {str(e)}"
            )
    
    def handle_request(self, request: SettingsControllerRequest) -> SettingsControllerResponse:
        """Обработать запрос настроек.
        
        Args:
            request: Запрос контроллера
            
        Returns:
            Ответ контроллера с результатом
        """
        try:
            if request.action == "get":
                return self._handle_get_request(request)
            elif request.action == "set":
                return self._handle_set_request(request)
            elif request.action == "reset":
                return self._handle_reset_request()
            elif request.action == "export":
                return self._handle_export_request()
            elif request.action == "import":
                return self._handle_import_request(request)
            else:
                return SettingsControllerResponse(
                    success=False,
                    message=f"Неизвестное действие: {request.action}"
                )
                
        except Exception as e:
            return SettingsControllerResponse(
                success=False,
                message=f"Ошибка обработки запроса: {str(e)}"
            )
    
    def get_current_settings(self) -> Optional[SettingsStateDTO]:
        """Получить текущие настройки.
        
        Returns:
            Текущие настройки или None
        """
        return self._current_settings
    
    def _handle_get_request(self, request: SettingsControllerRequest) -> SettingsControllerResponse:
        """Обработать запрос получения настройки.
        
        Args:
            request: Запрос на получение
            
        Returns:
            Ответ с настройкой
        """
        if request.key:
            # Получить конкретную настройку
            setting = self._settings_use_case.get_setting(request.key)
            if setting:
                setting_dto = SettingDTO.from_entity(setting)
                return SettingsControllerResponse(
                    success=True,
                    message="Настройка получена",
                    setting=setting_dto,
                    value=setting.get_value()
                )
            else:
                return SettingsControllerResponse(
                    success=False,
                    message=f"Настройка не найдена: {request.key}"
                )
        else:
            # Получить все настройки
            settings = self._settings_use_case.get_all_settings()
            setting_dtos = [SettingDTO.from_entity(s) for s in settings]
            
            return SettingsControllerResponse(
                success=True,
                message="Все настройки получены",
                all_settings=setting_dtos
            )
    
    def _handle_set_request(self, request: SettingsControllerRequest) -> SettingsControllerResponse:
        """Обработать запрос установки настройки.
        
        Args:
            request: Запрос на установку
            
        Returns:
            Ответ с результатом
        """
        if not request.key or request.value is None:
            return SettingsControllerResponse(
                success=False,
                message="Не указан ключ или значение настройки"
            )
        
        success = self._settings_use_case.set_setting(request.key, request.value)
        
        if success:
            # Обновляем текущие настройки
            settings = self._settings_use_case.initialize_settings()
            self._current_settings = SettingsStateDTO.from_settings(settings)
            
            setting = self._settings_use_case.get_setting(request.key)
            setting_dto = SettingDTO.from_entity(setting) if setting else None
            
            return SettingsControllerResponse(
                success=True,
                message="Настройка обновлена",
                setting=setting_dto,
                value=request.value
            )
        else:
            return SettingsControllerResponse(
                success=False,
                message="Не удалось установить настройку"
            )
    
    def _handle_reset_request(self) -> SettingsControllerResponse:
        """Обработать запрос сброса настроек.
        
        Returns:
            Ответ с результатом
        """
        success = self._settings_use_case.reset_to_defaults()
        
        if success:
            # Обновляем текущие настройки
            settings = self._settings_use_case.initialize_settings()
            self._current_settings = SettingsStateDTO.from_settings(settings)
            
            return SettingsControllerResponse(
                success=True,
                message="Настройки сброшены к умолчанию",
                all_settings=self._current_settings.settings
            )
        else:
            return SettingsControllerResponse(
                success=False,
                message="Не удалось сбросить настройки"
            )
    
    def _handle_export_request(self) -> SettingsControllerResponse:
        """Обработать запрос экспорта настроек.
        
        Returns:
            Ответ с результатом
        """
        settings_data = self._settings_use_case.export_settings()
        
        if settings_data is not None:
            return SettingsControllerResponse(
                success=True,
                message="Настройки экспортированы",
                data=settings_data
            )
        else:
            return SettingsControllerResponse(
                success=False,
                message="Не удалось экспортировать настройки"
            )
    
    def _handle_import_request(self, request: SettingsControllerRequest) -> SettingsControllerResponse:
        """Обработать запрос импорта настроек.
        
        Args:
            request: Запрос на импорт
            
        Returns:
            Ответ с результатом
        """
        if not request.settings_data:
            return SettingsControllerResponse(
                success=False,
                message="Не указаны данные для импорта"
            )
        
        success = self._settings_use_case.import_settings(request.settings_data)
        
        if success:
            # Обновляем текущие настройки
            settings = self._settings_use_case.initialize_settings()
            self._current_settings = SettingsStateDTO.from_settings(settings)
            
            return SettingsControllerResponse(
                success=True,
                message="Настройки импортированы",
                all_settings=self._current_settings.settings
            )
        else:
            return SettingsControllerResponse(
                success=False,
                message="Не удалось импортировать настройки"
            )
