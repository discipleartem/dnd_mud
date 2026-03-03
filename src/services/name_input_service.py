"""Сервис для ввода имени персонажа."""

from typing import Optional

from src.interfaces.character_repository import CharacterRepository
from src.models.entities.character import Character
from src.validators.name_validator import NameValidator, ValidationResult


class NameInputService:
    """Сервис для оркестрации процесса ввода имени персонажа.
    
    Применяемые паттерны:
    - Service (Сервис) — инкапсулирует бизнес-логику ввода имени
    - Dependency Injection (Внедрение зависимостей) — зависимости передаются через конструктор
    
    Применяемые принципы:
    - Single Responsibility — только процесс ввода и валидации имени
    - Explicit > Implicit — явная обработка всех случаев
    - Don't Repeat Yourself — валидация вынесена в NameValidator
    """
    
    def __init__(self, character_repo: CharacterRepository):
        """Инициализировать сервис с репозиторием персонажей.
        
        Args:
            character_repo: Репозиторий для работы с персонажами
        """
        self.character_repo = character_repo
        self.validator = NameValidator()
    
    def validate_name(self, name: str) -> ValidationResult:
        """Валидировать имя персонажа.
        
        Args:
            name: Имя для валидации
            
        Returns:
            ValidationResult с детальной информацией
        """
        return self.validator.validate(name)
    
    def check_name_uniqueness(self, name: str) -> bool:
        """Проверить уникальность имени.
        
        Args:
            name: Имя для проверки
            
        Returns:
            True если имя уникально, иначе False
        """
        existing_character = self.character_repo.find_by_name(name)
        return existing_character is None
    
    def create_character_with_name(self, name: str) -> Character:
        """Создать персонажа с указанным именем.
        
        Args:
            name: Имя персонажа
            
        Returns:
            Созданный персонаж
            
        Raises:
            ValueError: если имя не валидно или не уникально
        """
        # Валидация формата имени
        validation_result = self.validate_name(name)
        if not validation_result.is_valid:
            raise ValueError(validation_result.error_message)
        
        # Проверка уникальности имени
        if not self.check_name_uniqueness(name):
            raise ValueError(f"Персонаж с именем '{name}' уже существует")
        
        # Создание персонажа
        character = Character(name=name.strip())
        
        # Сохранение в репозиторий
        saved_character = self.character_repo.save(character)
        
        return saved_character
    
    def get_validation_rules_text(self) -> str:
        """Получить текст с правилами валидации имени.
        
        Returns:
            Строка с правилами для отображения пользователю
        """
        return (
            f"Правила выбора имени:\n"
            f"• Минимальная длина: {self.validator.MIN_LENGTH} символа\n"
            f"• Максимальная длина: {self.validator.MAX_LENGTH} символов\n"
            f"• Разрешены: буквы (включая кириллицу) и дефисы\n"
            f"• Запрещены: цифры и спецсимволы (кроме дефиса)\n"
            f"• Имя не может начинаться или заканчиваться дефисом\n"
            f"• Имя не может содержать двойные дефисы"
        )
