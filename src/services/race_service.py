"""Реализация сервиса рас.

Следует Clean Architecture - бизнес-логика работы с расами.
Реализует интерфейс RaceServiceInterface.
"""

from src.entities.race_entity import Race, Subrace, RaceSelectionResult
from src.interfaces.services.race_service_interface import RaceServiceInterface
from typing import Dict, List, Optional
from pathlib import Path
import yaml

class RaceService(RaceServiceInterface):
    """Сервис работы с расами.

    Следует Clean Architecture - содержит бизнес-логику
    управления данными рас и применения бонусов.
    """

    def __init__(self, data_file: Optional[str] = None) -> None:
        """Инициализация сервиса.

        Args:
            data_file: Путь к файлу с данными рас
        """
        self._data_file = data_file or "data/races.yaml"
        self._races: Optional[List[Race]] = None

    def load_races(self) -> List[Race]:
        """Загрузить все расы из YAML файла.

        Returns:
            Список всех доступных рас
        """
        if self._races is not None:
            return self._races.copy()

        try:
            file_path = Path(self._data_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Файл с расами не найден: {self._data_file}")

            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)

            if not data or 'races' not in data:
                raise ValueError("Некорректная структура файла рас")

            self._races = []
            for race_key, race_data in data['races'].items():
                race = self._create_race_from_data(race_key, race_data)
                self._races.append(race)

            return self._races.copy()

        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки рас: {e}")

    def _create_race_from_data(self, race_key: str, race_data: Dict) -> Race:
        """Создать объект Race из YAML данных.

        Args:
            race_key: Ключ расы в YAML
            race_data: Данные расы из YAML

        Returns:
            Объект Race
        """
        subraces = None
        if 'subraces' in race_data and race_data['subraces']:
            subraces = []
            for subrace_key, subrace_data in race_data['subraces'].items():
                subrace = self._create_subrace_from_data(
                    race_key, subrace_key, subrace_data
                )
                subraces.append(subrace)

        return Race(
            name=race_data.get('name', race_key.title()),
            description=race_data.get('description', ''),
            speed=race_data.get('speed', 30),
            size=race_data.get('size', 'medium'),
            ability_bonuses=race_data.get('ability_bonuses', {}),
            traits=race_data.get('traits', []),
            languages=race_data.get('languages', []),
            subraces=subraces,
            allow_base_race_choice=race_data.get('allow_base_race_choice', False)
        )

    def _create_subrace_from_data(
        self, race_key: str, subrace_key: str, subrace_data: Dict[str, any]
    ) -> Subrace:
        """Создать объект Subrace из YAML данных.

        Args:
            race_key: Ключ родительской расы
            subrace_key: Ключ подрасы в YAML
            subrace_data: Данные подрасы из YAML

        Returns:
            Объект Subrace
        """
        return Subrace(
            name=subrace_data.get('name', subrace_key.replace('_', ' ').title()),
            parent_race=race_key,
            description=subrace_data.get('description', ''),
            ability_bonuses=subrace_data.get('ability_bonuses', {}),
            traits=subrace_data.get('traits', []),
            languages=subrace_data.get('languages', []),
            inherit_base_abilities=subrace_data.get('inherit_base_abilities', True),
            ability_bonuses_description=subrace_data.get('ability_bonuses_description', ''),
            features=subrace_data.get('features', [])
        )

    def get_race(self, name: str) -> Optional[Race]:
        """Получить расу по имени.

        Args:
            name: Название расы

        Returns:
            Раса или None если не найдена
        """
        if self._races is None:
            self.load_races()

        for race in self._races:
            if race.name.lower() == name.lower():
                return race
        return None

    def get_subrace(self, race_name: str, subrace_name: str) -> Optional[Subrace]:
        """Получить подрасу по имени расы и подрасы.

        Args:
            race_name: Название родительской расы
            subrace_name: Название подрасы

        Returns:
            Подраса или None если не найдена
        """
        race = self.get_race(race_name)
        if not race or not race.subraces:
            return None

        for subrace in race.subraces:
            if subrace.name.lower() == subrace_name.lower():
                return subrace
        return None

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
        result = abilities.copy()

        # Применяем бонусы расы
        for ability, bonus in race.ability_bonuses.items():
            result[ability] = result.get(ability, 0) + bonus

        # Применяем бонусы подрасы
        if subrace:
            for ability, bonus in subrace.ability_bonuses.items():
                result[ability] = result.get(ability, 0) + bonus

        return result

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
        # Валидация выбора
        if not self.validate_race_choice(race_name, subrace_name):
            raise ValueError(f"Некорректный выбор расы: {race_name}, {subrace_name}")

        # Получаем расу
        race = self.get_race(race_name)
        if not race:
            raise ValueError(f"Раса не найдена: {race_name}")

        # Получаем подрасу (если указана)
        subrace = None
        if subrace_name:
            subrace = self.get_subrace(race_name, subrace_name)
            if not subrace:
                raise ValueError(f"Подраса не найдена: {subrace_name}")

        # Базовые характеристики (по умолчанию 10 для всех)
        if base_abilities is None:
            base_abilities = {
                'strength': 10,
                'dexterity': 10,
                'constitution': 10,
                'intelligence': 10,
                'wisdom': 10,
                'charisma': 10
            }

        # Применяем бонусы
        final_abilities = self.apply_race_bonuses(base_abilities, race, subrace)

        return RaceSelectionResult(
            race_name=race_name,
            subrace_name=subrace_name,
            race=race,
            subrace=subrace,
            applied_bonuses=race.ability_bonuses.copy(),
            final_abilities=final_abilities
        )

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
        race = self.get_race(race_name)
        if not race:
            return False

        # Если указана подраса, проверяем её существование
        if subrace_name:
            subrace = self.get_subrace(race_name, subrace_name)
            if not subrace:
                return False

        # Проверяем, можно ли выбирать базовую расу
        if subrace_name is None and not race.allow_base_race_choice:
            return False

        return True
