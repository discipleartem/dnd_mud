"""Контроллер персонажей.

Адаптер интерфейса, который преобразует данные между UI и Use Cases.
Следует принципам чистой архитектуры.
"""

from typing import Dict, List, Optional

from src.use_cases.character_creation import (
    CreateCharacterUseCase, CreateCharacterRequest, CreateCharacterResponse,
    GetRaceChoicesUseCase, GetClassChoicesUseCase
)


class CharacterController:
    """Контроллер для работы с персонажами.
    
    Является Interface Adapter, преобразуя данные
    между UI слоем и Use Cases.
    """
    
    def __init__(self, 
                 create_character_use_case: CreateCharacterUseCase,
                 get_race_choices_use_case: GetRaceChoicesUseCase,
                 get_class_choices_use_case: GetClassChoicesUseCase) -> None:
        """Инициализировать контроллер с Use Cases."""
        self._create_character_use_case = create_character_use_case
        self._get_race_choices_use_case = get_race_choices_use_case
        self._get_class_choices_use_case = get_class_choices_use_case
    
    def create_character(self, name: str, race_id: str, class_id: str, 
                        abilities: Optional[Dict[str, int]] = None) -> CreateCharacterResponse:
        """Создать персонажа."""
        request = CreateCharacterRequest(
            name=name,
            race_id=race_id,
            class_id=class_id,
            abilities=abilities
        )
        
        return self._create_character_use_case.execute(request)
    
    def get_race_choices(self) -> List[tuple]:
        """Получить список рас для выбора."""
        return self._get_race_choices_use_case.execute()
    
    def get_class_choices(self) -> List[tuple]:
        """Получить список классов для выбора."""
        return self._get_class_choices_use_case.execute()
    
    def get_race_details(self, race_id: str) -> Optional[Dict]:
        """Получить информацию о расе."""
        # Делегируем в Use Case через репозиторий
        return self._create_character_use_case._race_repository.get_race_details(race_id)
    
    def get_subrace_choices(self, race_id: str) -> List[tuple]:
        """Получить подрасы."""
        return self._create_character_use_case._race_repository.get_subrace_choices(race_id)
    
    def get_subrace_details(self, race_id: str, subrace_id: str) -> Optional[Dict]:
        """Получить информацию о подрасе."""
        return self._create_character_use_case._race_repository.get_subrace_details(race_id, subrace_id)