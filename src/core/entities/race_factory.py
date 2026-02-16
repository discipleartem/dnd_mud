# src/core/entities/race_factory.py
from typing import Dict, List, Optional
from .race import Race
from ..localization.loader import localization


class RaceFactory:
    """Фабрика для создания рас из YAML конфигурации."""
    
    _races_cache: Dict[str, Race] = {}
    
    @classmethod
    def create_race(cls, race_key: str, subrace_key: Optional[str] = None) -> Race:
        """Создает объект расы по ключу.
        
        Args:
            race_key: Ключ расы (human, elf, half_orc)
            subrace_key: Ключ подрасы (high_elf, wood_elf)
            
        Returns:
            Объект расы
        """
        cache_key = f"{race_key}_{subrace_key}" if subrace_key else race_key
        
        if cache_key in cls._races_cache:
            return cls._races_cache[cache_key]
        
        races_data = localization.get_all_races()
        
        if race_key not in races_data:
            raise ValueError(f"Раса '{race_key}' не найдена")
        
        race_data = races_data[race_key]
        
        # Если запрошена подраса
        if subrace_key and 'subraces' in race_data and subrace_key in race_data['subraces']:
            subrace_data = race_data['subraces'][subrace_key]
            race = Race(
                name=subrace_data['name'],
                bonuses=subrace_data.get('bonuses', {}),
                description=subrace_data.get('description', '')
            )
        else:
            race = Race(
                name=race_data['name'],
                bonuses=race_data.get('bonuses', {}),
                description=race_data.get('description', '')
            )
            
            # Добавляем подрасы если они есть
            if 'subraces' in race_data:
                for sub_key, sub_data in race_data['subraces'].items():
                    subrace = Race(
                        name=sub_data['name'],
                        bonuses=sub_data.get('bonuses', {}),
                        description=sub_data.get('description', '')
                    )
                    race.add_subrace(subrace)
        
        cls._races_cache[cache_key] = race
        return race
    
    @classmethod
    def get_all_races(cls) -> List[Race]:
        """Возвращает список всех доступных рас."""
        races_data = localization.get_all_races()
        races = []
        
        for race_key in races_data:
            races.append(cls.create_race(race_key))
            
        return races
    
    @classmethod
    def get_race_choices(cls) -> Dict[str, str]:
        """Возвращает словарь для меню выбора рас."""
        races_data = localization.get_all_races()
        choices = {}
        choice_num = 1
        
        for race_key, race_data in races_data.items():
            choices[str(choice_num)] = race_data['name']
            choice_num += 1
            
            # Добавляем подрасы
            if 'subraces' in race_data and race_data['subraces']:
                for sub_key, sub_data in race_data['subraces'].items():
                    choices[str(choice_num)] = sub_data['name']
                    choice_num += 1
        
        return choices
    
    @classmethod
    def clear_cache(cls) -> None:
        """Очищает кэш рас."""
        cls._races_cache.clear()
