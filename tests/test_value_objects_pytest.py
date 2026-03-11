"""Pytest тесты для Value Objects.

Следует KISS - просто и понятно.
"""

import pytest

from src.value_objects.ascii_art import AsciiArt
from src.value_objects.language import Language
from src.value_objects.welcome_content import WelcomeContent


class TestAsciiArt:
    """Тесты для AsciiArt."""

    def test_create_valid_ascii_art(self) -> None:
        """Тест создания валидного ASCII-арта."""
        art = AsciiArt(value="Test ASCII Art")
        assert art.value == "Test ASCII Art"
        assert not art.is_empty()

    def test_create_empty_ascii_art(self) -> None:
        """Тест создания пустого ASCII-арта."""
        art = AsciiArt(value="")
        assert art.is_empty()
        assert art.value == ""

    def test_create_too_long_ascii_art(self) -> None:
        """Тест создания слишком длинного ASCII-арта."""
        long_art = "x" * 2001
        with pytest.raises(ValueError, match="ASCII-арт слишком длинный"):
            AsciiArt(value=long_art)

    def test_create_dnd_logo(self) -> None:
        """Тест создания логотипа D&D."""
        logo = AsciiArt.create_dnd_logo()
        assert isinstance(logo, AsciiArt)
        assert not logo.is_empty()

    def test_equality(self) -> None:
        """Тест равенства по значению."""
        art1 = AsciiArt(value="Test")
        art2 = AsciiArt(value="Test")
        assert art1 == art2

    def test_inequality(self) -> None:
        """Тест неравенства по значению."""
        art1 = AsciiArt(value="Test1")
        art2 = AsciiArt(value="Test2")
        assert art1 != art2


class TestLanguage:
    """Тесты для Language."""

    def test_create_valid_language(self) -> None:
        """Тест создания валидного языка."""
        lang = Language.from_string("ru")
        assert lang.get_code() == "ru"
        assert str(lang) == "ru"

    def test_create_english_language(self) -> None:
        """Тест создания английского языка."""
        lang = Language.from_string("en")
        assert lang.get_code() == "en"
        assert str(lang) == "en"

    def test_create_invalid_language(self) -> None:
        """Тест создания невалидного языка."""
        with pytest.raises(ValueError, match="Язык 'de' не поддерживается"):
            Language.from_string("de")

    def test_create_empty_language(self) -> None:
        """Тест создания пустого языка."""
        with pytest.raises(ValueError, match="Код языка не может быть пустым"):
            Language.from_string("")

    def test_case_insensitive(self) -> None:
        """Тест нечувствительности к регистру."""
        lang1 = Language.from_string("RU")
        lang2 = Language.from_string("ru")
        assert lang1 == lang2
        assert lang1.get_code() == "ru"

    def test_create_default(self) -> None:
        """Тест создания языка по умолчанию."""
        lang = Language.create_default()
        assert lang.get_code() == "ru"
        assert str(lang) == "ru"


class TestWelcomeContent:
    """Тесты для Value Object WelcomeContent."""

    def test_create_valid_content(self) -> None:
        """Тест создания валидного контента."""
        content = WelcomeContent(
            title="Test Title",
            subtitle="Test Subtitle",
            description="Test Description"
        )
        assert content.get_title() == "Test Title"
        assert content.get_subtitle() == "Test Subtitle"
        assert content.get_description() == "Test Description"

    def test_create_empty_title(self) -> None:
        """Тест создания с пустым заголовком."""
        with pytest.raises(ValueError, match="Заголовок не может быть пустым"):
            WelcomeContent(
                title="",
                subtitle="Test Subtitle",
                description="Test Description"
            )

    def test_create_too_long_title(self) -> None:
        """Тест создания слишком длинного заголовка."""
        with pytest.raises(ValueError, match="Заголовок слишком длинный"):
            WelcomeContent(
                title="x" * 101,
                subtitle="Test Subtitle",
                description="Test Description"
            )

    def test_create_empty_subtitle(self) -> None:
        """Тест создания с пустым подзаголовком."""
        with pytest.raises(ValueError, match="Подзаголовок не может быть пустым"):
            WelcomeContent(
                title="Test Title",
                subtitle="",
                description="Test Description"
            )

    def test_create_empty_description(self) -> None:
        """Тест создания с пустым описанием."""
        with pytest.raises(ValueError, match="Описание не может быть пустым"):
            WelcomeContent(
                title="Test Title",
                subtitle="Test Subtitle",
                description=""
            )

    def test_whitespace_trimming(self) -> None:
        """Тест обрезки пробелов."""
        content = WelcomeContent(
            title="  Test Title  ",
            subtitle=" Test Subtitle ",
            description=" Test Description "
        )
        assert content.get_title() == "Test Title"
        assert content.get_subtitle() == "Test Subtitle"
        assert content.get_description() == "Test Description"

    def test_equality(self) -> None:
        """Тест равенства по значению."""
        content1 = WelcomeContent(
            title="Test",
            subtitle="Sub",
            description="Desc"
        )
        content2 = WelcomeContent(
            title="Test",
            subtitle="Sub",
            description="Desc"
        )
        assert content1 == content2
