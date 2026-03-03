"""Unit тесты для NameValidator."""

from src.validators.name_validator import NameValidator, ValidationResult


class TestNameValidator:
    """Тесты валидатора имени персонажа."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.validator = NameValidator()

    def test_valid_names(self):
        """Тест валидных имен."""
        valid_names = [
            "Арагорн",
            "Gandalf",
            "Фродо",
            "Legolas",
            "Гэндальф-Серый",
            "Арторниус",
            "Zorro",
            "Иван-Царевич",
            "Robin-Hood",
        ]

        for name in valid_names:
            result = self.validator.validate(name)
            assert result.is_valid, f"Имя '{name}' должно быть валидным"
            assert result.error_message is None

    def test_empty_name(self):
        """Тест пустого имени."""
        result = self.validator.validate("")
        assert not result.is_valid
        assert "Имя не может быть пустым" in result.error_message

        result = self.validator.validate("   ")
        assert not result.is_valid
        assert "Имя не может быть пустым" in result.error_message

    def test_name_too_short(self):
        """Тест слишком короткого имени."""
        result = self.validator.validate("А")
        assert not result.is_valid
        assert "минимум 3 символа" in result.error_message

        result = self.validator.validate("Аб")
        assert not result.is_valid
        assert "минимум 3 символа" in result.error_message

    def test_name_too_long(self):
        """Тест слишком длинного имени."""
        long_name = "А" * 17  # 17 символов
        result = self.validator.validate(long_name)
        assert not result.is_valid
        assert "максимум 16 символов" in result.error_message

    def test_name_with_digits(self):
        """Тест имени с цифрами."""
        names_with_digits = ["Арагорн2", "Gandalf123", "Фродо0", "Legolas99"]

        for name in names_with_digits:
            result = self.validator.validate(name)
            assert not result.is_valid
            assert "Цифры и спецсимволы запрещены" in result.error_message

    def test_name_with_special_chars(self):
        """Тест имени со спецсимволами."""
        names_with_special_chars = [
            "Арагорн!",
            "Gandalf@",
            "Фродо#",
            "Legolas$",
            "Артор%ниус",
            "Zorro&",
            "Иван*Царевич",
        ]

        for name in names_with_special_chars:
            result = self.validator.validate(name)
            assert not result.is_valid
            assert "Цифры и спецсимволы запрещены" in result.error_message

    def test_name_with_spaces(self):
        """Тест имени с пробелами."""
        names_with_spaces = [
            "Арагорн Сын",
            "Gandalf the Grey",
            "Фродо Бэггинс",
            "Robin Hood",
        ]

        for name in names_with_spaces:
            result = self.validator.validate(name)
            assert not result.is_valid
            assert "Цифры и спецсимволы запрещены" in result.error_message

    def test_name_starting_with_hyphen(self):
        """Тест имени, начинающегося с дефиса."""
        result = self.validator.validate("-Арагорн")
        assert not result.is_valid
        assert (
            "не может начинаться или заканчиваться дефисом"
            in result.error_message
        )

    def test_name_ending_with_hyphen(self):
        """Тест имени, заканчивающегося дефисом."""
        result = self.validator.validate("Арагорн-")
        assert not result.is_valid
        assert (
            "не может начинаться или заканчиваться дефисом"
            in result.error_message
        )

    def test_name_with_double_hyphen(self):
        """Тест имени с двойным дефисом."""
        result = self.validator.validate("Арагорн--Сын")
        assert not result.is_valid
        assert "не может содержать двойные дефисы" in result.error_message

    def test_name_with_valid_hyphens(self):
        """Тест имени с корректными дефисами."""
        valid_names_with_hyphens = [
            "Арагорн-Сын",
            "Gandalf-the-Grey",
            "Фродо-Бэггинс",
            "Robin-Hood",
            "Иван-Царевич",
        ]

        for name in valid_names_with_hyphens:
            result = self.validator.validate(name)
            assert (
                result.is_valid
            ), f"Имя '{name}' с дефисами должно быть валидным"

    def test_name_with_mixed_case(self):
        """Тест имени в разном регистре."""
        mixed_case_names = ["аРАГОРН", "gANDALF", "фРОДО", "lEGOLAS"]

        for name in mixed_case_names:
            result = self.validator.validate(name)
            assert (
                result.is_valid
            ), f"Имя '{name}' в любом регистре должно быть валидным"

    def test_name_with_whitespace_trimming(self):
        """Тест имени с пробелами по краям."""
        names_with_whitespace = [
            "  Арагорн  ",
            "\tGandalf\t",
            "\nФродо\n",
            "  Legolas  ",
        ]

        for name in names_with_whitespace:
            result = self.validator.validate(name)
            assert (
                result.is_valid
            ), f"Имя '{repr(name)}' с пробелами по краям должно быть валидным"

    def test_is_valid_method(self):
        """Тест метода is_valid (только True/False)."""
        assert self.validator.is_valid("Арагорн") is True
        assert self.validator.is_valid("") is False
        assert self.validator.is_valid("А") is False
        assert self.validator.is_valid("Арагорн2") is False

    def test_validation_result_classes(self):
        """Тест классов-конструкторов ValidationResult."""
        success = ValidationResult.success()
        assert success.is_valid is True
        assert success.error_message is None

        failure = ValidationResult.failure("Test error")
        assert failure.is_valid is False
        assert failure.error_message == "Test error"

    def test_edge_cases(self):
        """Тест граничных случаев."""
        # Минимальная длина
        result = self.validator.validate("Абв")
        assert result.is_valid

        # Максимальная длина
        max_length_name = "А" * 16
        result = self.validator.validate(max_length_name)
        assert result.is_valid

        # Только латиница
        result = self.validator.validate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        assert not result.is_valid  # Слишком длинное

        result = self.validator.validate("ABC")
        assert result.is_valid
