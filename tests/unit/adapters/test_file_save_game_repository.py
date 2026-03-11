"""Тесты для FileSaveGameRepository.

Следует Clean Architecture - тестирование адаптера репозитория.
"""

import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.frameworks.repositories.file_save_game_repository import (
    FileSaveGameRepository,
)
from src.interfaces.repositories.save_game_repository import (
    SaveGame,
)


class TestFileSaveGameRepository:
    """Тесты файлового репозитория сохранений."""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Фикстура временной директории."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def repository(self, temp_dir: Path) -> FileSaveGameRepository:
        """Фикстура репозитория с временной директорией."""
        return FileSaveGameRepository(str(temp_dir))

    @pytest.fixture
    def sample_save_game(self) -> SaveGame:
        """Фикстура примера сохранения."""
        return SaveGame(
            save_id="test-id",
            character_name="Тестовый воин",
            character_level=1,
            character_class="Воин",
            save_time=datetime.now(),
            slot_number=1,
        )

    @pytest.fixture
    def sample_game_data(self) -> dict:
        """Фикстура данных игры."""
        return {
            "character": {
                "name": "Тестовый воин",
                "level": 1,
                "class": "Воин",
                "race": "Человек",
                "abilities": {"strength": 16, "dexterity": 14},
            },
            "game_state": {
                "current_location": "Таверна",
                "playtime_minutes": 0,
                "quests_completed": [],
                "current_objectives": [],
            },
            "version": "1.0.0",
        }

    def test_init_creates_directory(self, temp_dir: Path) -> None:
        """Тест создания директории при инициализации."""
        # Удаляем директорию если существует
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        FileSaveGameRepository(str(temp_dir))

        assert temp_dir.exists()
        assert (temp_dir / "metadata.json").exists()

    def test_save_new_game(
        self,
        repository: FileSaveGameRepository,
        sample_save_game: SaveGame,
        sample_game_data: dict,
    ) -> None:
        """Тест сохранения новой игры."""
        result = repository.save(sample_save_game, sample_game_data)

        assert result == sample_save_game

        # Проверяем создание файла сохранения
        save_file = (
            Path(repository._saves_directory)
            / f"{sample_save_game.save_id}.json"
        )
        assert save_file.exists()

        # Проверяем содержимое файла
        with open(save_file, encoding="utf-8") as f:
            save_data = json.load(f)

        assert save_data["metadata"]["save_id"] == sample_save_game.save_id
        assert save_data["game_data"] == sample_game_data

        # Проверяем метаданные
        metadata = repository._load_metadata()
        assert len(metadata["saves"]) == 1
        assert metadata["saves"][0]["save_id"] == sample_save_game.save_id

    def test_save_overwrites_existing_slot(
        self,
        repository: FileSaveGameRepository,
        sample_save_game: SaveGame,
        sample_game_data: dict,
    ) -> None:
        """Тест перезаписи существующего слота."""
        # Создаем первое сохранение
        repository.save(sample_save_game, sample_game_data)

        # Создаем второе сохранение в том же слоте
        second_save = SaveGame(
            save_id="second-id",
            character_name="Второй воин",
            character_level=2,
            character_class="Плут",
            save_time=datetime.now(),
            slot_number=1,  # Тот же слот
        )

        second_game_data = {
            "character": {
                "name": "Второй воин",
                "level": 2,
                "class": "Плут",
                "abilities": {"dexterity": 18, "intelligence": 14},
            },
            "game_state": {"current_location": "Лес"},
            "version": "1.0.0",
        }

        result = repository.save(second_save, second_game_data)

        assert result == second_save

        # Проверяем, что в метаданных только одно сохранение для слота 1
        metadata = repository._load_metadata()
        slot_saves = [s for s in metadata["saves"] if s["slot_number"] == 1]
        assert len(slot_saves) == 1
        assert slot_saves[0]["save_id"] == "second-id"

    def test_load_existing_game(
        self,
        repository: FileSaveGameRepository,
        sample_save_game: SaveGame,
        sample_game_data: dict,
    ) -> None:
        """Тест загрузки существующей игры."""
        # Сначала сохраняем
        repository.save(sample_save_game, sample_game_data)

        # Затем загружаем
        loaded_data = repository.load(sample_save_game.save_id)

        assert loaded_data == sample_game_data

    def test_load_nonexistent_game(
        self, repository: FileSaveGameRepository
    ) -> None:
        """Тест загрузки несуществующей игры."""
        result = repository.load("non-existent-id")

        assert result is None

    def test_find_by_id_existing(
        self,
        repository: FileSaveGameRepository,
        sample_save_game: SaveGame,
        sample_game_data: dict,
    ) -> None:
        """Тест поиска существующего сохранения по ID."""
        repository.save(sample_save_game, sample_game_data)

        result = repository.find_by_id(sample_save_game.save_id)

        assert result is not None
        assert result.save_id == sample_save_game.save_id
        assert result.character_name == sample_save_game.character_name

    def test_find_by_id_nonexistent(
        self, repository: FileSaveGameRepository
    ) -> None:
        """Тест поиска несуществующего сохранения по ID."""
        result = repository.find_by_id("non-existent-id")

        assert result is None

    def test_find_by_slot_existing(
        self,
        repository: FileSaveGameRepository,
        sample_save_game: SaveGame,
        sample_game_data: dict,
    ) -> None:
        """Тест поиска существующего сохранения по слоту."""
        repository.save(sample_save_game, sample_game_data)

        result = repository.find_by_slot(sample_save_game.slot_number)

        assert result is not None
        assert result.slot_number == sample_save_game.slot_number
        assert result.character_name == sample_save_game.character_name

    def test_find_by_slot_nonexistent(
        self, repository: FileSaveGameRepository
    ) -> None:
        """Тест поиска несуществующего сохранения по слоту."""
        result = repository.find_by_slot(999)

        assert result is None

    def test_find_all_empty(self, repository: FileSaveGameRepository) -> None:
        """Тест получения всех сохранений из пустого репозитория."""
        result = repository.find_all()

        assert result == []

    def test_find_all_with_saves(
        self,
        repository: FileSaveGameRepository,
        sample_save_game: SaveGame,
        sample_game_data: dict,
    ) -> None:
        """Тест получения всех сохранений."""
        # Создаем несколько сохранений
        repository.save(sample_save_game, sample_game_data)

        second_save = SaveGame(
            save_id="second-id",
            character_name="Второй",
            character_level=2,
            character_class="Плут",
            save_time=datetime.now(),
            slot_number=2,
        )
        repository.save(second_save, sample_game_data)

        result = repository.find_all()

        assert len(result) == 2
        save_ids = [s.save_id for s in result]
        assert sample_save_game.save_id in save_ids
        assert "second-id" in save_ids

    def test_delete_existing(
        self,
        repository: FileSaveGameRepository,
        sample_save_game: SaveGame,
        sample_game_data: dict,
    ) -> None:
        """Тест удаления существующего сохранения."""
        # Сначала сохраняем
        repository.save(sample_save_game, sample_game_data)

        # Проверяем, что файл существует
        save_file = (
            Path(repository._saves_directory)
            / f"{sample_save_game.save_id}.json"
        )
        assert save_file.exists()

        # Удаляем
        result = repository.delete(sample_save_game.save_id)

        assert result is True
        assert not save_file.exists()

        # Проверяем, что удалено из метаданных
        metadata = repository._load_metadata()
        save_ids = [s["save_id"] for s in metadata["saves"]]
        assert sample_save_game.save_id not in save_ids

    def test_delete_nonexistent(
        self, repository: FileSaveGameRepository
    ) -> None:
        """Тест удаления несуществующего сохранения."""
        result = repository.delete("non-existent-id")

        assert result is False

    def test_validate_save_format_valid(
        self, repository: FileSaveGameRepository
    ) -> None:
        """Тест валидации корректного формата сохранения."""
        valid_data = {
            "character": {
                "name": "Тест",
                "level": 1,
                "class": "Воин",
                "abilities": {"strength": 16},
            },
            "game_state": {"current_location": "Таверна"},
            "version": "1.0.0",
        }

        result = repository.validate_save_format(valid_data)

        assert result is True

    def test_validate_save_format_invalid(
        self, repository: FileSaveGameRepository
    ) -> None:
        """Тест валидации некорректного формата сохранения."""
        # Отсутствуют обязательные поля
        invalid_data = {
            "character": {
                "name": "Тест"
                # Отсутствуют level, class, abilities
            }
            # Отсутствуют game_state, version
        }

        result = repository.validate_save_format(invalid_data)

        assert result is False

    def test_validate_save_format_not_dict(
        self, repository: FileSaveGameRepository
    ) -> None:
        """Тест валидации не-словаря."""
        result = repository.validate_save_format("not a dict")

        assert result is False

    def test_saves_sorted_by_time(
        self,
        repository: FileSaveGameRepository,
        sample_save_game: SaveGame,
        sample_game_data: dict,
    ) -> None:
        """Тест сортировки сохранений по времени."""
        # Создаем сохранения в разное время
        first_save = SaveGame(
            save_id="first-id",
            character_name="Первый",
            character_level=1,
            character_class="Воин",
            save_time=datetime.now(),
            slot_number=1,
        )
        repository.save(first_save, sample_game_data)

        # Небольшая задержка для разницы во времени
        import time

        time.sleep(0.01)

        second_save = SaveGame(
            save_id="second-id",
            character_name="Второй",
            character_level=2,
            character_class="Плут",
            save_time=datetime.now(),
            slot_number=2,
        )
        repository.save(second_save, sample_game_data)

        result = repository.find_all()

        # Проверяем, что второе сохранение (более новое) первое в списке
        assert len(result) == 2
        assert result[0].save_id == "second-id"
        assert result[1].save_id == "first-id"
