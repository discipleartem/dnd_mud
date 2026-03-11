"""Unit тесты для WelcomeUserUseCase.

Следует Clean Architecture - тестируем Use Case в изоляции
с использованием моков для внешних зависимостей.
"""

from unittest.mock import Mock

import pytest

from src.dto.welcome_dto import WelcomeRequest, WelcomeResponse
from src.interfaces.services.ascii_art_service import AsciiArtService
from src.interfaces.services.translation_service_interface import (
    TranslationService,
)
from src.use_cases.welcome_user import WelcomeUserUseCase


class TestWelcomeUserUseCase:
    """Тесты для WelcomeUserUseCase."""

    def setup_method(self) -> None:
        """Настройка тестов."""
        self.mock_translation_service = Mock(spec=TranslationService)
        self.mock_ascii_art_service = Mock(spec=AsciiArtService)
        self.use_case = WelcomeUserUseCase(
            translation_service=self.mock_translation_service,
            ascii_art_service=self.mock_ascii_art_service,
        )

    def test_execute_success_with_ascii_art(self) -> None:
        """Тест успешного выполнения с ASCII-артом."""
        # Настройка моков
        self.mock_translation_service.is_language_supported.return_value = True
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: {
                (
                    "ru",
                    "welcome_title",
                    "Добро пожаловать в D&D MUD",
                ): "Добро пожаловать в D&D MUD",
                (
                    "ru",
                    "welcome_subtitle",
                    "Текстовая многопользовательская ролевая игра",
                ): "Текстовая MUD игра",
                (
                    "ru",
                    "welcome_description",
                    "Создайте персонажа...",
                ): "Создайте персонажа и исследуйте мир",
                (
                    "ru",
                    "press_enter",
                    "Нажмите Enter для продолжения...",
                ): "Нажмите Enter для продолжения...",
            }.get((lang, key, default), default)
        )
        self.mock_ascii_art_service.get_dnd_logo.return_value = "ASCII LOGO"

        # Выполнение
        request = WelcomeRequest(language="ru", show_ascii_art=True)
        response = self.use_case.execute(request)

        # Проверки
        assert isinstance(response, WelcomeResponse)
        assert response.title == "Добро пожаловать в D&D MUD"
        assert response.subtitle == "Текстовая MUD игра"
        assert response.language == "ru"
        assert response.ascii_art == "ASCII LOGO"
        assert response.press_enter_text == "Нажмите Enter для продолжения..."

        # Проверка вызовов моков
        self.mock_translation_service.is_language_supported.assert_called_once_with(
            "ru"
        )
        self.mock_ascii_art_service.get_dnd_logo.assert_called_once()

    def test_execute_success_without_ascii_art(self) -> None:
        """Тест успешного выполнения без ASCII-арта."""
        # Настройка моков
        self.mock_translation_service.is_language_supported.return_value = True
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: {
                (
                    "en",
                    "welcome_title",
                    "Добро пожаловать в D&D MUD",
                ): "Welcome to D&D MUD",
                (
                    "en",
                    "welcome_subtitle",
                    "Текстовая многопользовательская ролевая игра",
                ): "Text MUD game",
                (
                    "en",
                    "welcome_description",
                    "Создайте персонажа...",
                ): "Create a character and explore",
                (
                    "en",
                    "press_enter",
                    "Нажмите Enter для продолжения...",
                ): "Press Enter to continue...",
            }.get((lang, key, default), default)
        )

        # Выполнение
        request = WelcomeRequest(language="en", show_ascii_art=False)
        response = self.use_case.execute(request)

        # Проверки
        assert response.title == "Welcome to D&D MUD"
        assert response.subtitle == "Text MUD game"
        assert response.language == "en"
        assert response.ascii_art is None
        assert response.press_enter_text == "Press Enter to continue..."

        # Проверка что ASCII сервис не вызывался
        self.mock_ascii_art_service.get_dnd_logo.assert_not_called()

    def test_validate_language_empty_string(self) -> None:
        """Тест валидации пустой строки языка."""
        self.mock_translation_service.is_language_supported.return_value = True

        request = WelcomeRequest(language="", show_ascii_art=False)
        response = self.use_case.execute(request)

        assert response.language == "ru"  # Язык по умолчанию

    def test_validate_language_whitespace_only(self) -> None:
        """Тест валидации строки из пробелов."""
        self.mock_translation_service.is_language_supported.return_value = True

        request = WelcomeRequest(language="   ", show_ascii_art=False)
        response = self.use_case.execute(request)

        assert response.language == "ru"  # Язык по умолчанию

    def test_validate_language_unsupported_fallback_to_russian(self) -> None:
        """Тест fallback на русский при неподдерживаемом языке."""
        self.mock_translation_service.is_language_supported.return_value = (
            False
        )
        self.mock_translation_service.get_supported_languages.return_value = [
            "ru",
            "en",
        ]
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: default
        )

        request = WelcomeRequest(language="invalid", show_ascii_art=False)
        response = self.use_case.execute(request)

        assert response.language == "ru"

    def test_validate_language_unsupported_fallback_to_first_available(
        self,
    ) -> None:
        """Тест fallback на первый доступный язык."""
        self.mock_translation_service.is_language_supported.return_value = (
            False
        )
        self.mock_translation_service.get_supported_languages.return_value = [
            "en",
            "de",
        ]
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: default
        )

        request = WelcomeRequest(language="invalid", show_ascii_art=False)
        response = self.use_case.execute(request)

        assert response.language == "en"

    def test_validate_language_no_supported_languages_raises_error(
        self,
    ) -> None:
        """Тест ошибки при отсутствии поддерживаемых языков."""
        self.mock_translation_service.is_language_supported.return_value = (
            False
        )
        self.mock_translation_service.get_supported_languages.return_value = []

        request = WelcomeRequest(language="invalid", show_ascii_art=False)

        # Должен вернуть fallback response
        response = self.use_case.execute(request)
        assert response.title == "D&D Text MUD"

    def test_validate_content_missing_title(self) -> None:
        """Тест валидации контента с пустым заголовком."""
        self.mock_translation_service.is_language_supported.return_value = True
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: {
                ("ru", "welcome_title", "Добро пожаловать в D&D MUD"): "",
                (
                    "ru",
                    "welcome_subtitle",
                    "Текстовая многопользовательская ролевая игра",
                ): "Подзаголовок",
                (
                    "ru",
                    "welcome_description",
                    "Создайте персонажа...",
                ): "Описание",
                (
                    "ru",
                    "press_enter",
                    "Нажмите Enter для продолжения...",
                ): "Нажмите Enter",
            }.get((lang, key, default), default)
        )

        request = WelcomeRequest(language="ru", show_ascii_art=False)

        # Должен вернуть fallback response из-за ошибки валидации
        response = self.use_case.execute(request)
        assert response.title == "D&D Text MUD"

    def test_validate_content_missing_subtitle(self) -> None:
        """Тест валидации контента с пустым подзаголовком."""
        self.mock_translation_service.is_language_supported.return_value = True
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: {
                (
                    "ru",
                    "welcome_title",
                    "Добро пожаловать в D&D MUD",
                ): "Заголовок",
                (
                    "ru",
                    "welcome_subtitle",
                    "Текстовая многопользовательская ролевая игра",
                ): "",
                (
                    "ru",
                    "welcome_description",
                    "Создайте персонажа...",
                ): "Описание",
                (
                    "ru",
                    "press_enter",
                    "Нажмите Enter для продолжения...",
                ): "Нажмите Enter",
            }.get((lang, key, default), default)
        )

        request = WelcomeRequest(language="ru", show_ascii_art=False)

        # Должен вернуть fallback response
        response = self.use_case.execute(request)
        assert response.title == "D&D Text MUD"

    def test_validate_content_missing_description(self) -> None:
        """Тест валидации контента с пустым описанием."""
        self.mock_translation_service.is_language_supported.return_value = True
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: {
                (
                    "ru",
                    "welcome_title",
                    "Добро пожаловать в D&D MUD",
                ): "Заголовок",
                (
                    "ru",
                    "welcome_subtitle",
                    "Текстовая многопользовательская ролевая игра",
                ): "Подзаголовок",
                ("ru", "welcome_description", "Создайте персонажа..."): "",
                (
                    "ru",
                    "press_enter",
                    "Нажмите Enter для продолжения...",
                ): "Нажмите Enter",
            }.get((lang, key, default), default)
        )

        request = WelcomeRequest(language="ru", show_ascii_art=False)

        # Должен вернуть fallback response
        response = self.use_case.execute(request)
        assert response.title == "Заголовок"

    def test_validate_content_missing_press_enter_uses_default(self) -> None:
        """Тест использования значения по умолчанию для press_enter."""
        self.mock_translation_service.is_language_supported.return_value = True
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: {
                (
                    "ru",
                    "welcome_title",
                    "Добро пожаловать в D&D MUD",
                ): "Заголовок",
                (
                    "ru",
                    "welcome_subtitle",
                    "Текстовая многопользовательская ролевая игра",
                ): "Подзаголовок",
                (
                    "ru",
                    "welcome_description",
                    "Создайте персонажа...",
                ): "Описание",
                ("ru", "press_enter", "Нажмите Enter для продолжения..."): "",
            }.get((lang, key, default), default)
        )

        request = WelcomeRequest(language="ru", show_ascii_art=False)
        response = self.use_case.execute(request)

        # Должен установить значение по умолчанию
        assert response.press_enter_text == "Нажмите Enter для продолжения..."

    def test_exception_in_translation_service_returns_fallback(self) -> None:
        """Тест обработки исключения от translation сервиса."""
        self.mock_translation_service.is_language_supported.side_effect = (
            Exception("Service error")
        )

        request = WelcomeRequest(language="ru", show_ascii_art=False)
        response = self.use_case.execute(request)

        # Должен вернуть fallback response
        assert response.title == "D&D Text MUD"
        assert response.subtitle == "Текстовая многопользовательская игра"

    def test_exception_in_ascii_service_continues_without_ascii(self) -> None:
        """Тест обработки исключения от ASCII сервиса."""
        self.mock_translation_service.is_language_supported.return_value = True
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: default
        )
        self.mock_ascii_art_service.get_dnd_logo.side_effect = Exception(
            "ASCII error"
        )

        request = WelcomeRequest(language="ru", show_ascii_art=True)
        response = self.use_case.execute(request)

        # Должен продолжиться без ASCII-арта
        assert response.ascii_art is None

    def test_get_supported_languages_success(self) -> None:
        """Тест получения поддерживаемых языков."""
        self.mock_translation_service.get_supported_languages.return_value = [
            "ru",
            "en",
            "de",
        ]

        languages = self.use_case.get_supported_languages()

        assert languages == ["ru", "en", "de"]
        self.mock_translation_service.get_supported_languages.assert_called_once()

    def test_get_supported_languages_exception_returns_fallback(self) -> None:
        """Тест обработки исключения при получении языков."""
        self.mock_translation_service.get_supported_languages.side_effect = (
            Exception("Service error")
        )

        languages = self.use_case.get_supported_languages()

        assert languages == ["ru"]  # Fallback

    def test_fallback_response_with_ascii_art(self) -> None:
        """Тест fallback ответа с ASCII-артом."""
        self.mock_translation_service.is_language_supported.side_effect = (
            Exception("Service error")
        )

        request = WelcomeRequest(language="ru", show_ascii_art=True)
        response = self.use_case.execute(request)

        assert response.title == "D&D Text MUD"
        assert (
            response.ascii_art is None
        )  # Должен быть None при ошибке сервиса

    def test_fallback_response_without_ascii_art(self) -> None:
        """Тест fallback ответа без ASCII-арта."""
        self.mock_translation_service.is_language_supported.side_effect = (
            Exception("Service error")
        )

        request = WelcomeRequest(language="en", show_ascii_art=False)
        response = self.use_case.execute(request)

        assert response.title == "D&D Text MUD"
        assert response.ascii_art is None

    @pytest.mark.timeout(5)
    def test_execute_performance_timeout(self) -> None:
        """Тест производительности с таймаутом."""
        self.mock_translation_service.is_language_supported.return_value = True
        self.mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: default
        )

        request = WelcomeRequest(language="ru", show_ascii_art=False)
        response = self.use_case.execute(request)

        assert response is not None
