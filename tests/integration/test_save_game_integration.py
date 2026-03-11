"""Интеграционные тесты системы сохранений.

Следует Clean Architecture - тестирование взаимодействия всех слоев.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from src.dependency_injection import DIContainer
from src.dto.save_game_dto import SaveGameRequest
from src.frameworks.repositories.file_save_game_repository import (
    FileSaveGameRepository,
)


class TestSaveGameIntegration:
    """Интеграционные тесты системы сохранений."""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Фикстура временной директории."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def di_container(self, temp_dir: Path) -> DIContainer:
        """Фикстура DI контейнера с временной директорией."""
        container = DIContainer()

        # Заменяем репозиторий на тестовый
        test_repository = FileSaveGameRepository(str(temp_dir))
        container.register_singleton("save_game_repository", test_repository)

        return container

    @pytest.fixture
    def save_controller(self, di_container: DIContainer):
        """Фикстура контроллера сохранений."""
        return di_container.get("save_game_controller")

    @pytest.fixture
    def sample_character_data(self) -> dict:
        """Фикстура данных персонажа."""
        return {
            "name": "Интеграционный воин",
            "level": 3,
            "class": "Воин",
            "race": "Человек",
            "background": "Воин",
            "abilities": {
                "strength": 18,
                "dexterity": 14,
                "constitution": 16,
                "intelligence": 12,
                "wisdom": 13,
                "charisma": 10,
            },
            "hp": 19,
            "ac": 18,
            "equipment": ["длинный меч", "щит", "кольчуга"],
            "gold": 25,
            "skills": ["атака", "запугивание", "атлетика"],
            "features": ["стиль боя: защита", "восстановление"],
        }

    def test_full_save_load_cycle(
        self, save_controller, sample_character_data: dict
    ) -> None:
        """Тест полного цикла сохранения и загрузки."""
        # 1. Создаем сохранение
        save_request = SaveGameRequest(
            action="save",
            character_name="Интеграционный воин",
            character_level=3,
            character_class="Воин",
            character_data=sample_character_data,
            slot_number=5,
            location="Интеграционная локация",
        )

        save_response = save_controller.handle_request(save_request)

        assert save_response.success is True
        assert save_response.save_game is not None
        save_id = save_response.save_game["save_id"]

        # 2. Загружаем список сохранений
        list_request = SaveGameRequest(action="list")
        list_response = save_controller.handle_request(list_request)

        assert list_response.success is True
        assert len(list_response.all_saves) == 1
        assert (
            list_response.all_saves[0]["character_name"]
            == "Интеграционный воин"
        )
        assert list_response.all_saves[0]["slot_number"] == 5

        # 3. Загружаем сохранение
        load_request = SaveGameRequest(action="load", save_id=save_id)

        load_response = save_controller.handle_request(load_request)

        assert load_response.success is True
        assert load_response.game_data is not None
        assert (
            load_response.game_data["character"]["name"]
            == "Интеграционный воин"
        )
        assert load_response.game_data["character"]["level"] == 3
        assert (
            load_response.game_data["character"]["abilities"]["strength"] == 18
        )
        assert (
            load_response.game_data["game_state"]["current_location"]
            == "Интеграционная локация"
        )

    def test_multiple_saves_management(
        self, save_controller, sample_character_data: dict
    ) -> None:
        """Тест управления несколькими сохранениями."""
        # Создаем первое сохранение
        save1_request = SaveGameRequest(
            action="save",
            character_name="Воин 1",
            character_level=1,
            character_class="Воин",
            character_data=sample_character_data,
            slot_number=1,
        )

        save1_response = save_controller.handle_request(save1_request)
        assert save1_response.success is True

        # Создаем второе сохранение
        save2_data = sample_character_data.copy()
        save2_data["name"] = "Плут 2"
        save2_data["level"] = 2
        save2_data["class"] = "Плут"

        save2_request = SaveGameRequest(
            action="save",
            character_name="Плут 2",
            character_level=2,
            character_class="Плут",
            character_data=save2_data,
            slot_number=2,
        )

        save2_response = save_controller.handle_request(save2_request)
        assert save2_response.success is True

        # Проверяем список
        list_request = SaveGameRequest(action="list")
        list_response = save_controller.handle_request(list_request)

        assert list_response.success is True
        assert len(list_response.all_saves) == 2

        # Проверяем доступные слоты
        slots_request = SaveGameRequest(action="get_available_slots")
        slots_response = save_controller.handle_request(slots_request)

        assert slots_response.success is True
        assert len(slots_response.available_slots) == 8  # 10 - 2 занятых
        assert 1 not in slots_response.available_slots
        assert 2 not in slots_response.available_slots
        assert 3 in slots_response.available_slots

        # Удаляем первое сохранение
        delete_request = SaveGameRequest(
            action="delete", save_id=save1_response.save_game["save_id"]
        )

        delete_response = save_controller.handle_request(delete_request)
        assert delete_response.success is True

        # Проверяем, что слот освободился
        slots_response_after = save_controller.handle_request(slots_request)
        assert 1 in slots_response_after.available_slots
        assert 2 not in slots_response_after.available_slots

    def test_slot_overwrite(
        self, save_controller, sample_character_data: dict
    ) -> None:
        """Тест перезаписи слота."""
        # Создаем первое сохранение
        save1_request = SaveGameRequest(
            action="save",
            character_name="Оригинальный персонаж",
            character_level=1,
            character_class="Воин",
            character_data=sample_character_data,
            slot_number=3,
        )

        save1_response = save_controller.handle_request(save1_request)
        assert save1_response.success is True
        original_save_id = save1_response.save_game["save_id"]

        # Перезаписываем тот же слот
        save2_data = sample_character_data.copy()
        save2_data["name"] = "Новый персонаж"
        save2_data["level"] = 5
        save2_data["class"] = "Паладин"

        save2_request = SaveGameRequest(
            action="save",
            character_name="Новый персонаж",
            character_level=5,
            character_class="Паладин",
            character_data=save2_data,
            slot_number=3,  # Тот же слот
        )

        save2_response = save_controller.handle_request(save2_request)
        assert save2_response.success is True
        new_save_id = save2_response.save_game["save_id"]

        # Проверяем, что ID разные
        assert original_save_id != new_save_id

        # Проверяем, что старое сохранение не загружается
        load_old_request = SaveGameRequest(
            action="load", save_id=original_save_id
        )

        load_old_response = save_controller.handle_request(load_old_request)
        assert load_old_response.success is False
        assert "Сохранение не найдено" in load_old_response.message

        # Проверяем, что новое сохранение загружается корректно
        load_new_request = SaveGameRequest(action="load", save_id=new_save_id)

        load_new_response = save_controller.handle_request(load_new_request)
        assert load_new_response.success is True
        assert (
            load_new_response.game_data["character"]["name"]
            == "Новый персонаж"
        )
        assert load_new_response.game_data["character"]["level"] == 5

    def test_character_preview(
        self, save_controller, sample_character_data: dict
    ) -> None:
        """Тест предпросмотра персонажа."""
        # Создаем данные персонажа с правильным именем
        character_data = sample_character_data.copy()
        character_data["name"] = "Персонаж для предпросмотра"
        character_data["level"] = 4
        character_data["class"] = "Жрец"

        # Создаем сохранение
        save_request = SaveGameRequest(
            action="save",
            character_name="Персонаж для предпросмотра",
            character_level=4,
            character_class="Жрец",
            character_data=character_data,
            slot_number=7,
        )

        save_response = save_controller.handle_request(save_request)
        assert save_response.success is True

        save_id = save_response.save_game["save_id"]

        # Получаем предпросмотр
        preview = save_controller.get_character_preview(save_id)

        assert preview is not None
        assert preview.name == "Персонаж для предпросмотра"
        assert preview.level == 4
        assert preview.character_class == "Жрец"
        assert preview.race == "Человек"
        assert preview.background == "Воин"
        assert preview.abilities == sample_character_data["abilities"]
        assert preview.hp == sample_character_data["hp"]
        assert preview.ac == sample_character_data["ac"]

    def test_quick_save_functionality(
        self, save_controller, sample_character_data: dict
    ) -> None:
        """Тест функциональности быстрого сохранения."""
        # Используем быстрое сохранение
        response = save_controller.quick_save(
            character_name="Быстрый персонаж",
            character_level=2,
            character_class="Варвар",
            character_data=sample_character_data,
            location="Быстрая локация",
        )

        assert response.success is True
        assert response.save_game is not None
        assert "Игра быстро сохранена в слот" in response.message

        # Проверяем, что сохранение appears в списке
        list_request = SaveGameRequest(action="list")
        list_response = save_controller.handle_request(list_request)

        assert list_response.success is True
        assert len(list_response.all_saves) == 1
        assert (
            list_response.all_saves[0]["character_name"] == "Быстрый персонаж"
        )

    def test_error_handling(self, save_controller) -> None:
        """Тест обработки ошибок."""
        # Запрос с отсутствующими данными
        invalid_request = SaveGameRequest(action="save")
        response = save_controller.handle_request(invalid_request)

        assert response.success is False
        assert "Отсутствуют обязательные данные" in response.message

        # Загрузка несуществующего сохранения
        load_request = SaveGameRequest(
            action="load", save_id="non-existent-id"
        )
        load_response = save_controller.handle_request(load_request)

        assert load_response.success is False
        assert "Сохранение не найдено" in load_response.message

        # Удаление несуществующего сохранения
        delete_request = SaveGameRequest(
            action="delete", save_id="non-existent-id"
        )
        delete_response = save_controller.handle_request(delete_request)

        assert delete_response.success is False
        assert "Сохранение не найдено" in delete_response.message

    def test_slots_info(
        self, save_controller, sample_character_data: dict
    ) -> None:
        """Тест информации о слотах."""
        # Создаем сохранения в разных слотах
        for slot_num, char_info in [(1, "Воин"), (5, "Плут"), (9, "Жрец")]:
            save_request = SaveGameRequest(
                action="save",
                character_name=char_info,
                character_level=1,
                character_class=char_info,
                character_data=sample_character_data,
                slot_number=slot_num,
            )
            save_controller.handle_request(save_request)

        # Получаем информацию о слотах
        slots = save_controller.get_save_slots_info()

        assert len(slots) == 10

        # Проверяем занятые слоты
        occupied_slots = [s for s in slots if s.is_occupied]
        assert len(occupied_slots) == 3

        occupied_numbers = {s.slot_number for s in occupied_slots}
        assert 1 in occupied_numbers
        assert 5 in occupied_numbers
        assert 9 in occupied_numbers

        # Проверяем свободные слоты
        free_slots = [s for s in slots if not s.is_occupied]
        assert len(free_slots) == 7

        free_numbers = {s.slot_number for s in free_slots}
        assert 2 in free_numbers
        assert 3 in free_numbers
        assert 4 in free_numbers
