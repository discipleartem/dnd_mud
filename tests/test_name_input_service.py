"""Интеграционные тесты для NameInputService."""

import pytest
from datetime import datetime
from src.services.name_input_service import NameInputService
from src.repositories.json_character_repository import JsonCharacterRepository
from src.models.entities.character import Character


import tempfile
import shutil
from pathlib import Path

class TestNameInputService:
    """Интеграционные тесты сервиса ввода имени."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test_characters.json"
        self.repo = JsonCharacterRepository(str(self.test_file))
        self.service = NameInputService(self.repo)
    
    def teardown_method(self):
        """Очистка после каждого теста."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_character_with_valid_name(self):
        """Тест создания персонажа с валидным именем."""
        name = "Арагорн"
        character = self.service.create_character_with_name(name)
        
        assert character is not None
        assert character.name == "Арагорн"
        assert character.id is not None
        assert character.created_at is not None
        assert character.updated_at is not None
        assert character.is_new is False
    
    def test_create_character_with_whitespace_name(self):
        """Тест создания персонажа с именем, содержащим пробелы."""
        name = "  Фродо  "
        character = self.service.create_character_with_name(name)
        
        assert character is not None
        assert character.name == "Фродо"  # Пробелы должны быть обрезаны
    
    def test_create_character_with_invalid_name_raises_error(self):
        """Тест создания персонажа с невалидным именем вызывает ошибку."""
        invalid_names = [
            "",  # Пустое
            "А",  # Слишком короткое
            "А" * 17,  # Слишком длинное
            "Gandalf123",  # С цифрами
            "Legolas!",  # Со спецсимволами
            "-Арагорн",  # Начинается с дефиса
            "Арагорн-",  # Заканчивается дефисом
            "Иван--Царевич"  # Двойной дефис
        ]
        
        for invalid_name in invalid_names:
            with pytest.raises(ValueError) as exc_info:
                self.service.create_character_with_name(invalid_name)
            
            assert str(exc_info.value) is not None
            assert len(str(exc_info.value)) > 0
    
    def test_create_character_with_duplicate_name_raises_error(self):
        """Тест создания персонажа с дублирующимся именем вызывает ошибку."""
        name = "Гэндальф"
        
        # Создаем первого персонажа
        character1 = self.service.create_character_with_name(name)
        assert character1 is not None
        
        # Попытка создать второго с тем же именем
        with pytest.raises(ValueError) as exc_info:
            self.service.create_character_with_name(name)
        
        assert "уже существует" in str(exc_info.value)
    
    def test_check_name_uniqueness(self):
        """Тест проверки уникальности имени."""
        name = "Legolas"
        
        # Имя уникально до создания персонажа
        assert self.service.check_name_uniqueness(name) is True
        
        # Создаем персонажа
        self.service.create_character_with_name(name)
        
        # Имя больше не уникально
        assert self.service.check_name_uniqueness(name) is False
        
        # Другое имя остается уникальным
        assert self.service.check_name_uniqueness("Арагорн") is True
    
    def test_check_name_uniqueness_case_insensitive(self):
        """Тест проверки уникальности имени без учета регистра."""
        name = "RobinHood"
        name_different_case = "robinhood"
        name_with_spaces = "  RobinHood  "
        
        # Создаем персонажа
        self.service.create_character_with_name(name)
        
        # Проверяем разные варианты того же имени
        assert self.service.check_name_uniqueness(name_different_case) is False
        assert self.service.check_name_uniqueness(name_with_spaces) is False
    
    def test_validate_name_delegates_to_validator(self):
        """Тест валидации имени делегирует валидатору."""
        # Валидное имя
        result = self.service.validate_name("Арагорн")
        assert result.is_valid is True
        
        # Невалидное имя
        result = self.service.validate_name("")
        assert result.is_valid is False
        assert result.error_message is not None
    
    def test_get_validation_rules_text(self):
        """Тест получения текста с правилами валидации."""
        rules_text = self.service.get_validation_rules_text()
        
        assert "Правила выбора имени:" in rules_text
        assert str(self.service.validator.MIN_LENGTH) in rules_text
        assert str(self.service.validator.MAX_LENGTH) in rules_text
        assert "буквы" in rules_text
        assert "дефисы" in rules_text
        assert "цифры" in rules_text
        assert "спецсимволы" in rules_text
    
    def test_character_saved_in_repository(self):
        """Тест сохранения персонажа в репозитории."""
        name = "Арторниус"
        character = self.service.create_character_with_name(name)
        
        # Проверяем, что персонаж сохранен в репозитории
        found_character = self.repo.find_by_id(character.id)
        assert found_character is not None
        assert found_character.name == name
        assert found_character.id == character.id
        
        # Проверяем поиск по имени
        found_by_name = self.repo.find_by_name(name)
        assert found_by_name is not None
        assert found_by_name.id == character.id
    
    def test_multiple_characters_creation(self):
        """Тест создания нескольких персонажей."""
        names = ["Арагорн", "Фродо", "Леголас", "Гэндальф"]
        characters = []
        
        for name in names:
            character = self.service.create_character_with_name(name)
            characters.append(character)
        
        # Проверяем, что все персонажи созданы с разными ID
        ids = [char.id for char in characters]
        assert len(set(ids)) == len(ids)  # Все ID уникальны
        
        # Проверяем, что все персонажи сохранены в репозитории
        all_characters = self.repo.find_all()
        assert len(all_characters) == len(names)
        
        # Проверяем, что имена уникальны
        saved_names = [char.name for char in all_characters]
        assert set(saved_names) == set(names)
    
    def test_character_timestamps(self):
        """Тест временных меток персонажа."""
        before_creation = datetime.now()
        
        name = "Боромир"
        character = self.service.create_character_with_name(name)
        
        after_creation = datetime.now()
        
        # Проверяем временные метки
        assert character.created_at is not None
        assert character.updated_at is not None
        assert before_creation <= character.created_at <= after_creation
        assert before_creation <= character.updated_at <= after_creation
    
    def test_service_with_empty_repository(self):
        """Тест работы сервиса с пустым репозиторием."""
        empty_file = self.temp_dir / "empty.json"
        empty_repo = JsonCharacterRepository(str(empty_file))
        service = NameInputService(empty_repo)
        
        # Все имена должны быть уникальны
        assert service.check_name_uniqueness("Любое имя") is True
        
        # Валидация работает
        result = service.validate_name("Арагорн")
        assert result.is_valid is True
