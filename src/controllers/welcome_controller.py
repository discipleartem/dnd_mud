"""Контроллер приветственного экрана.

Следует Clean Architecture - преобразует данные между слоями.
Зависит от Use Cases и Entities.
"""

from dataclasses import dataclass
from typing import Optional

from src.dto.welcome_dto import (
    WelcomeControllerRequest, 
    WelcomeControllerResponse,
    WelcomeRequest,
    WelcomeResponse
)
from src.use_cases.welcome_user import WelcomeUserUseCase


class WelcomeController:
    """Контроллер приветственного экрана.
    
    Следует Clean Architecture - преобразует входные данные
    в запросы Use Case и ответы в формат для отображения.
    """
    
    def __init__(self, welcome_use_case: WelcomeUserUseCase) -> None:
        """Инициализация контроллера.
        
        Args:
            welcome_use_case: Use Case приветствия
        """
        self._welcome_use_case = welcome_use_case
    
    def show_welcome(self, request: WelcomeControllerRequest) -> WelcomeControllerResponse:
        """Показать приветственный экран.
        
        Args:
            request: Запрос контроллера
            
        Returns:
            Ответ контроллера с данными для отображения
        """
        try:
            # Преобразование запроса контроллера в запрос Use Case
            use_case_request = self._transform_request(request)
            
            # Выполнение Use Case
            use_case_response = self._welcome_use_case.execute(use_case_request)
            
            # Прямое преобразование ответа Use Case в данные для UI
            return self._transform_response(use_case_response)
            
        except Exception as e:
            return WelcomeControllerResponse(
                success=False,
                message=f"Ошибка в контроллере приветствия: {str(e)}",
                data=None
            )
    
    def get_supported_languages(self) -> WelcomeControllerResponse:
        """Получить поддерживаемые языки.
        
        Returns:
            Ответ со списком языков
        """
        try:
            languages = self._welcome_use_case.get_supported_languages()
            
            return WelcomeControllerResponse(
                success=True,
                message="Список поддерживаемых языков получен",
                data={"languages": languages}
            )
            
        except Exception as e:
            return WelcomeControllerResponse(
                success=False,
                message=f"Ошибка получения языков: {str(e)}",
                data=None
            )
    
    def _transform_request(self, request: WelcomeControllerRequest) -> WelcomeRequest:
        """Преобразовать запрос контроллера в запрос Use Case.
        
        Args:
            request: Запрос контроллера
            
        Returns:
            Запрос Use Case
        """
        # Установка значений по умолчанию
        language = request.language if request.language is not None else "ru"
        show_ascii_art = request.show_ascii_art if request.show_ascii_art is not None else True
        
        return WelcomeRequest(
            language=language,
            show_ascii_art=show_ascii_art
        )
    
    def _transform_response(self, response: WelcomeResponse) -> WelcomeControllerResponse:
        """Преобразовать ответ Use Case в ответ контроллера.
        
        Args:
            response: Ответ Use Case
            
        Returns:
            Ответ контроллера
        """
        return WelcomeControllerResponse(
            success=True,
            message="Приветственный экран подготовлен",
            data={
                "title": response.title,
                "subtitle": response.subtitle,
                "description": response.description,
                "ascii_art": response.ascii_art,
                "language": response.language,
                "press_enter_text": response.press_enter_text,
                "has_ascii_art": response.ascii_art is not None and response.ascii_art.strip() != ""
            }
        )