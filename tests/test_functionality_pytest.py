"""Pytest тесты для основного функционала.

Проверяет корректность работы сервисов, use cases и адаптеров.
"""


from src.console.welcome_adapter import WelcomeScreenAdapter
from src.services.welcome_service import WelcomeService
from src.value_objects.ascii_art import AsciiArt
from src.value_objects.language import Language
from src.value_objects.welcome_content import WelcomeContent
from src.welcome_dto import WelcomeScreenRequest, WelcomeScreenResponse
from src.welcome_screen import WelcomeScreen
from src.welcome_use_case import ShowWelcomeScreenUseCase


class TestWelcomeService:
    """Тесты для WelcomeService."""

    def test_create_welcome_screen_default(self) -> None:
        """Тест создания экрана по умолчанию."""
        service = WelcomeService()
        screen = service.create_welcome_screen()

        assert screen is not None
        assert screen.language.get_code() == "ru"
        assert screen.has_ascii_art() is True
        assert screen.content.get_title() == "D&D Text MUD"

    def test_create_welcome_screen_english(self) -> None:
        """Тест создания экрана на английском."""
        service = WelcomeService()
        screen = service.create_welcome_screen(language_code="en")

        assert screen.language.get_code() == "en"
        assert screen.has_ascii_art() is True

    def test_create_welcome_screen_no_ascii(self) -> None:
        """Тест создания экрана без ASCII-арта."""
        service = WelcomeService()
        screen = service.create_welcome_screen(show_ascii_art=False)

        assert screen.has_ascii_art() is False
        assert screen.ascii_art is None

    def test_get_display_content(self) -> None:
        """Тест получения контента для отображения."""
        service = WelcomeService()
        screen = service.create_welcome_screen()
        display_data = service.get_display_content(screen)

        assert isinstance(display_data, dict)
        assert "title" in display_data
        assert display_data["language"] == "ru"


class TestWelcomeUseCase:
    """Тесты для ShowWelcomeScreenUseCase."""

    def test_execute_default_request(self) -> None:
        """Тест выполнения с запросом по умолчанию."""
        use_case = ShowWelcomeScreenUseCase()
        request = WelcomeScreenRequest()
        response = use_case.execute(request)

        assert isinstance(response, WelcomeScreenResponse)
        assert response.language == "ru"
        assert response.ascii_art is not None
        assert response.title == "D&D Text MUD"

    def test_execute_custom_request(self) -> None:
        """Тест выполнения с кастомным запросом."""
        use_case = ShowWelcomeScreenUseCase()
        request = WelcomeScreenRequest(language="en", show_ascii_art=False)
        response = use_case.execute(request)

        assert response.language == "en"
        assert response.ascii_art is None


class TestWelcomeScreenAdapter:
    """Тесты для WelcomeScreenAdapter."""

    def test_adapter_initialization(self) -> None:
        """Тест инициализации адаптера."""
        adapter = WelcomeScreenAdapter()
        assert adapter is not None

    def test_adapter_has_required_methods(self) -> None:
        """Тест наличия требуемых методов."""
        adapter = WelcomeScreenAdapter()

        assert hasattr(adapter, 'display')
        assert hasattr(adapter, 'clear_screen')
        assert callable(adapter.display)
        assert callable(adapter.clear_screen)

    def test_clear_screen_method(self) -> None:
        """Тест метода очистки экрана."""
        adapter = WelcomeScreenAdapter()
        # Просто проверяем, что метод не вызывает исключений
        adapter.clear_screen()


class TestWelcomeScreen:
    """Тесты для WelcomeScreen."""

    def test_create_valid_screen(self) -> None:
        """Тест создания валидного экрана."""
        content = WelcomeContent(
            title="Test Title",
            subtitle="Test Subtitle",
            description="Test Description"
        )
        screen = WelcomeScreen(
            content=content,
            ascii_art=AsciiArt.create_dnd_logo(),
            language=Language.from_string("en"),
            press_enter_text="Press Enter"
        )

        assert screen.content.get_title() == "Test Title"
        assert screen.language.get_code() == "en"
        assert screen.has_ascii_art() is True

    def test_screen_without_ascii_art(self) -> None:
        """Тест экрана без ASCII-арта."""
        content = WelcomeContent(
            title="Test Title",
            subtitle="Test Subtitle",
            description="Test Description"
        )
        screen = WelcomeScreen(
            content=content,
            ascii_art=None,
            language=Language.from_string("en")
        )

        assert screen.has_ascii_art() is False

    def test_screen_str_representation(self) -> None:
        """Тест строкового представления экрана."""
        content = WelcomeContent(
            title="Test Title",
            subtitle="Test Subtitle",
            description="Test Description"
        )
        screen = WelcomeScreen(
            content=content,
            ascii_art=AsciiArt.create_dnd_logo(),
            language=Language.from_string("en")
        )

        screen_str = str(screen)
        assert "Test Title" in screen_str
        assert "en" in screen_str
        assert "has_ascii=True" in screen_str


class TestIntegration:
    """Интеграционные тесты."""

    def test_full_workflow(self) -> None:
        """Тест полного рабочего процесса."""
        # Создаем сервис
        service = WelcomeService()

        # Создаем экран
        screen = service.create_welcome_screen(language_code="ru", show_ascii_art=True)
        assert screen is not None

        # Получаем контент для отображения
        display_data = service.get_display_content(screen)
        assert isinstance(display_data, dict)

        # Создаем use case
        use_case = ShowWelcomeScreenUseCase()
        request = WelcomeScreenRequest(language="ru", show_ascii_art=True)
        response = use_case.execute(request)

        # Проверяем ответ
        assert response.language == "ru"
        assert response.ascii_art is not None
        assert response.title is not None

        # Создаем адаптер
        adapter = WelcomeScreenAdapter()
        assert adapter is not None

        # Проверяем, что адаптер может обработать ответ
        assert hasattr(adapter, 'display')
