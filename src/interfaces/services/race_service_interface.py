"""Интерфейс сервиса рас.

Следует Clean Architecture - определяет контракт для работы с расами.
Не содержит реализации, только абстрактные методы.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from src.entities.race_entity import Race, Subrace, RaceSelectionResult


class RaceServiceInterface(ABC):
    """Интерфейс сервиса работы с расами.

    Следует Clean Architecture - определяет контракт для
    бизнес-логики работы с расами без конкретной реализации.
    """

    @abstractmethod
    def load_races(self) -> List[Race]:
        """Загрузить все расы из источника данных.

        Returns:
            Список всех доступных рас
        """
        pass

    @abstractmethod
    def get_race(self, name: str) -> Optional[Race]:
        """Получить расу по имени.

        Args:
            name: Название расы

        Returns:
            Раса или None если не найдена
        """
        pass

    @abstractmethod
    def get_subrace(self, race_name: str, subrace_name: str) -> Optional[Subrace]:
        """Получить подрасу по имени расы и подрасы.

        Args:
            race_name: Название родительской расы
            subrace_name: Название подрасы

        Returns:
            Подраса или None если не найдена
        """
        pass

    @abstractmethod
    def apply_race_bonuses(
        self, 
        abilities: Dict[str, int], 
        race: Race, 
        subrace: Optional[Subrace] = None
    ) -> Dict[str, int]:
        """Применить расовые бонусы к характеристикам.

        Args:
            abilities: Базовые характеристики персонажа
            race: Выбранная раса
            subrace: Выбранная подраса (опционально)

        Returns:
            Характеристики с применёнными бонусами
        """
        pass

    @abstractmethod
    def create_race_selection(
        self,
        race_name: str,
        subrace_name: Optional[str] = None,
        base_abilities: Optional[Dict[str, int]] = None
    ) -> RaceSelectionResult:
        """Создать результат выбора расы с применёнными бонусами.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы (опционально)
            base_abilities: Базовые характеристики (опционально)

        Returns:
            Результат выбора расы с бонусами

        Raises:
            ValueError: Если раса или подраса не найдены
        """
        pass

    @abstractmethod
    def validate_race_choice(
        self, 
        race_name: str, 
        subrace_name: Optional[str] = None
    ) -> bool:
        """Валидировать выбор расы и подрасы.

        Args:
            race_name: Название расы
            subrace_name: Название подрасы (опционально)

        Returns:
            True если выбор валиден, иначе False
        """
        pass
