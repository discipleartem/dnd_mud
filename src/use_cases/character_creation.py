"""Use Case для создания персонажа.

Реализует сценарий использования создания персонажа
согласно чистой архитектуре.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from src.entities.character import Character, CharacterData, CharacterRace, CharacterClass
from src.interfaces.repositories import RaceRepositoryInterface, ClassRepositoryInterface, CharacterRepositoryInterface


@dataclass
class CreateCharacterRequest:
    """Запрос на создание персонажа."""
    name: str
    race_id: str
    class_id: str
    abilities: Optional[Dict[str, int]] = None


@dataclass
class CreateCharacterResponse:
    """Результат создания персонажа."""
    character: Optional[Character] = None
    success: bool = False
    errors: List[str] = None
    
    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


class CreateCharacterUseCase:
    """Use Case для создания персонажа.
    
    Реализует бизнес-логику создания персонажа,
    завися только от абстракций.
    """
    
    def __init__(self, 
                 race_repository: RaceRepositoryInterface,
                 class_repository: ClassRepositoryInterface,
                 character_repository: CharacterRepositoryInterface) -> None:
        """Инициализировать Use Case с зависимостями."""
        self._race_repository = race_repository
        self._class_repository = class_repository
        self._character_repository = character_repository
    
    def execute(self, request: CreateCharacterRequest) -> CreateCharacterResponse:
        """Выполнить создание персонажа."""
        try:
            # Валидация имени
            if not request.name.strip():
                return CreateCharacterResponse(
                    success=False, 
                    errors=["Имя не может быть пустым"]
                )
            
            # Валидация и преобразование расы
            try:
                race_enum = CharacterRace(request.race_id.split(":")[0])
            except ValueError:
                return CreateCharacterResponse(
                    success=False, 
                    errors=[f"Неизвестная раса: {request.race_id}"]
                )
            
            # Валидация и преобразование класса
            try:
                class_enum = CharacterClass(request.class_id)
            except ValueError:
                return CreateCharacterResponse(
                    success=False, 
                    errors=[f"Неизвестный класс: {request.class_id}"]
                )
            
            # Получение данных расы и класса
            race_data = self._race_repository.get_race_details(race_enum.value)
            class_data = self._class_repository.get_class_details(class_enum.value)
            
            if not race_data:
                return CreateCharacterResponse(
                    success=False, 
                    errors=["Данные расы не найдены"]
                )
            
            if not class_data:
                return CreateCharacterResponse(
                    success=False, 
                    errors=["Данные класса не найдены"]
                )
            
            # Создание данных персонажа
            character_data = CharacterData(
                name=request.name.strip(),
                race=race_enum,
                character_class=class_enum,
                level=1
            )
            
            # Применение характеристик
            if request.abilities:
                self._apply_abilities(character_data, request.abilities)
            
            # Применение параметров расы
            self._apply_race_params(character_data, race_data, request.race_id)
            
            # Создание персонажа
            character = Character(character_data)
            
            # Сохранение персонажа
            saved_character = self._character_repository.save(character)
            
            return CreateCharacterResponse(
                success=True,
                character=saved_character,
                errors=[]
            )
            
        except Exception as e:
            return CreateCharacterResponse(
                success=False,
                errors=[f"Ошибка при создании персонажа: {str(e)}"]
            )
    
    def _apply_abilities(self, data: CharacterData, abilities: Dict[str, int]) -> None:
        """Применить характеристики к данным персонажа."""
        for ability, value in abilities.items():
            if hasattr(data, ability):
                setattr(data, ability, value)
    
    def _apply_race_params(self, data: CharacterData, race_data: Dict, race_id: str) -> None:
        """Применить параметры расы (кроме бонусов характеристик)."""
        data.size = race_data.get("size", "MEDIUM")
        data.speed = race_data.get("speed", 30)
        data.languages = race_data.get("languages", [])


class GetRaceChoicesUseCase:
    """Use Case для получения списка рас."""
    
    def __init__(self, race_repository: RaceRepositoryInterface) -> None:
        self._race_repository = race_repository
    
    def execute(self) -> List[tuple]:
        """Получить список рас для выбора."""
        return self._race_repository.get_race_choices()


class GetClassChoicesUseCase:
    """Use Case для получения списка классов."""
    
    def __init__(self, class_repository: ClassRepositoryInterface) -> None:
        self._class_repository = class_repository
    
    def execute(self) -> List[tuple]:
        """Получить список классов для выбора."""
        return self._class_repository.get_class_choices()