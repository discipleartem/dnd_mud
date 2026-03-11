"""Unit тесты для адаптеров.

Следует Clean Architecture - тестируем адаптеры в изоляции.
"""

import pytest
from unittest.mock import Mock, patch

from src.adapters.translation_service_adapter import TranslationServiceAdapter
from src.adapters.welcome_screen_factory_adapter import (
    WelcomeScreenFactoryAdapter,
)
from src.dto.welcome_dto import WelcomeScreenRequest


class TestTranslationServiceAdapter:
    """Тесты для TranslationServiceAdapter."""

    @pytest.mark.timeout(5)
    def test_get_translation_delegates_to_loader(self) -> None:
        """Тест делегирования в TranslationLoader."""
        with patch(
            "src.adapters.translation_service_adapter.TranslationLoader"
        ) as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            mock_loader.get_translation.return_value = "Переведенный текст"

            adapter = TranslationServiceAdapter()

            result = adapter.get_translation(
                "ru", "welcome.title", "Добро пожаловать"
            )

            assert result == "Переведенный текст"
            mock_loader.get_translation.assert_called_once_with(
                "ru", "welcome.title", "Добро пожаловать"
            )

    @pytest.mark.timeout(5)
    def test_is_language_supported_delegates_to_loader(self) -> None:
        """Тест делегирования проверки языка."""
        with patch(
            "src.adapters.translation_service_adapter.TranslationLoader"
        ) as mock_loader_class:
            mock_loader = Mock()
            mock_loader_class.return_value = mock_loader
            mock_loader.is_language_supported.return_value = True

            adapter = TranslationServiceAdapter()

            result = adapter.is_language_supported("ru")

            assert result is True
            mock_loader.is_language_supported.assert_called_once_with("ru")


class TestWelcomeScreenFactoryAdapter:
    """Тесты для WelcomeScreenFactoryAdapter."""

    @patch(
        "src.adapters.welcome_screen_factory_adapter.TranslationServiceAdapter"
    )
    @pytest.mark.timeout(5)
    def test_create_screen_with_ascii_art(
        self, mock_translation_service_class
    ) -> None:
        """Тест создания экрана с ASCII-артом."""
        mock_translation_service = Mock()
        mock_translation_service_class.return_value = mock_translation_service

        # Настраиваем моки для переводов
        mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: {
                (
                    "ru",
                    "welcome.title",
                    "Default Title",
                ): "Добро пожаловать в D&D MUD",
                (
                    "ru",
                    "welcome.subtitle",
                    "Default Subtitle",
                ): "Текстовая MUD игра",
                (
                    "ru",
                    "welcome.description",
                    "Default Description",
                ): "Описание игры",
                (
                    "ru",
                    "welcome.press_enter",
                    "Default Press",
                ): "Нажмите Enter для продолжения...",
                ("en", "welcome.title", "Default Title"): "Welcome to D&D MUD",
                (
                    "en",
                    "welcome.subtitle",
                    "Default Subtitle",
                ): "Text MUD game",
                (
                    "en",
                    "welcome.description",
                    "Default Description",
                ): "Game description",
                (
                    "en",
                    "welcome.press_enter",
                    "Default Press",
                ): "Press Enter to continue...",
            }.get((lang, key, default), default)
        )

        factory = WelcomeScreenFactoryAdapter()

        request = WelcomeScreenRequest(language="ru", show_ascii_art=True)

        screen = factory.create_screen(request)

        assert screen.content.get_title() is not None
        assert screen.content.get_subtitle() is not None
        assert screen.content.get_description() is not None
        assert screen.ascii_art is not None
        assert screen.language.get_code() == "ru"
        assert screen.press_enter_text is not None
        assert screen.has_ascii_art() is True

    @patch(
        "src.adapters.welcome_screen_factory_adapter.TranslationServiceAdapter"
    )
    @pytest.mark.timeout(5)
    def test_create_screen_without_ascii_art(
        self, mock_translation_service_class
    ) -> None:
        """Тест создания экрана без ASCII-арта."""
        mock_translation_service = Mock()
        mock_translation_service_class.return_value = mock_translation_service

        mock_translation_service.get_translation.side_effect = (
            lambda lang, key, default: {
                ("en", "welcome.title", "Default Title"): "Welcome to D&D MUD",
                (
                    "en",
                    "welcome.subtitle",
                    "Default Subtitle",
                ): "Text MUD game",
                (
                    "en",
                    "welcome.description",
                    "Default Description",
                ): "Game description",
                (
                    "en",
                    "welcome.press_enter",
                    "Default Press",
                ): "Press Enter to continue...",
            }.get((lang, key, default), default)
        )

        factory = WelcomeScreenFactoryAdapter()

        request = WelcomeScreenRequest(language="en", show_ascii_art=False)

        screen = factory.create_screen(request)

        assert screen.ascii_art is None
        assert screen.has_ascii_art() is False
        assert screen.language.get_code() == "en"

    @patch(
        "src.adapters.welcome_screen_factory_adapter.TranslationServiceAdapter"
    )
    @pytest.mark.timeout(5)
    def test_get_supported_languages(
        self, mock_translation_service_class
    ) -> None:
        """Тест получения поддерживаемых языков."""
        mock_translation_service = Mock()
        mock_translation_service_class.return_value = mock_translation_service
        mock_translation_service.get_supported_languages.return_value = [
            "ru",
            "en",
        ]

        factory = WelcomeScreenFactoryAdapter()

        languages = factory.get_supported_languages()

        assert languages == ["ru", "en"]
        mock_translation_service.get_supported_languages.assert_called_once()
