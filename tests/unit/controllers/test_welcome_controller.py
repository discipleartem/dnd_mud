"""Unit тесты для WelcomeController.

Следует Clean Architecture - тестируем Controller в изоляции
с использованием моков для Use Cases.
"""

import pytest
from unittest.mock import Mock

from src.controllers.welcome_controller import WelcomeController, WelcomeControllerRequest, WelcomeControllerResponse
from src.use_cases.welcome_user import WelcomeUserUseCase
from src.dto.welcome_dto import WelcomeRequest, WelcomeResponse


class TestWelcomeController:
    """Тесты для WelcomeController."""

    def setup_method(self) -> None:
        """Настройка тестов."""
        self.mock_use_case = Mock(spec=WelcomeUserUseCase)
        self.controller = WelcomeController(welcome_use_case=self.mock_use_case)

    def test_show_welcome_success(self) -> None:
        """Тест успешного отображения приветствия."""
        # Настройка мока Use Case
        expected_use_case_response = WelcomeResponse(
            title="Добро пожаловать в D&D MUD",
            subtitle="Текстовая MUD игра",
            description="Создайте персонажа и исследуйте мир",
            ascii_art="ASCII LOGO",
            language="ru",
            press_enter_text="Нажмите Enter для продолжения..."
        )
        self.mock_use_case.execute.return_value = expected_use_case_response

        # Выполнение
        controller_request = WelcomeControllerRequest(language="ru", show_ascii_art=True)
        response = self.controller.show_welcome(controller_request)

        # Проверки
        assert isinstance(response, WelcomeControllerResponse)
        assert response.success is True
        assert response.data is not None
        assert response.data["title"] == "Добро пожаловать в D&D MUD"
        assert response.data["subtitle"] == "Текстовая MUD игра"
        assert response.data["description"] == "Создайте персонажа и исследуйте мир"
        assert response.data["ascii_art"] == "ASCII LOGO"
        assert response.data["language"] == "ru"
        assert response.data["press_enter_text"] == "Нажмите Enter для продолжения..."

        # Проверка вызова Use Case
        self.mock_use_case.execute.assert_called_once()
        call_args = self.mock_use_case.execute.call_args[0][0]
        assert isinstance(call_args, WelcomeRequest)
        assert call_args.language == "ru"
        assert call_args.show_ascii_art is True

    def test_show_welcome_without_ascii_art(self) -> None:
        """Тест отображения приветствия без ASCII-арта."""
        expected_use_case_response = WelcomeResponse(
            title="Welcome to D&D MUD",
            subtitle="Text MUD game",
            description="Create a character and explore",
            ascii_art=None,
            language="en",
            press_enter_text="Press Enter to continue..."
        )
        self.mock_use_case.execute.return_value = expected_use_case_response

        controller_request = WelcomeControllerRequest(language="en", show_ascii_art=False)
        response = self.controller.show_welcome(controller_request)

        assert response.success is True
        assert response.data["title"] == "Welcome to D&D MUD"
        assert response.data["ascii_art"] is None
        assert response.data["language"] == "en"

    def test_show_welcome_use_case_exception(self) -> None:
        """Тест обработки исключения от Use Case."""
        self.mock_use_case.execute.side_effect = Exception("Use Case error")

        controller_request = WelcomeControllerRequest(language="ru", show_ascii_art=True)
        response = self.controller.show_welcome(controller_request)

        assert response.success is False
        assert response.error is not None
        assert "Use Case error" in response.error
        assert response.data is None

    def test_transform_request_data(self) -> None:
        """Тест преобразования данных запроса."""
        controller_request = WelcomeControllerRequest(language="en", show_ascii_art=False)
        
        # Вызываем внутренний метод напрямую для тестирования
        use_case_request = self.controller._transform_request_data(controller_request)
        
        assert isinstance(use_case_request, WelcomeRequest)
        assert use_case_request.language == "en"
        assert use_case_request.show_ascii_art is False

    def test_transform_response_data(self) -> None:
        """Тест преобразования данных ответа."""
        use_case_response = WelcomeResponse(
            title="Test Title",
            subtitle="Test Subtitle",
            description="Test Description",
            ascii_art="Test ASCII",
            language="test",
            press_enter_text="Test Press"
        )
        
        # Вызываем внутренний метод напрямую для тестирования
        controller_response_data = self.controller._transform_response_data(use_case_response)
        
        assert isinstance(controller_response_data, dict)
        assert controller_response_data["title"] == "Test Title"
        assert controller_response_data["subtitle"] == "Test Subtitle"
        assert controller_response_data["description"] == "Test Description"
        assert controller_response_data["ascii_art"] == "Test ASCII"
        assert controller_response_data["language"] == "test"
        assert controller_response_data["press_enter_text"] == "Test Press"

    def test_transform_response_data_with_none_ascii(self) -> None:
        """Тест преобразования ответа с None ASCII."""
        use_case_response = WelcomeResponse(
            title="Test Title",
            subtitle="Test Subtitle",
            description="Test Description",
            ascii_art=None,
            language="test",
            press_enter_text="Test Press"
        )
        
        controller_response_data = self.controller._transform_response_data(use_case_response)
        
        assert controller_response_data["ascii_art"] is None

    def test_controller_request_dataclass(self) -> None:
        """Тест DTO запроса контроллера."""
        request = WelcomeControllerRequest(language="ru", show_ascii_art=True)
        
        assert request.language == "ru"
        assert request.show_ascii_art is True

    def test_controller_response_dataclass_success(self) -> None:
        """Тест DTO ответа контроллера при успехе."""
        response = WelcomeControllerResponse(
            success=True,
            data={"title": "Test"},
            error=None
        )
        
        assert response.success is True
        assert response.data == {"title": "Test"}
        assert response.error is None

    def test_controller_response_dataclass_error(self) -> None:
        """Тест DTO ответа контроллера при ошибке."""
        response = WelcomeControllerResponse(
            success=False,
            data=None,
            error="Error message"
        )
        
        assert response.success is False
        assert response.data is None
        assert response.error == "Error message"

    def test_controller_depends_only_on_use_case(self) -> None:
        """Тест что контроллер зависит только от Use Case."""
        # Контроллер должен зависеть только от Use Case
        # и не должен зависеть от внешних сервисов напрямую
        assert hasattr(self.controller, '_welcome_use_case')
        assert self.controller._welcome_use_case == self.mock_use_case
        
        # Нет прямых зависимостей от TranslationService, AsciiArtService и т.д.
        assert not hasattr(self.controller, '_translation_service')
        assert not hasattr(self.controller, '_ascii_art_service')

    def test_controller_transforms_data_correctly(self) -> None:
        """Тест правильности преобразования данных."""
        # Тестируем полный цикл преобразования
        controller_request = WelcomeControllerRequest(language="test", show_ascii_art=True)
        
        # Use Case ответ
        use_case_response = WelcomeResponse(
            title="Original Title",
            subtitle="Original Subtitle", 
            description="Original Description",
            ascii_art="Original ASCII",
            language="original",
            press_enter_text="Original Press"
        )
        self.mock_use_case.execute.return_value = use_case_response
        
        # Выполняем контроллер
        response = self.controller.show_welcome(controller_request)
        
        # Проверяем что данные преобразованы корректно
        assert response.success is True
        assert response.data["title"] == "Original Title"
        assert response.data["language"] == "original"

    @pytest.mark.timeout(5)
    def test_controller_performance_timeout(self) -> None:
        """Тест производительности контроллера с таймаутом."""
        self.mock_use_case.execute.return_value = WelcomeResponse(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art=None,
            language="ru",
            press_enter_text="Press"
        )
        
        request = WelcomeControllerRequest(language="ru", show_ascii_art=False)
        response = self.controller.show_welcome(request)
        
        assert response is not None
        assert response.success is True

    def test_controller_handles_none_use_case_response(self) -> None:
        """Тест обработки None ответа от Use Case."""
        self.mock_use_case.execute.return_value = None
        
        request = WelcomeControllerRequest(language="ru", show_ascii_art=False)
        
        # Должен обработать ошибку
        with pytest.raises(AttributeError):
            # Это должно вызвать ошибку, т.к. None не имеет атрибутов
            self.controller._transform_response_data(None)

    def test_controller_request_validation(self) -> None:
        """Тест валидации запроса контроллера."""
        # Контроллер не должен валидировать данные - это задача Use Case
        # Он должен только передавать данные дальше
        
        invalid_request = WelcomeControllerRequest(language="", show_ascii_art=True)
        use_case_request = self.controller._transform_request_data(invalid_request)
        
        # Данные передаются как есть
        assert use_case_request.language == ""
        assert use_case_request.show_ascii_art is True
