"""
Сервис создания персонажей.

Простой и понятный сервис following KISS principle.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

from src.models.data import Character, CharacterData, CharacterRace, CharacterClass
from src.data.repositories import RaceRepository, ClassRepository
from src.services.ability_generator import AbilityGenerator


@dataclass
class CreateCharacterResponse:
    """Результат создания персонажа."""
    character: Optional[Character] = None
    success: bool = False
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class CharacterService:
    """Сервис для создания персонажей."""
    
    def __init__(self):
        self.race_repo = RaceRepository()
        self.class_repo = ClassRepository()
        self.ability_generator = AbilityGenerator()
    
    def get_race_choices(self) -> List[tuple]:
        """Получить список рас для выбора."""
        return self.race_repo.get_race_choices()
    
    def get_class_choices(self) -> List[tuple]:
        """Получить список классов для выбора."""
        return self.class_repo.get_class_choices()
    
    def get_race_details(self, race_id: str) -> Optional[Dict]:
        """Получить информацию о расе."""
        return self.race_repo.get_race_details(race_id)
    
    def get_subrace_choices(self, race_id: str) -> List[tuple]:
        """Получить подрасы."""
        return self.race_repo.get_subrace_choices(race_id)
    
    def get_subrace_details(self, race_id: str, subrace_id: str) -> Optional[Dict]:
        """Получить информацию о подрасе."""
        return self.race_repo.get_subrace_details(race_id, subrace_id)
    
    def create_character(self, name: str, race_id: str, class_id: str, 
                        abilities: Optional[Dict[str, int]] = None) -> CreateCharacterResponse:
        """Создать персонажа."""
        try:
            # Валидация
            if not name.strip():
                return CreateCharacterResponse(success=False, errors=["Имя не может быть пустым"])
            
            # Преобразование строк в enum
            try:
                race_enum = CharacterRace(race_id.split(":")[0])
            except ValueError:
                return CreateCharacterResponse(success=False, errors=[f"Неизвестная раса: {race_id}"])
            
            try:
                class_enum = CharacterClass(class_id)
            except ValueError:
                return CreateCharacterResponse(success=False, errors=[f"Неизвестный класс: {class_id}"])
            
            # Получаем данные расы и класса
            race_data = self.race_repo.get_race_details(race_enum.value)
            class_data = self.class_repo.get_class_details(class_enum.value)
            
            if not race_data:
                return CreateCharacterResponse(success=False, errors=["Данные расы не найдены"])
            if not class_data:
                return CreateCharacterResponse(success=False, errors=["Данные класса не найдены"])
            
            # Создаем данные персонажа
            character_data = CharacterData(
                name=name.strip(),
                race=race_enum,
                character_class=class_enum,
                level=1
            )
            
            # Применяем базовые характеристики (уже с расовыми бонусами)
            if abilities:
                for ability, value in abilities.items():
                    if hasattr(character_data, ability):
                        setattr(character_data, ability, value)
            
            # Применяем остальные параметры расы (не бонусы, т.к. уже применены)
            self._apply_race_params(character_data, race_data, race_id)
            
            # Создаем персонажа
            character = Character(character_data)
            
            return CreateCharacterResponse(
                success=True,
                character=character,
                errors=[]
            )
            
        except Exception as e:
            return CreateCharacterResponse(
                success=False,
                errors=[f"Ошибка при создании персонажа: {str(e)}"]
            )
    
    def _apply_race_params(self, data: CharacterData, race_data: Dict, race_id: str) -> None:
        """Применить параметры расы (кроме бонусов характеристик)."""
        # Применяем остальные параметры расы
        data.size = race_data.get("size", "MEDIUM")
        data.speed = race_data.get("speed", 30)
        data.languages = race_data.get("languages", [])
    
    def validate_abilities(self, abilities: Dict[str, int]) -> tuple[bool, List[str]]:
        """Валидировать характеристики."""
        errors = []
        warnings = []
        
        # Проверка диапазона значений
        for ability, value in abilities.items():
            if not isinstance(value, int) or value < 1 or value > 20:
                errors.append(f"Неверное значение для {ability}: {value} (должно быть 1-20)")
        
        # Проверка суммы значений
        total_sum = sum(abilities.values())
        if total_sum < 60:
            warnings.append(f"Низкая сумма характеристик: {total_sum} (средняя ~72)")
        elif total_sum > 85:
            warnings.append(f"Высокая сумма характеристик: {total_sum} (средняя ~72)")
        
        # Проверка на экстремальные значения
        low_count = sum(1 for v in abilities.values() if v <= 8)
        high_count = sum(1 for v in abilities.values() if v >= 15)
        
        if low_count >= 3:
            warnings.append(f"Много низких характеристик (≤8): {low_count}")
        
        if high_count >= 3:
            warnings.append(f"Много высоких характеристик (≥15): {high_count}")
        
        # Проверка на соответствие Point Buy (если все значения в диапазоне 8-15)
        if all(8 <= v <= 15 for v in abilities.values()):
            point_buy_cost = sum(self.ability_generator.POINT_BUY_COSTS.get(v, 0) for v in abilities.values())
            if point_buy_cost > 27:
                errors.append(f"Превышен лимит Point Buy: {point_buy_cost} очков (максимум 27)")
            elif point_buy_cost < 20:
                warnings.append(f"Низкая стоимость Point Buy: {point_buy_cost} очков (рекомендуется 27)")
        
        # Объединяем ошибки и предупреждения
        all_messages = errors + warnings
        
        if errors:
            return False, all_messages
        elif warnings:
            return True, all_messages
        else:
            return True, []
