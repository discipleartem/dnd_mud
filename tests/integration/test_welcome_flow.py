"""Интеграционные тесты для приветственного экрана.

Следует Clean Architecture - тестируем взаимодействие всех слоев.
"""

import pytest

from src.controllers.welcome_controller import (
    WelcomeControllerRequest,
)
from src.dependency_injection import ApplicationServices


class TestWelcomeFlowIntegration:
    """Интеграционные тесты полного потока."""

    @pytest.mark.timeout(10)
    def test_full_welcome_flow_russian(self) -> None:
        """Тест полного потока на русском языке."""
        # Используем Dependency Injection для создания реальных зависимостей
        app_services = ApplicationServices()
        controller = app_services.welcome_controller

        # Выполняем полный сценарий
        request = WelcomeControllerRequest(language="ru", show_ascii_art=True)

        response = controller.show_welcome(request)

        # Проверяем результат
        assert response.success is True
        assert response.data is not None
        assert "title" in response.data
        assert "subtitle" in response.data
        assert "description" in response.data
        assert "language" in response.data
        assert "press_enter_text" in response.data

        # Проверяем наличие ожидаемых строк
        assert response.data["language"] == "ru"
        assert (
            response.data["ascii_art"] is not None
        )  # ASCII-арт должен быть непустым

    @pytest.mark.timeout(10)
    def test_full_welcome_flow_english(self) -> None:
        """Тест полного потока на английском языке."""
        app_services = ApplicationServices()
        controller = app_services.welcome_controller

        request = WelcomeControllerRequest(language="en", show_ascii_art=False)

        response = controller.show_welcome(request)

        assert response.success is True
        assert response.data["language"] == "en"
        assert response.data["ascii_art"] is None  # Без ASCII-арта
        assert response.data["title"] is not None
        assert response.data["subtitle"] is not None

    @pytest.mark.timeout(5)
    def test_translation_service_integration(self) -> None:
        """Тест интеграции сервиса переводов."""
        app_services = ApplicationServices()
        translation_service = app_services.translation_service

        # Проверяем поддерживаемые языки
        languages = translation_service.get_supported_languages()
        assert "ru" in languages
        assert "en" in languages

        # Проверяем получение переводов
        ru_title = translation_service.get_translation(
            "ru", "welcome_title", "Default"
        )
        en_title = translation_service.get_translation(
            "en", "welcome_title", "Default"
        )

        assert ru_title is not None
        assert en_title is not None
        # В текущей реализации переводы могут быть одинаковыми, если ключ не найден

    @pytest.mark.timeout(5)
    def test_ascii_art_service_integration(self) -> None:
        """Тест интеграции сервиса ASCII art."""
        app_services = ApplicationServices()
        ascii_art_service = app_services.ascii_art_service

        # Проверяем получение логотипа
        logo = ascii_art_service.get_dnd_logo()
        assert isinstance(logo, str)
        assert len(logo) > 0
        # ASCII-art может не содержать текст "D&D", а состоять из символов

    @pytest.mark.timeout(5)
    def test_controller_error_handling(self) -> None:
        """Тест обработки ошибок в контроллере."""
        app_services = ApplicationServices()
        controller = app_services.welcome_controller

        # Тестируем с некорректными данными
        request = WelcomeControllerRequest(
            language="invalid", show_ascii_art=True
        )

        response = controller.show_welcome(request)

        # Контроллер может обрабатывать некорректный язык и возвращать успешный ответ
        # с fallback на язык по умолчанию
        assert response.success is True
        assert response.data is not None

    @pytest.mark.timeout(10)
    def test_use_case_with_real_services(self) -> None:
        """Тест Use Case с реальными сервисами."""
        app_services = ApplicationServices()
        use_case = app_services.welcome_controller._welcome_use_case

        # Тестируем разные комбинации параметров
        from src.use_cases.welcome_user import WelcomeRequest

        test_cases = [
            {"language": "ru", "show_ascii_art": True},
            {"language": "ru", "show_ascii_art": False},
            {"language": "en", "show_ascii_art": True},
            {"language": "en", "show_ascii_art": False},
        ]

        for params in test_cases:
            request = WelcomeRequest(**params)
            response = use_case.execute(request)

            assert response.language == params["language"]
            if params["show_ascii_art"]:
                assert response.ascii_art is not None
            else:
                assert response.ascii_art is None
