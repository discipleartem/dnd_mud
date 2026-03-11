"""Unit тесты для WelcomeScreen Entity.

Следует Clean Architecture - тестируем сущность в полной изоляции.
Entity не должен иметь внешних зависимостей.
"""

import pytest

from src.entities.welcome_screen import WelcomeScreen


class TestWelcomeScreen:
    """Тесты для WelcomeScreen Entity."""

    def test_create_welcome_screen_with_all_fields(self) -> None:
        """Тест создания сущности со всеми полями."""
        screen = WelcomeScreen(
            title="Добро пожаловать",
            subtitle="Текстовая MUD игра",
            description="Создайте персонажа",
            ascii_art="ASCII LOGO",
            language="ru",
            press_enter_text="Нажмите Enter"
        )

        assert screen.title == "Добро пожаловать"
        assert screen.subtitle == "Текстовая MUD игра"
        assert screen.description == "Создайте персонажа"
        assert screen.ascii_art == "ASCII LOGO"
        assert screen.language == "ru"
        assert screen.press_enter_text == "Нажмите Enter"

    def test_create_welcome_screen_with_defaults(self) -> None:
        """Тест создания сущности с параметрами по умолчанию."""
        screen = WelcomeScreen(
            title="Welcome",
            subtitle="Game",
            description="Description"
        )

        assert screen.title == "Welcome"
        assert screen.subtitle == "Game"
        assert screen.description == "Description"
        assert screen.ascii_art is None
        assert screen.language == "ru"
        assert screen.press_enter_text == "Нажмите Enter для продолжения..."

    def test_has_ascii_art_with_content(self) -> None:
        """Тест проверки наличия ASCII-арта с контентом."""
        screen = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art="Some ASCII art"
        )

        assert screen.has_ascii_art() is True

    def test_has_ascii_art_with_empty_string(self) -> None:
        """Тест проверки наличия ASCII-арта с пустой строкой."""
        screen = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art=""
        )

        assert screen.has_ascii_art() is False

    def test_has_ascii_art_with_whitespace_only(self) -> None:
        """Тест проверки наличия ASCII-арта с пробелами."""
        screen = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art="   \n\t  "
        )

        assert screen.has_ascii_art() is False

    def test_has_ascii_art_with_none(self) -> None:
        """Тест проверки наличия ASCII-арта с None."""
        screen = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art=None
        )

        assert screen.has_ascii_art() is False

    def test_str_representation_with_ascii(self) -> None:
        """Тест строкового представления с ASCII-артом."""
        screen = WelcomeScreen(
            title="D&D MUD",
            subtitle="Game",
            description="Description",
            ascii_art="Logo",
            language="en"
        )

        str_repr = str(screen)
        assert "D&D MUD" in str_repr
        assert "en" in str_repr
        assert "has_ascii=True" in str_repr

    def test_str_representation_without_ascii(self) -> None:
        """Тест строкового представления без ASCII-арта."""
        screen = WelcomeScreen(
            title="D&D MUD",
            subtitle="Game", 
            description="Description",
            language="ru"
        )

        str_repr = str(screen)
        assert "D&D MUD" in str_repr
        assert "ru" in str_repr
        assert "has_ascii=False" in str_repr

    def test_immutability_of_fields(self) -> None:
        """Тест что поля dataclass доступны для изменения (dataclass не immutable)."""
        screen = WelcomeScreen(
            title="Original",
            subtitle="Original",
            description="Original"
        )

        # dataclass по умолчанию mutable
        screen.title = "Modified"
        assert screen.title == "Modified"

    def test_equality_of_same_screens(self) -> None:
        """Тест равенства одинаковых сущностей."""
        screen1 = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art="ASCII",
            language="ru",
            press_enter_text="Press"
        )
        
        screen2 = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art="ASCII",
            language="ru",
            press_enter_text="Press"
        )

        assert screen1 == screen2

    def test_difference_in_title(self) -> None:
        """Тест различия в заголовке."""
        screen1 = WelcomeScreen(
            title="Title1",
            subtitle="Subtitle",
            description="Description"
        )
        
        screen2 = WelcomeScreen(
            title="Title2",
            subtitle="Subtitle",
            description="Description"
        )

        assert screen1 != screen2

    def test_difference_in_ascii_art(self) -> None:
        """Тест различия в ASCII-арте."""
        screen1 = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art="ASCII1"
        )
        
        screen2 = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art="ASCII2"
        )

        assert screen1 != screen2

    def test_difference_in_none_vs_empty_ascii(self) -> None:
        """Тест различия между None и пустой строкой в ASCII."""
        screen1 = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art=None
        )
        
        screen2 = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art=""
        )

        assert screen1 != screen2
        assert screen1.has_ascii_art() is False
        assert screen2.has_ascii_art() is False

    @pytest.mark.timeout(5)
    def test_performance_has_ascii_art(self) -> None:
        """Тест производительности метода has_ascii_art."""
        screen = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            ascii_art="A" * 10000  # Большой ASCII-арт
        )

        # Метод должен работать быстро даже с большими данными
        result = screen.has_ascii_art()
        assert result is True

    @pytest.mark.timeout(5)
    def test_performance_str_representation(self) -> None:
        """Тест производительности строкового представления."""
        screen = WelcomeScreen(
            title="A" * 1000,
            subtitle="B" * 1000,
            description="C" * 1000,
            ascii_art="D" * 1000,
            language="test"
        )

        str_repr = str(screen)
        assert len(str_repr) > 0
        assert "A" * 1000 in str_repr

    def test_entity_contains_only_business_data(self) -> None:
        """Тест что сущность содержит только бизнес-данные без логики."""
        screen = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description"
        )

        # Проверяем что у сущности есть только данные и простые методы
        assert hasattr(screen, 'title')
        assert hasattr(screen, 'subtitle')
        assert hasattr(screen, 'description')
        assert hasattr(screen, 'has_ascii_art')
        assert hasattr(screen, '__str__')
        
        # Нет внешних зависимостей, нет сложной бизнес-логики
        assert callable(screen.has_ascii_art)
        assert callable(screen.__str__)

    def test_language_code_validation_not_in_entity(self) -> None:
        """Тест что валидация языкового кода не входит в Entity."""
        # Entity не должна валидировать бизнес-правила
        # Это задача Use Case
        screen = WelcomeScreen(
            title="Title",
            subtitle="Subtitle",
            description="Description",
            language="invalid_language_code"
        )

        # Entity просто хранит данные
        assert screen.language == "invalid_language_code"
