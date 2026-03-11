"""Unit тесты для адаптеров.

Следует Clean Architecture - тестируем адаптеры в изоляции.
"""

from unittest.mock import Mock, patch

import pytest

from src.frameworks.console.welcome_adapter import ConsoleWelcomeScreenAdapter
from src.frameworks.services.translation_service_adapter import (
    TranslationServiceAdapter,
)


class TestTranslationServiceAdapter:
    """Тесты для TranslationServiceAdapter."""

    @pytest.mark.timeout(5)
    def test_get_translation_delegates_to_loader(self) -> None:
        """Тест делегирования загрузчику переводов."""
        mock_loader = Mock()
        mock_loader.get_translation.return_value = "Test translation"

        with patch(
            "src.frameworks.services.translation_service_adapter.TranslationLoader"
        ) as mock_loader_class:
            mock_loader_class.return_value = mock_loader

            adapter = TranslationServiceAdapter()

            result = adapter.get_translation("ru", "test.key", "Default")

            assert result == "Test translation"
            mock_loader.get_translation.assert_called_once_with(
                "ru", "test.key", "Default"
            )

    @pytest.mark.timeout(5)
    def test_is_language_supported_delegates_to_loader(self) -> None:
        """Тест делегирования проверки поддержки языка."""
        mock_loader = Mock()
        mock_loader.is_language_supported.return_value = True

        with patch(
            "src.frameworks.services.translation_service_adapter.TranslationLoader"
        ) as mock_loader_class:
            mock_loader_class.return_value = mock_loader

            adapter = TranslationServiceAdapter()

            result = adapter.is_language_supported("ru")

            assert result is True
            mock_loader.is_language_supported.assert_called_once_with("ru")


class TestConsoleWelcomeScreenAdapter:
    """Тесты для ConsoleWelcomeScreenAdapter."""

    @pytest.mark.timeout(5)
    def test_adapter_initialization(self) -> None:
        """Тест инициализации адаптера."""
        adapter = ConsoleWelcomeScreenAdapter()

        assert adapter is not None
        assert adapter._ui is not None
        assert adapter._main_menu_adapter is not None
        assert adapter._use_main_menu is False

    @pytest.mark.timeout(5)
    def test_adapter_with_colors(self) -> None:
        """Тест инициализации с цветами."""
        adapter = ConsoleWelcomeScreenAdapter(use_colors=False)

        assert adapter is not None
        assert adapter._use_main_menu is False

    @pytest.mark.timeout(5)
    def test_main_menu_toggle(self) -> None:
        """Тест переключения режима главного меню."""
        adapter = ConsoleWelcomeScreenAdapter()

        # По умолчанию выключено
        assert adapter.is_main_menu_enabled() is False

        # Включаем
        adapter.enable_main_menu()
        assert adapter.is_main_menu_enabled() is True

        # Выключаем
        adapter.disable_main_menu()
        assert adapter.is_main_menu_enabled() is False

    @pytest.mark.timeout(5)
    def test_clear_screen(self) -> None:
        """Тест очистки экрана."""
        adapter = ConsoleWelcomeScreenAdapter()

        # Просто проверяем что метод не вызывает ошибок
        adapter.clear_screen()

        # С включенным главным меню
        adapter.enable_main_menu()
        adapter.clear_screen()

    @pytest.mark.timeout(5)
    def test_display_message(self) -> None:
        """Тест отображения сообщения."""
        adapter = ConsoleWelcomeScreenAdapter()

        # Просто проверяем что метод не вызывает ошибок
        adapter.display_message("Test message", "info")
        adapter.display_message("Warning message", "warning")
        adapter.display_message("Error message", "error")
