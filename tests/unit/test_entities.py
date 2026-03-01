"""Тесты для бизнес-сущностей.

Следует принципам:
- Простые тесты для простой логики
- Проверка бизнес-правил D&D
- Явное лучше неявного
"""

import pytest

from entities.character import Character
from entities.game_session import GameSession


class TestCharacter:
    """Тесты сущности персонажа."""

    def test_character_creation_valid(self):
        """Тест создания валидного персонажа."""
        character = Character(name="Артем", level=1, hit_points=10, max_hit_points=10)

        assert character.name == "Артем"
        assert character.level == 1
        assert character.hit_points == 10
        assert character.max_hit_points == 10
        assert character.is_alive()

    def test_character_creation_invalid_name(self):
        """Тест создания персонажа с невалидным именем."""
        with pytest.raises(ValueError, match="Имя слишком короткое"):
            Character(name="", level=1)

        with pytest.raises(ValueError, match="Имя слишком короткое"):
            Character(name="А", level=1)

    def test_character_creation_invalid_level(self):
        """Тест создания персонажа с невалидным уровнем."""
        with pytest.raises(ValueError, match="Неверный уровень"):
            Character(name="Артем", level=0)

        with pytest.raises(ValueError, match="Неверный уровень"):
            Character(name="Артем", level=21)

    def test_character_creation_invalid_hp(self):
        """Тест создания персонажа с невалидными HP."""
        with pytest.raises(ValueError, match="HP не могут быть отрицательными"):
            Character(name="Артем", hit_points=-1)

        with pytest.raises(ValueError, match="Max HP должны быть положительными"):
            Character(name="Артем", max_hit_points=0)

    def test_take_damage(self):
        """Тест получения урона."""
        character = Character(name="Артем", hit_points=10, max_hit_points=10)

        character.take_damage(3)
        assert character.hit_points == 7
        assert character.is_alive()

        character.take_damage(10)
        assert character.hit_points == 0
        assert not character.is_alive()

    def test_take_damage_negative(self):
        """Тест получения отрицательного урона."""
        character = Character(name="Артем")

        with pytest.raises(ValueError, match="Урон не может быть отрицательным"):
            character.take_damage(-1)

    def test_heal(self):
        """Тест лечения."""
        character = Character(name="Артем", hit_points=5, max_hit_points=10)

        character.heal(3)
        assert character.hit_points == 8

        # Лечение не должно превышать максимум
        character.heal(5)
        assert character.hit_points == 10

    def test_heal_negative(self):
        """Тест отрицательного лечения."""
        character = Character(name="Артем")

        with pytest.raises(ValueError, match="Лечение не может быть отрицательным"):
            character.heal(-1)

    def test_level_up(self):
        """Тест повышения уровня."""
        character = Character(name="Артем", level=1, hit_points=10, max_hit_points=10)

        character.level_up()
        assert character.level == 2
        assert character.max_hit_points == 12
        assert character.hit_points == 12

    def test_level_up_max_level(self):
        """Тест повышения уровня до максимума."""
        character = Character(name="Артем", level=20)

        with pytest.raises(ValueError, match="Максимальный уровень достигнут"):
            character.level_up()

    def test_get_status(self):
        """Тест получения статуса."""
        # Здоров
        character = Character(name="Артем", hit_points=9, max_hit_points=10)
        assert character.get_status() == "Здоров"

        # Ранен
        character = Character(name="Артем", hit_points=5, max_hit_points=10)
        assert character.get_status() == "Ранен"

        # Тяжело ранен
        character = Character(name="Артем", hit_points=2, max_hit_points=10)
        assert character.get_status() == "Тяжело ранен"

        # Погиб
        character = Character(name="Артем", hit_points=0, max_hit_points=10)
        assert character.get_status() == "Погиб"

    def test_str_representation(self):
        """Тест строкового представления."""
        character = Character(name="Артем", level=5, hit_points=8, max_hit_points=10)
        str_repr = str(character)

        assert "Артем" in str_repr
        assert "Уровень 5" in str_repr
        assert "8/10" in str_repr


class TestGameSession:
    """Тесты сессии игры."""

    def test_session_creation_valid(self):
        """Тест создания валидной сессии."""
        character = Character(name="Артем")
        session = GameSession(player=character, session_name="Тестовая игра")

        assert session.player == character
        assert session.session_name == "Тестовая игра"
        assert session.turn_count == 0
        assert session.is_new_game()

    def test_session_creation_invalid_player(self):
        """Тест создания сессии без персонажа."""
        with pytest.raises(ValueError, match="Персонаж обязателен"):
            GameSession(player=None)

    def test_session_creation_invalid_name(self):
        """Тест создания сессии с пустым названием."""
        character = Character(name="Артем")

        with pytest.raises(ValueError, match="Название сессии не может быть пустым"):
            GameSession(player=character, session_name="")

        with pytest.raises(ValueError, match="Название сессии не может быть пустым"):
            GameSession(player=character, session_name="   ")

    def test_session_creation_invalid_turns(self):
        """Тест создания сессии с отрицательным количеством ходов."""
        character = Character(name="Артем")

        with pytest.raises(ValueError, match="Количество ходов не может быть отрицательным"):
            GameSession(player=character, turn_count=-1)

    def test_advance_turn(self):
        """Тест продвижения хода."""
        character = Character(name="Артем")
        session = GameSession(player=character)

        session.advance_turn()
        assert session.turn_count == 1
        assert not session.is_new_game()

        session.advance_turn()
        assert session.turn_count == 2

    def test_get_session_info(self):
        """Тест получения информации о сессии."""
        character = Character(name="Артем")
        session = GameSession(player=character, session_name="Приключение")

        info = session.get_session_info()
        assert "Приключение" in info
        assert "Ход 0" in info

        session.advance_turn()
        info = session.get_session_info()
        assert "Ход 1" in info

    def test_reset_session(self):
        """Тест сброса сессии."""
        character = Character(name="Артем")
        session = GameSession(player=character, session_name="Тест")

        session.advance_turn()
        assert session.turn_count == 1
        assert not session.is_new_game()

        session.reset_session()
        assert session.turn_count == 0
        assert session.session_name == "Новая игра"
        assert session.is_new_game()

    def test_str_representation(self):
        """Тест строкового представления."""
        character = Character(name="Артем", level=1)
        session = GameSession(player=character, session_name="Тест")

        str_repr = str(session)
        assert "Тест" in str_repr
        assert "Ход 0" in str_repr
        assert "Артем" in str_repr
