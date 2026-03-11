"""Use Case для управления сохранениями игр.

Следует Clean Architecture - бизнес-логика в слое Use Cases.
Оркестрация операций с сохранениями через репозиторий.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from src.interfaces.repositories.save_game_repository import (
    SaveGameRepository, 
    SaveGame, 
    RepositoryError
)
from src.entities.save_game_entity import SaveGameEntity


class SaveGameUseCase:
    """Use Case для управления сохранениями игр.
    
    Следует Clean Architecture - реализует бизнес-логику
    работы с сохранениями, инкапсулируя детали репозитория.
    """
    
    def __init__(self, repository: SaveGameRepository) -> None:
        """Инициализация Use Case.
        
        Args:
            repository: Репозиторий сохранений
        """
        self._repository = repository
    
    def create_new_save(
        self,
        character_name: str,
        character_level: int,
        character_class: str,
        character_data: Dict[str, Any],
        slot_number: int = 1,
        location: str = "Начало пути"
    ) -> SaveGame:
        """Создать новое сохранение.
        
        Args:
            character_name: Имя персонажа
            character_level: Уровень персонажа
            character_class: Класс персонажа
            character_data: Данные персонажа
            slot_number: Номер слота
            location: Текущая локация
            
        Returns:
            Созданное сохранение
            
        Raises:
            RepositoryError: Ошибка сохранения
            ValueError: Ошибка валидации данных
        """
        # Валидация входных данных
        if not character_name.strip():
            raise ValueError("Имя персонажа не может быть пустым")
        
        if character_level < 1 or character_level > 20:
            raise ValueError("Уровень должен быть от 1 до 20")
        
        if not character_class.strip():
            raise ValueError("Класс персонажа не может быть пустым")
        
        if slot_number < 1 or slot_number > 10:
            raise ValueError("Номер слота должен быть от 1 до 10")
        
        # Создаем сущность сохранения
        save_entity = SaveGameEntity(
            character_name=character_name,
            character_level=character_level,
            character_class=character_class,
            slot_number=slot_number,
            location=location,
            character_data=character_data
        )
        
        # Формируем данные для сохранения
        game_data = {
            "character": character_data,
            "game_state": {
                "current_location": location,
                "playtime_minutes": 0,
                "quests_completed": [],
                "current_objectives": []
            },
            "version": "1.0.0",
            "saved_at": datetime.now().isoformat()
        }
        
        # Создаем объект SaveGame для репозитория
        save_game = SaveGame(
            save_id=save_entity.save_id,
            character_name=save_entity.character_name,
            character_level=save_entity.character_level,
            character_class=save_entity.character_class,
            save_time=save_entity.save_time,
            slot_number=save_entity.slot_number,
            location=save_entity.location
        )
        
        # Сохраняем через репозиторий
        return self._repository.save(save_game, game_data)
    
    def load_game(self, save_id: str) -> Optional[Dict[str, Any]]:
        """Загрузить игру.
        
        Args:
            save_id: ID сохранения
            
        Returns:
            Данные игры или None если не найдено
            
        Raises:
            RepositoryError: Ошибка загрузки
        """
        return self._repository.load(save_id)
    
    def get_save_by_id(self, save_id: str) -> Optional[SaveGame]:
        """Получить сохранение по ID.
        
        Args:
            save_id: ID сохранения
            
        Returns:
            Сохранение или None если не найдено
            
        Raises:
            RepositoryError: Ошибка поиска
        """
        return self._repository.find_by_id(save_id)
    
    def get_save_by_slot(self, slot_number: int) -> Optional[SaveGame]:
        """Получить сохранение по номеру слота.
        
        Args:
            slot_number: Номер слота
            
        Returns:
            Сохранение или None если не найдено
            
        Raises:
            RepositoryError: Ошибка поиска
        """
        return self._repository.find_by_slot(slot_number)
    
    def get_all_saves(self) -> List[SaveGame]:
        """Получить все сохранения.
        
        Returns:
            Список всех сохранений
            
        Raises:
            RepositoryError: Ошибка получения
        """
        return self._repository.find_all()
    
    def delete_save(self, save_id: str) -> bool:
        """Удалить сохранение.
        
        Args:
            save_id: ID сохранения
            
        Returns:
            True если удалено успешно
            
        Raises:
            RepositoryError: Ошибка удаления
        """
        return self._repository.delete(save_id)
    
    def get_available_slots(self) -> List[int]:
        """Получить доступные слоты для сохранения.
        
        Returns:
            Список доступных номеров слотов (1-10)
            
        Raises:
            RepositoryError: Ошибка получения сохранений
        """
        all_saves = self.get_all_saves()
        used_slots = {save.slot_number for save in all_saves}
        
        # Возвращаем свободные слоты от 1 до 10
        available_slots = [i for i in range(1, 11) if i not in used_slots]
        return available_slots
    
    def quick_save(
        self,
        character_name: str,
        character_level: int,
        character_class: str,
        character_data: Dict[str, Any],
        location: str = "Начало пути"
    ) -> SaveGame:
        """Быстрое сохранение в первый доступный слот.
        
        Args:
            character_name: Имя персонажа
            character_level: Уровень персонажа
            character_class: Класс персонажа
            character_data: Данные персонажа
            location: Текущая локация
            
        Returns:
            Созданное сохранение
            
        Raises:
            RepositoryError: Ошибка сохранения
            ValueError: Нет доступных слотов
        """
        available_slots = self.get_available_slots()
        
        if not available_slots:
            raise ValueError("Нет доступных слотов для сохранения")
        
        # Используем первый доступный слот
        slot_number = min(available_slots)
        
        return self.create_new_save(
            character_name=character_name,
            character_level=character_level,
            character_class=character_class,
            character_data=character_data,
            slot_number=slot_number,
            location=location
        )
    
    def update_save(
        self,
        save_id: str,
        character_data: Dict[str, Any],
        location: Optional[str] = None,
        additional_playtime: int = 0
    ) -> bool:
        """Обновить существующее сохранение.
        
        Args:
            save_id: ID сохранения
            character_data: Обновленные данные персонажа
            location: Новая локация (опционально)
            additional_playtime: Дополнительное время игры (опционально)
            
        Returns:
            True если обновлено успешно
            
        Raises:
            RepositoryError: Ошибка обновления
        """
        # Загружаем текущее сохранение
        current_save = self.get_save_by_id(save_id)
        if not current_save:
            return False
        
        # Загружаем текущие данные игры
        current_game_data = self.load_game(save_id)
        if not current_game_data:
            return False
        
        # Обновляем данные
        current_game_data["character"] = character_data
        current_game_data["saved_at"] = datetime.now().isoformat()
        
        if location:
            current_game_data["game_state"]["current_location"] = location
            current_save.location = location
        
        if additional_playtime > 0:
            current_game_data["game_state"]["playtime_minutes"] += additional_playtime
        
        # Создаем обновленный объект SaveGame
        updated_save = SaveGame(
            save_id=current_save.save_id,
            character_name=current_save.character_name,
            character_level=current_save.character_level,
            character_class=current_save.character_class,
            save_time=datetime.now(),
            slot_number=current_save.slot_number,
            location=current_save.location,
            playtime_minutes=current_game_data["game_state"]["playtime_minutes"]
        )
        
        # Сохраняем обновленные данные
        self._repository.save(updated_save, current_game_data)
        
        return True
