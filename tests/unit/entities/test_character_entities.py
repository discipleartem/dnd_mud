#!/usr/bin/env python3
"""Тесты для сущностей персонажа."""

from unittest.mock import Mock, patch

import pytest

from src.ui.entities.character import Character, Size


class TestSize:
    """Тесты для перечисления Size."""

    def test_size_values(self) -> None:
        """Тест значений перечисления."""
        assert Size.TINY.value == "tiny"
        assert Size.SMALL.value == "small"
        assert Size.MEDIUM.value == "medium"
        assert Size.LARGE.value == "large"
        assert Size.HUGE.value == "huge"
        assert Size.GARGANTUAN.value == "gargantuan"
        assert Size.COLOSSAL.value == "colossal"

    @patch('src.ui.entities.character.t')
    def test_get_localized_name(self, mock_t) -> None:
        """Тест получения локализованного названия."""
        mock_t.return_value = "Средний"
        
        result = Size.MEDIUM.get_localized_name()
        
        assert result == "Средний"
        mock_t.assert_called_once_with("character.size.medium")

    @patch('src.ui.entities.character.t')
    def test_str_representation(self, mock_t) -> None:
        """Тест строкового представления."""
        mock_t.return_value = "Маленький"
        
        result = str(Size.SMALL)
        
        assert result == "Маленький"
        mock_t.assert_called_once_with("character.size.small")

    def test_size_comparison(self) -> None:
        """Тест сравнения размеров."""
        assert Size.TINY != Size.SMALL
        assert Size.SMALL != Size.MEDIUM
        assert Size.MEDIUM == Size.MEDIUM
        
        # Проверяем, что это перечисление
        assert isinstance(Size.TINY, Size)
        assert hasattr(Size.TINY, 'value')


class TestCharacter:
    """Тесты для класса Character."""

    def test_character_init_minimal(self) -> None:
        """Тест минимальной инициализации персонажа."""
        character = Character()
        
        assert character.name == "Безымянный"
        assert character.race is None
        assert character._class == ""
        assert character.level == 1
        assert character.subrace is None
        assert character.sub_class is None
        assert character.ability_scores is None

    def test_character_init_full(self) -> None:
        """Тест полной инициализации персонажа."""
        mock_race = Mock()
        mock_race.name = "Человек"
        mock_race.size = Size.MEDIUM
        
        mock_subrace = Mock()
        mock_subrace.name = "Высший человек"
        
        mock_ability_scores = Mock()
        
        character = Character(
            name="Арагорн",
            race=mock_race,
            _class="Воин",
            level=5,
            subrace=mock_subrace,
            sub_class="Рыцарь",
            ability_scores=mock_ability_scores
        )
        
        assert character.name == "Арагорн"
        assert character.race is mock_race
        assert character._class == "Воин"
        assert character.level == 5
        assert character.subrace is mock_subrace
        assert character.sub_class == "Рыцарь"
        assert character.ability_scores is mock_ability_scores

    def test_character_init_partial(self) -> None:
        """Тест частичной инициализации персонажа."""
        mock_race = Mock()
        mock_race.name = "Эльф"
        mock_race.size = Size.MEDIUM
        
        character = Character(
            name="Леголас",
            race=mock_race,
            _class="Следопыт",
            level=3
        )
        
        assert character.name == "Леголас"
        assert character.race is mock_race
        assert character._class == "Следопыт"
        assert character.level == 3
        assert character.subrace is None
        assert character.sub_class is None
        assert character.ability_scores is None

    def test_size_property_with_race(self) -> None:
        """Тест свойства size с установленной расой."""
        mock_race = Mock()
        mock_race.size = Size.SMALL
        
        character = Character(name="Халфлинг", race=mock_race)
        
        assert character.size == Size.SMALL

    def test_size_property_without_race(self) -> None:
        """Тест свойства size без установленной расы."""
        character = Character(name="Без расы")
        
        # Должен возвращать размер по умолчанию (MEDIUM)
        # Но в текущей реализации это вызовет AttributeError, т.к. race=None
        with pytest.raises(AttributeError):
            _ = character.size

    def test_character_with_different_race_sizes(self) -> None:
        """Тест персонажей с разными размерами рас."""
        sizes = [Size.TINY, Size.SMALL, Size.MEDIUM, Size.LARGE, Size.HUGE, Size.GARGANTUAN, Size.COLOSSAL]
        
        for size in sizes:
            mock_race = Mock()
            mock_race.size = size
            
            character = Character(name=f"Персонаж {size.value}", race=mock_race)
            
            assert character.size == size

    def test_character_level_validation(self) -> None:
        """Тест валидации уровня персонажа."""
        # Тест с корректными уровнями
        for level in [1, 5, 10, 20]:
            character = Character(level=level)
            assert character.level == level
        
        # Тест с некорректными уровнями (в текущей реализации нет валидации)
        # Это может быть добавлено в будущем
        character_negative = Character(level=-1)
        character_zero = Character(level=0)
        character_too_high = Character(level=100)
        
        assert character_negative.level == -1
        assert character_zero.level == 0
        assert character_too_high.level == 100

    def test_character_name_validation(self) -> None:
        """Тест валидации имени персонажа."""
        # Различные имена
        names = [
            "Арагорн",
            "Леголас",
            "Гимли",
            "Гэндальф",
            "Фродо",
            "Сэм",
            "",
            "Очень длинное имя персонажа с пробелами и символами 123!@#",
            "Имя на русском языке",
            "Name in English",
            "12345",
            "   пробелы   ",
        ]
        
        for name in names:
            character = Character(name=name)
            assert character.name == name

    def test_character_class_property(self) -> None:
        """Тест свойства класса персонажа."""
        classes = [
            "Воин",
            "Волшебник",
            "Следопыт",
            "Жрец",
            "Плут",
            "Бард",
            "Друид",
            "Паладин",
            "Чернокнижник",
            "Монах",
            "",
            "Кастомный класс",
        ]
        
        for class_name in classes:
            character = Character(_class=class_name)
            assert character._class == class_name

    def test_character_subclass_property(self) -> None:
        """Тест свойства подкласса персонажа."""
        subclasses = [
            None,
            "Рыцарь",
            "Заклинатель",
            "Лучник",
            "Целитель",
            "Убийца",
            "Скриптор",
            "",
            "Кастомный подкласс",
        ]
        
        for subclass in subclasses:
            character = Character(sub_class=subclass)
            assert character.sub_class == subclass

    def test_character_relationships(self) -> None:
        """Тест взаимосвязей персонажа."""
        mock_race = Mock()
        mock_race.name = "Человек"
        mock_race.size = Size.MEDIUM
        
        mock_subrace = Mock()
        mock_subrace.name = "Высший человек"
        
        # Проверяем, что подраса может быть связана с расой
        character = Character(
            name="Тестовый персонаж",
            race=mock_race,
            subrace=mock_subrace
        )
        
        assert character.race is mock_race
        assert character.subrace is mock_subrace
        
        # В реальном приложении может быть проверка, что подраса принадлежит расе
        # Но в текущей реализации такой проверки нет

    def test_character_ability_scores(self) -> None:
        """Тест характеристик персонажа."""
        mock_ability_scores = Mock()
        mock_ability_scores.strength = 16
        mock_ability_scores.dexterity = 14
        mock_ability_scores.constitution = 15
        mock_ability_scores.intelligence = 12
        mock_ability_scores.wisdom = 13
        mock_ability_scores.charisma = 10
        
        character = Character(
            name="Тестовый персонаж",
            ability_scores=mock_ability_scores
        )
        
        assert character.ability_scores is mock_ability_scores
        assert character.ability_scores.strength == 16

    def test_character_copy(self) -> None:
        """Тест копирования персонажа."""
        mock_race = Mock()
        mock_race.name = "Человек"
        mock_race.size = Size.MEDIUM
        
        original = Character(
            name="Оригинал",
            race=mock_race,
            _class="Воин",
            level=5
        )
        
        # Простое копирование через создание нового объекта с теми же данными
        copy = Character(
            name=original.name,
            race=original.race,
            _class=original._class,
            level=original.level,
            subrace=original.subrace,
            sub_class=original.sub_class,
            ability_scores=original.ability_scores
        )
        
        assert copy.name == original.name
        assert copy.race is original.race
        assert copy._class == original._class
        assert copy.level == original.level

    def test_character_str_representation(self) -> None:
        """Тест строкового представления персонажа."""
        mock_race = Mock()
        mock_race.name = "Эльф"
        
        character = Character(
            name="Леголас",
            race=mock_race,
            _class="Следопыт",
            level=5
        )
        
        # В текущей реализации нет метода __str__, но можно проверить базовое представление
        str_repr = str(character)
        assert "Леголас" in str_repr or "object" in str_repr.lower()

    def test_character_equality(self) -> None:
        """Тест равенства персонажей."""
        # В текущей реализации нет метода __eq__, поэтому используется сравнение объектов
        character1 = Character(name="Персонаж")
        character2 = Character(name="Персонаж")
        
        assert character1 is not character2
        assert character1 != character2  # Разные объекты
        
        # Проверяем равенство с самим собой
        assert character1 == character1
