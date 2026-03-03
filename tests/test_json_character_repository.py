"""Тесты для JSON репозитория персонажей."""

import json
import shutil
import tempfile
from pathlib import Path

from src.models.entities.character import Character
from src.repositories.json_character_repository import JsonCharacterRepository


class TestJsonCharacterRepository:
    """Тесты JSON репозитория персонажей."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test_characters.json"
        self.repo = JsonCharacterRepository(str(self.test_file))

    def teardown_method(self):
        """Очистка после каждого теста."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_new_repository(self):
        """Тест создания нового репозитория."""
        # Файл может не создаваться сразу, но директория должна быть
        assert self.test_file.parent.exists()

        # Репозиторий должен быть пустым
        assert len(self.repo.find_all()) == 0
        assert self.repo._next_id == 1

    def test_save_character(self):
        """Тест сохранения персонажа."""
        character = Character(name="Тестовый персонаж")
        saved = self.repo.save(character)

        assert saved.id is not None
        assert saved.id == 1
        assert saved.name == "Тестовый персонаж"
        assert saved.created_at is not None

        # Проверяем, что персонаж сохранен в файл
        found = self.repo.find_by_id(1)
        assert found is not None
        assert found.name == "Тестовый персонаж"

    def test_save_multiple_characters(self):
        """Тест сохранения нескольких персонажей."""
        names = ["Арагорн", "Фродо", "Леголас"]
        characters = []

        for name in names:
            character = Character(name=name)
            saved = self.repo.save(character)
            characters.append(saved)

        # Проверяем ID
        assert characters[0].id == 1
        assert characters[1].id == 2
        assert characters[2].id == 3

        # Проверяем, что все персонажи сохранены
        all_characters = self.repo.find_all()
        assert len(all_characters) == 3

        saved_names = [char.name for char in all_characters]
        assert set(saved_names) == set(names)

    def test_find_by_name(self):
        """Тест поиска по имени."""
        # Создаем персонажей
        self.repo.save(Character(name="Арагорн"))
        self.repo.save(Character(name="Фродо"))

        # Поиск точного имени
        found = self.repo.find_by_name("Арагорн")
        assert found is not None
        assert found.name == "Арагорн"

        # Поиск с разным регистром
        found = self.repo.find_by_name("фродо")
        assert found is not None
        assert found.name == "Фродо"

        # Поиск с пробелами
        found = self.repo.find_by_name("  Арагорн  ")
        assert found is not None
        assert found.name == "Арагорн"

        # Поиск несуществующего имени
        found = self.repo.find_by_name("Гэндальф")
        assert found is None

    def test_update_character(self):
        """Тест обновления персонажа."""
        # Создаем персонажа
        character = Character(name="Старое имя")
        saved = self.repo.save(character)

        original_created = saved.created_at

        # Небольшая задержка для обновления timestamp
        import time

        time.sleep(0.001)

        # Обновляем имя
        saved.name = "Новое имя"
        updated = self.repo.update(saved)

        assert updated.name == "Новое имя"
        assert updated.id == saved.id
        assert updated.created_at == original_created
        assert updated.updated_at >= saved.updated_at

        # Проверяем, что изменения сохранены
        found = self.repo.find_by_id(1)
        assert found.name == "Новое имя"

    def test_delete_character(self):
        """Тест удаления персонажа."""
        # Создаем персонажей
        self.repo.save(Character(name="Арагорн"))
        self.repo.save(Character(name="Фродо"))

        assert len(self.repo.find_all()) == 2

        # Удаляем персонажа
        deleted = self.repo.delete(1)
        assert deleted is True

        # Проверяем, что персонаж удален
        assert len(self.repo.find_all()) == 1
        assert self.repo.find_by_id(1) is None
        assert self.repo.find_by_name("Арагорн") is None

        # Второй персонаж должен остаться
        found = self.repo.find_by_id(2)
        assert found is not None
        assert found.name == "Фродо"

    def test_persistence_between_instances(self):
        """Тест сохранения данных между экземплярами репозитория."""
        # Создаем персонажа в первом экземпляре
        repo1 = JsonCharacterRepository(str(self.test_file))
        character = Character(name="Тестовый персонаж")
        saved = repo1.save(character)

        # Создаем новый экземпляр и проверяем, что данные загружены
        repo2 = JsonCharacterRepository(str(self.test_file))
        found = repo2.find_by_id(saved.id)

        assert found is not None
        assert found.name == "Тестовый персонаж"
        assert found.id == saved.id
        assert found.created_at is not None

    def test_json_file_structure(self):
        """Тест структуры JSON файла."""
        # Создаем персонажа
        character = Character(name="Тест")
        self.repo.save(character)

        # Читаем JSON файл
        with open(self.test_file, encoding="utf-8") as f:
            data = json.load(f)

        # Проверяем структуру
        assert "characters" in data
        assert "next_id" in data
        assert "last_updated" in data

        assert len(data["characters"]) == 1
        assert data["next_id"] == 2

        char_data = data["characters"][0]
        assert char_data["id"] == 1
        assert char_data["name"] == "Тест"
        assert "created_at" in char_data
        assert "updated_at" in char_data

    def test_load_from_existing_json(self):
        """Тест загрузки из существующего JSON файла."""
        # Создаем JSON файл вручную
        test_data = {
            "characters": [
                {
                    "id": 1,
                    "name": "Существующий персонаж",
                    "created_at": "2023-01-01T12:00:00",
                    "updated_at": "2023-01-01T12:00:00",
                }
            ],
            "next_id": 2,
            "last_updated": "2023-01-01T12:00:00",
        }

        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)

        # Создаем репозиторий и проверяем загрузку
        repo = JsonCharacterRepository(str(self.test_file))

        assert len(repo.find_all()) == 1
        assert repo._next_id == 2

        found = repo.find_by_id(1)
        assert found is not None
        assert found.name == "Существующий персонаж"

    def test_corrupted_json_handling(self):
        """Тест обработки поврежденного JSON файла."""
        # Создаем поврежденный JSON файл
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json")

        # Создание репозитория должно обработать ошибку
        repo = JsonCharacterRepository(str(self.test_file))

        # Репозиторий должен быть пустым
        assert len(repo.find_all()) == 0
        assert repo._next_id == 1

    def test_get_stats(self):
        """Тест получения статистики репозитория."""
        stats = self.repo.get_stats()

        assert stats["total_characters"] == 0
        assert stats["next_id"] == 1
        assert stats["file_path"] == str(self.test_file)
        # Файл может не существовать до первого сохранения
        # assert stats['file_exists'] is True
        # assert stats['file_size'] > 0

        # Добавляем персонажа
        self.repo.save(Character(name="Тест"))
        stats = self.repo.get_stats()

        assert stats["total_characters"] == 1
        assert stats["next_id"] == 2
        assert stats["file_exists"] is True
        assert stats["file_size"] > 0

    def test_character_with_whitespace_name(self):
        """Тест сохранения персонажа с именем, содержащим пробелы."""
        character = Character(name="  Тестовый персонаж  ")
        saved = self.repo.save(character)

        # Имя должно быть сохранено как есть
        assert saved.name == "  Тестовый персонаж  "

        # Но поиск должен работать с обрезанными пробелами
        found = self.repo.find_by_name("Тестовый персонаж")
        assert found is not None
        assert found.name == "  Тестовый персонаж  "

    def test_atomic_save(self):
        """Тест атомарного сохранения."""
        # Создаем персонажа
        character = Character(name="Тест")
        self.repo.save(character)

        # Файл должен существовать и быть валидным
        assert self.test_file.exists()

        # Проверяем, что временный файл удаляется
        temp_file = self.test_file.with_suffix(".tmp")
        assert not temp_file.exists()

        # Проверяем валидность JSON
        with open(self.test_file, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data["characters"]) == 1
