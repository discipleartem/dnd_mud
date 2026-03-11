"""Юнит-тесты для сущности сохранения игры.

Следует Clean Architecture - тестируем бизнес-правила сущности.
Entities не должны зависеть от внешних слоев.
"""

from datetime import datetime

import pytest

from src.entities.save_game_entity import SaveGameEntity


class TestSaveGameEntity:
    """Тесты бизнес-правил сущности SaveGameEntity.

    Entity содержит только бизнес-логику без внешних зависимостей.
    """

    def test_save_game_creation_valid(self):
        """Тест создания валидного сохранения согласно бизнес-правилам.

        Business Rules:
        - Имя персонажа не может быть пустым
        - Уровень от 1 до 20
        - Класс персонажа обязателен
        - Номер слота от 1 до 10
        """
        save_time = datetime.now()

        save = SaveGameEntity(
            save_id="test-save-123",
            character_name="Test Character",
            character_level=5,
            character_class="Warrior",
            save_time=save_time,
            slot_number=3,
            game_version="1.2.0",
            playtime_minutes=120,
            location="Forest",
            character_data={"strength": 16, "dexterity": 14},
        )

        assert save.save_id == "test-save-123"
        assert save.character_name == "Test Character"
        assert save.character_level == 5
        assert save.character_class == "Warrior"
        assert save.save_time == save_time
        assert save.slot_number == 3
        assert save.game_version == "1.2.0"
        assert save.playtime_minutes == 120
        assert save.location == "Forest"
        assert save.character_data == {"strength": 16, "dexterity": 14}

    def test_save_game_creation_with_defaults(self):
        """Тест создания сохранения с значениями по умолчанию."""
        save = SaveGameEntity(
            character_name="Test Character",
            character_level=5,
            character_class="Mage",
        )

        assert save.character_name == "Test Character"
        assert save.character_level == 5
        assert save.character_class == "Mage"
        assert save.slot_number == 1
        assert save.game_version == "1.0.0"
        assert save.playtime_minutes == 0
        assert save.location == "Начало пути"
        assert save.character_data == {}
        assert save.save_id is not None  # Сгенерирован автоматически
        assert save.save_time is not None  # Установлено автоматически

    def test_save_game_validation_empty_character_name(self):
        """Тест бизнес-правила: имя персонажа не может быть пустым."""
        with pytest.raises(
            ValueError, match="Имя персонажа не может быть пустым"
        ):
            SaveGameEntity(character_name="")

        with pytest.raises(
            ValueError, match="Имя персонажа не может быть пустым"
        ):
            SaveGameEntity(character_name="   ")

    def test_save_game_validation_invalid_character_level(self):
        """Тест валидации: неверный уровень персонажа."""
        with pytest.raises(
            ValueError, match="Уровень персонажа должен быть от 1 до 20"
        ):
            SaveGameEntity(character_name="Test", character_level=0)

        with pytest.raises(
            ValueError, match="Уровень персонажа должен быть от 1 до 20"
        ):
            SaveGameEntity(character_name="Test", character_level=21)

    def test_save_game_validation_empty_character_class(self):
        """Тест валидации: пустой класс персонажа."""
        with pytest.raises(
            ValueError, match="Класс персонажа не может быть пустым"
        ):
            SaveGameEntity(character_name="Test", character_class="")

        with pytest.raises(
            ValueError, match="Класс персонажа не может быть пустым"
        ):
            SaveGameEntity(character_name="Test", character_class="   ")

    def test_save_game_validation_invalid_slot_number(self):
        """Тест валидации: неверный номер слота."""
        with pytest.raises(
            ValueError, match="Номер слота должен быть от 1 до 10"
        ):
            SaveGameEntity(
                character_name="Test", character_class="Warrior", slot_number=0
            )

        with pytest.raises(
            ValueError, match="Номер слота должен быть от 1 до 10"
        ):
            SaveGameEntity(
                character_name="Test",
                character_class="Warrior",
                slot_number=11,
            )

    def test_save_game_validation_negative_playtime(self):
        """Тест валидации: отрицательное время игры."""
        with pytest.raises(
            ValueError, match="Время игры не может быть отрицательным"
        ):
            SaveGameEntity(
                character_name="Test",
                character_class="Warrior",
                playtime_minutes=-5,
            )

    def test_update_character_info_valid(self):
        """Тест обновления информации о персонаже."""
        save = SaveGameEntity(
            character_name="Old Name",
            character_level=3,
            character_class="Old Class",
        )

        save.update_character_info("New Name", 7, "New Class")

        assert save.character_name == "New Name"
        assert save.character_level == 7
        assert save.character_class == "New Class"

    def test_update_character_info_invalid(self):
        """Тест обновления с невалидными данными."""
        save = SaveGameEntity(
            character_name="Test", character_level=5, character_class="Warrior"
        )

        # Пустое имя
        with pytest.raises(
            ValueError, match="Имя персонажа не может быть пустым"
        ):
            save.update_character_info("", 5, "Warrior")

        # Неверный уровень
        with pytest.raises(
            ValueError, match="Уровень персонажа должен быть от 1 до 20"
        ):
            save.update_character_info("Test", 25, "Warrior")

    def test_update_playtime_valid(self):
        """Тест обновления времени игры."""
        save = SaveGameEntity(
            character_name="Test",
            character_class="Warrior",
            playtime_minutes=100,
        )

        save.update_playtime(50)
        assert save.playtime_minutes == 150

        # Добавляем 0 минут
        save.update_playtime(0)
        assert save.playtime_minutes == 150

    def test_update_playtime_negative(self):
        """Тест обновления времени игры с отрицательным значением."""
        save = SaveGameEntity(character_name="Test", character_class="Warrior")

        with pytest.raises(
            ValueError,
            match="Дополнительное время не может быть отрицательным",
        ):
            save.update_playtime(-10)

    def test_update_location_valid(self):
        """Тест обновления локации."""
        save = SaveGameEntity(character_name="Test", character_class="Warrior")

        save.update_location("Dungeon")
        assert save.location == "Dungeon"

    def test_update_location_empty(self):
        """Тест обновления локации с пустым значением."""
        save = SaveGameEntity(character_name="Test", character_class="Warrior")

        with pytest.raises(ValueError, match="Локация не может быть пустой"):
            save.update_location("")

        with pytest.raises(ValueError, match="Локация не может быть пустой"):
            save.update_location("   ")

    def test_set_character_data_valid(self):
        """Тест установки данных персонажа."""
        save = SaveGameEntity(character_name="Test", character_class="Warrior")

        new_data = {
            "strength": 18,
            "wisdom": 12,
            "inventory": ["sword", "shield"],
        }
        save.set_character_data(new_data)

        assert save.character_data == new_data

        # Проверяем, что это копия, а не ссылка
        new_data["strength"] = 20
        assert save.character_data["strength"] == 18

    def test_set_character_data_invalid_type(self):
        """Тест установки данных персонажа неверного типа."""
        save = SaveGameEntity(character_name="Test", character_class="Warrior")

        with pytest.raises(
            ValueError, match="Данные персонажа должны быть словарем"
        ):
            save.set_character_data("not a dict")

        with pytest.raises(
            ValueError, match="Данные персонажа должны быть словарем"
        ):
            save.set_character_data(123)

    def test_get_character_data(self):
        """Тест получения данных персонажа."""
        original_data = {"strength": 16, "dexterity": 14}
        save = SaveGameEntity(
            character_name="Test",
            character_class="Warrior",
            character_data=original_data,
        )

        retrieved_data = save.get_character_data()

        assert retrieved_data == original_data

        # Проверяем, что возвращается копия
        retrieved_data["strength"] = 20
        assert save.character_data["strength"] == 16

    def test_to_dict(self):
        """Тест преобразования в словарь."""
        save_time = datetime(2023, 1, 1, 12, 0, 0)
        save = SaveGameEntity(
            save_id="test-123",
            character_name="Test",
            character_level=5,
            character_class="Warrior",
            save_time=save_time,
            slot_number=2,
            game_version="1.5.0",
            playtime_minutes=180,
            location="Castle",
            character_data={"hp": 50, "mp": 30},
        )

        result = save.to_dict()

        expected = {
            "save_id": "test-123",
            "character_name": "Test",
            "character_level": 5,
            "character_class": "Warrior",
            "save_time": "2023-01-01T12:00:00",
            "slot_number": 2,
            "game_version": "1.5.0",
            "playtime_minutes": 180,
            "location": "Castle",
            "character_data": {"hp": 50, "mp": 30},
        }

        assert result == expected

    def test_from_dict_complete(self):
        """Тест создания из полного словаря."""
        data = {
            "save_id": "test-456",
            "character_name": "From Dict",
            "character_level": 8,
            "character_class": "Rogue",
            "save_time": "2023-06-15T14:30:00",
            "slot_number": 4,
            "game_version": "2.0.0",
            "playtime_minutes": 240,
            "location": "City",
            "character_data": {"gold": 1000, "items": ["dagger"]},
        }

        save = SaveGameEntity.from_dict(data)

        assert save.save_id == "test-456"
        assert save.character_name == "From Dict"
        assert save.character_level == 8
        assert save.character_class == "Rogue"
        assert save.save_time == datetime(2023, 6, 15, 14, 30, 0)
        assert save.slot_number == 4
        assert save.game_version == "2.0.0"
        assert save.playtime_minutes == 240
        assert save.location == "City"
        assert save.character_data == {"gold": 1000, "items": ["dagger"]}

    def test_from_dict_partial(self):
        """Тест создания сущности из неполных данных."""
        from datetime import datetime

        data = {
            "character_name": "Test Character",
            "character_level": 3,
            "character_class": "Rogue",
            "save_time": datetime.now().isoformat(),  # Добавляем обязательное поле
            "slot_number": 2,
        }

        save = SaveGameEntity.from_dict(data)

        assert save.character_name == "Test Character"
        assert save.character_level == 3
        assert save.character_class == "Rogue"
        assert save.slot_number == 2
        assert save.game_version == "1.0.0"  # Значение по умолчанию
        assert save.playtime_minutes == 0  # Значение по умолчанию
        assert save.location == "Начало пути"  # Значение по умолчанию
        assert save.character_data == {}  # По умолчанию
        assert save.save_id is not None  # Сгенерирован

    def test_get_display_info(self):
        """Тест получения информации для отображения."""
        save_time = datetime(2023, 12, 25, 15, 30, 0)
        save = SaveGameEntity(
            save_id="display-test",
            character_name="Display Test",
            character_level=12,
            character_class="Paladin",
            save_time=save_time,
            slot_number=3,
            playtime_minutes=125,  # 2ч 5м
            location="Temple",
        )

        display_info = save.get_display_info()

        expected = {
            "save_id": "display-test",
            "character_name": "Display Test",
            "character_level": "12",
            "character_class": "Paladin",
            "save_time": "2023-12-25 15:30",
            "slot_number": "3",
            "playtime_hours": "2ч 5м",
            "location": "Temple",
        }

        assert display_info == expected

    def test_get_display_info_round_hours(self):
        """Тест отображения времени с полными часами."""
        save = SaveGameEntity(
            character_name="Test",
            character_class="Warrior",
            playtime_minutes=180,  # 3ч 0м
        )

        display_info = save.get_display_info()
        assert display_info["playtime_hours"] == "3ч 0м"

    def test_edge_case_maximum_values(self):
        """Тест граничных значений."""
        save = SaveGameEntity(
            character_name="Max Test",
            character_level=20,  # Максимум
            character_class="Warrior",
            slot_number=10,  # Максимум
            playtime_minutes=999999,
        )

        assert save.character_level == 20
        assert save.slot_number == 10
        assert save.playtime_minutes == 999999
