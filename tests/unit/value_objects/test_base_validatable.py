"""Юнит-тесты для Value Objects.

Следует Clean Architecture - тестируем объекты-значения
без внешних зависимостей.
"""

import pytest

from src.constants import (
    MAX_ASCII_ART_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_SUBTITLE_LENGTH,
    MAX_TITLE_LENGTH,
)
from src.value_objects.base_validatable import (
    ASCII_ART_VALIDATION,
    DESCRIPTION_VALIDATION,
    SUBTITLE_VALIDATION,
    TITLE_VALIDATION,
    BaseValidatable,
)


class TestBaseValidatable:
    """Тесты для BaseValidatable."""

    def test_validate_string_valid_required(self):
        """Тест валидации валидной обязательной строки."""
        result = BaseValidatable.validate_string(
            "Test Title", TITLE_VALIDATION, required=True
        )

        assert result == "Test Title"

    def test_validate_string_valid_optional(self):
        """Тест валидации валидной необязательной строки."""
        result = BaseValidatable.validate_string(
            "Optional Content", DESCRIPTION_VALIDATION, required=False
        )

        assert result == "Optional Content"

    def test_validate_string_with_whitespace(self):
        """Тест валидации строки с пробелами по краям."""
        result = BaseValidatable.validate_string(
            "  Padded Title  ", TITLE_VALIDATION, required=True
        )

        assert result == "Padded Title"

    def test_validate_string_not_string_type(self):
        """Тест валидации с неверным типом данных."""
        with pytest.raises(ValueError, match="Заголовок должен быть строкой"):
            BaseValidatable.validate_string(123, TITLE_VALIDATION)

        with pytest.raises(ValueError, match="Описание должен быть строкой"):
            BaseValidatable.validate_string(None, DESCRIPTION_VALIDATION)

        with pytest.raises(
            ValueError, match="Подзаголовок должен быть строкой"
        ):
            BaseValidatable.validate_string(["list"], SUBTITLE_VALIDATION)

    def test_validate_string_empty_required(self):
        """Тест валидации пустой обязательной строки."""
        with pytest.raises(ValueError, match="Заголовок не может быть пустым"):
            BaseValidatable.validate_string(
                "", TITLE_VALIDATION, required=True
            )

        with pytest.raises(ValueError, match="Заголовок не может быть пустым"):
            BaseValidatable.validate_string(
                "   ", TITLE_VALIDATION, required=True
            )

        with pytest.raises(ValueError, match="Описание не может быть пустым"):
            BaseValidatable.validate_string(
                "", DESCRIPTION_VALIDATION, required=True
            )

    def test_validate_string_empty_optional(self):
        """Тест валидации пустой необязательной строки."""
        result = BaseValidatable.validate_string(
            "", ASCII_ART_VALIDATION, required=False
        )

        assert result == ""

        result = BaseValidatable.validate_string(
            "   ", ASCII_ART_VALIDATION, required=False
        )

        assert result == ""

    def test_validate_string_too_long(self):
        """Тест валидации слишком длинной строки."""
        long_title = "x" * (MAX_TITLE_LENGTH + 1)
        with pytest.raises(
            ValueError,
            match=f"Заголовок слишком длинный \\(максимум {MAX_TITLE_LENGTH} символов\\)",
        ):
            BaseValidatable.validate_string(long_title, TITLE_VALIDATION)

        long_description = "x" * (MAX_DESCRIPTION_LENGTH + 1)
        with pytest.raises(
            ValueError,
            match=f"Описание слишком длинный \\(максимум {MAX_DESCRIPTION_LENGTH} символов\\)",
        ):
            BaseValidatable.validate_string(
                long_description, DESCRIPTION_VALIDATION
            )

        long_subtitle = "x" * (MAX_SUBTITLE_LENGTH + 1)
        with pytest.raises(
            ValueError,
            match=f"Подзаголовок слишком длинный \\(максимум {MAX_SUBTITLE_LENGTH} символов\\)",
        ):
            BaseValidatable.validate_string(long_subtitle, SUBTITLE_VALIDATION)

        long_ascii = "x" * (MAX_ASCII_ART_LENGTH + 1)
        with pytest.raises(
            ValueError,
            match=f"ASCII-арт слишком длинный \\(максимум {MAX_ASCII_ART_LENGTH} символов\\)",
        ):
            BaseValidatable.validate_string(long_ascii, ASCII_ART_VALIDATION)

    def test_validate_string_max_length_boundary(self):
        """Тест валидации на границе максимальной длины."""
        # Точные максимальные длины должны проходить
        exact_title = "x" * MAX_TITLE_LENGTH
        result = BaseValidatable.validate_string(exact_title, TITLE_VALIDATION)
        assert result == exact_title

        exact_description = "x" * MAX_DESCRIPTION_LENGTH
        result = BaseValidatable.validate_string(
            exact_description, DESCRIPTION_VALIDATION
        )
        assert result == exact_description

        exact_subtitle = "x" * MAX_SUBTITLE_LENGTH
        result = BaseValidatable.validate_string(
            exact_subtitle, SUBTITLE_VALIDATION
        )
        assert result == exact_subtitle

        exact_ascii = "x" * MAX_ASCII_ART_LENGTH
        result = BaseValidatable.validate_string(
            exact_ascii, ASCII_ART_VALIDATION, required=False
        )
        assert result == exact_ascii

    def test_validate_string_without_max_length(self):
        """Тест валидации без ограничения максимальной длины."""
        config_without_max = {"name": "Тестовое поле"}
        long_string = "x" * 1000

        result = BaseValidatable.validate_string(
            long_string, config_without_max
        )
        assert result == long_string

    def test_validate_title(self):
        """Тест валидации заголовка."""
        # Валидный заголовок
        result = BaseValidatable.validate_title("Valid Title")
        assert result == "Valid Title"

        # С пробелами
        result = BaseValidatable.validate_title("  Spaced Title  ")
        assert result == "Spaced Title"

        # Пустой заголовок
        with pytest.raises(ValueError, match="Заголовок не может быть пустым"):
            BaseValidatable.validate_title("")

        # Слишком длинный
        with pytest.raises(ValueError, match="Заголовок слишком длинный"):
            BaseValidatable.validate_title("x" * (MAX_TITLE_LENGTH + 1))

        # Неверный тип
        with pytest.raises(ValueError, match="Заголовок должен быть строкой"):
            BaseValidatable.validate_title(123)

    def test_validate_subtitle(self):
        """Тест валидации подзаголовка."""
        # Валидный подзаголовок
        result = BaseValidatable.validate_subtitle("Valid Subtitle")
        assert result == "Valid Subtitle"

        # Пустой подзаголовок
        with pytest.raises(
            ValueError, match="Подзаголовок не может быть пустым"
        ):
            BaseValidatable.validate_subtitle("")

        # Слишком длинный
        with pytest.raises(ValueError, match="Подзаголовок слишком длинный"):
            BaseValidatable.validate_subtitle("x" * (MAX_SUBTITLE_LENGTH + 1))

    def test_validate_description(self):
        """Тест валидации описания."""
        # Валидное описание
        result = BaseValidatable.validate_description("Valid Description")
        assert result == "Valid Description"

        # Пустое описание
        with pytest.raises(ValueError, match="Описание не может быть пустым"):
            BaseValidatable.validate_description("")

        # Слишком длинное
        with pytest.raises(
            ValueError,
            match=r"Описание слишком длинный \(максимум 500 символов\)",
        ):
            BaseValidatable.validate_description(
                "x" * (MAX_DESCRIPTION_LENGTH + 1)
            )

    def test_validate_ascii_art(self):
        """Тест валидации ASCII-арта."""
        # Валидный ASCII-арт
        art = """
    /\\_/\\
   ( o.o )
    > ^ <
        """.strip()

        result = BaseValidatable.validate_ascii_art(art)
        assert result == art

        # Пустой ASCII-арт (допустимо)
        result = BaseValidatable.validate_ascii_art("")
        assert result == ""

        result = BaseValidatable.validate_ascii_art("   ")
        assert result == ""

        # Слишком длинный ASCII-арт
        with pytest.raises(ValueError, match="ASCII-арт слишком длинный"):
            BaseValidatable.validate_ascii_art(
                "x" * (MAX_ASCII_ART_LENGTH + 1)
            )

    def test_validation_constants(self):
        """Тест констант валидации."""
        assert TITLE_VALIDATION["max_length"] == MAX_TITLE_LENGTH
        assert TITLE_VALIDATION["name"] == "Заголовок"

        assert SUBTITLE_VALIDATION["max_length"] == MAX_SUBTITLE_LENGTH
        assert SUBTITLE_VALIDATION["name"] == "Подзаголовок"

        assert DESCRIPTION_VALIDATION["max_length"] == MAX_DESCRIPTION_LENGTH
        assert DESCRIPTION_VALIDATION["name"] == "Описание"

        assert ASCII_ART_VALIDATION["max_length"] == MAX_ASCII_ART_LENGTH
        assert ASCII_ART_VALIDATION["name"] == "ASCII-арт"

    def test_validate_string_unicode_characters(self):
        """Тест валидации с Unicode символами."""
        unicode_string = "Тест на русском 🐍 日本語"
        result = BaseValidatable.validate_string(
            unicode_string, TITLE_VALIDATION
        )
        assert result == unicode_string

        # Unicode символы считаются как 1 символ
        unicode_with_emoji = "Test 🎮 Title"
        result = BaseValidatable.validate_string(
            unicode_with_emoji, TITLE_VALIDATION
        )
        assert result == unicode_with_emoji

    def test_validate_string_special_characters(self):
        """Тест валидации со специальными символами."""
        special_chars = "Title with @#$%^&*()[]{}|\\:;\"'<>?,./"
        result = BaseValidatable.validate_string(
            special_chars, TITLE_VALIDATION
        )
        assert result == special_chars

        # Новые строки и табы
        multiline = "Title\nwith\ttabs\nand newlines"
        result = BaseValidatable.validate_string(
            multiline, DESCRIPTION_VALIDATION
        )
        assert result == multiline

    def test_validate_string_newlines_and_tabs(self):
        """Тест обработки новых строк и табов."""
        # Пробелы по краям удаляются, но внутренние сохраняются
        string_with_internal_whitespace = (
            "  Title\nwith\tinternal  \nwhitespace  "
        )
        result = BaseValidatable.validate_string(
            string_with_internal_whitespace, DESCRIPTION_VALIDATION
        )

        # Внешние пробелы удалены, внутренние сохранены
        assert result == "Title\nwith\tinternal  \nwhitespace"

    def test_error_messages_accuracy(self):
        """Тест точности сообщений об ошибках."""
        try:
            BaseValidatable.validate_string(123, TITLE_VALIDATION)
        except ValueError as e:
            assert str(e) == "Заголовок должен быть строкой"

        try:
            BaseValidatable.validate_string("", TITLE_VALIDATION)
        except ValueError as e:
            assert str(e) == "Заголовок не может быть пустым"

        try:
            BaseValidatable.validate_string(
                "x" * (MAX_TITLE_LENGTH + 1), TITLE_VALIDATION
            )
        except ValueError as e:
            expected = f"Заголовок слишком длинный (максимум {MAX_TITLE_LENGTH} символов)"
            assert str(e) == expected

    def test_method_chaining_compatibility(self):
        """Тест совместимости с цепочками вызовов."""
        # Все методы возвращают строку, что позволяет использовать их в цепочках
        title = BaseValidatable.validate_title("  Test Title  ")
        assert isinstance(title, str)

        subtitle = BaseValidatable.validate_subtitle("  Test Subtitle  ")
        assert isinstance(subtitle, str)

        description = BaseValidatable.validate_description(
            "  Test Description  "
        )
        assert isinstance(description, str)

        ascii_art = BaseValidatable.validate_ascii_art("  Test Art  ")
        assert isinstance(ascii_art, str)

    def test_performance_with_long_strings(self):
        """Тест производительности с длинными строками."""
        import time

        # Очень длинная строка (но в пределах лимита)
        very_long = "x" * 499  # В пределах лимита в 500 символов

        start_time = time.time()
        result = BaseValidatable.validate_string(
            very_long, DESCRIPTION_VALIDATION
        )
        end_time = time.time()

        assert result == very_long
        # Операция должна быть быстрой (менее 1ms)
        assert (end_time - start_time) < 0.001
