"""Тесты для сущности персонажа."""


from src.entities.character import Character


class TestCharacter:
    """Тесты для персонажа."""

    def test_character_creation(self) -> None:
        """Тест создания персонажа."""
        character = Character(name="Тест", level=1, hit_points=10, max_hit_points=10)

        assert character.name == "Тест"
        assert character.level == 1
        assert character.hit_points == 10
        assert character.max_hit_points == 10

    def test_character_is_alive(self) -> None:
        """Тест проверки жизни."""
        character = Character(name="Тест", hit_points=10)

        assert character.is_alive() is True

        character.hit_points = 0
        assert character.is_alive() is False

    def test_character_get_status(self) -> None:
        """Тест получения статуса."""
        character = Character(name="Тест", hit_points=10, max_hit_points=10)

        assert character.get_status() == "Здоров"

        character.hit_points = 5
        assert character.get_status() == "Ранен"

        character.hit_points = 2
        assert character.get_status() == "Тяжело ранен"

        character.hit_points = 0
        assert character.get_status() == "Погиб"

    def test_character_str(self) -> None:
        """Тест строкового представления."""
        character = Character(name="Тест", level=1, hit_points=10, max_hit_points=10)

        expected = "Тест (Уровень 1, HP: 10/10)"
        assert str(character) == expected
