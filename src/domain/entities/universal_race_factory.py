# src/domain/entities/universal_race_factory.py
"""
Универсальная фабрика рас для D&D MUD.

Поддерживает новую структуру YAML с:
- Универсальными особенностями
- Наследованием бонусов и особенностей
- Модификациями
- Гибкой системой подрас
"""

import os
from typing import Dict, List, Optional, Any
from .race import Race
from .race_features import RaceDisplayFormatter, FeatureProcessor
from .race_data_parser import RaceDataParser, ParsedRaceData, ParsedSubraceData


class UniversalRaceFactory:
    """Универсальная фабрика рас с поддержкой модификаций."""
    
    _races_cache: Dict[str, Race] = {}
    _parser: Optional[RaceDataParser] = None
    _modifications_data: Dict = {}
    
    @classmethod
    def _get_parser(cls) -> RaceDataParser:
        """Возвращает экземпляр парсера."""
        if cls._parser is None:
            cls._parser = RaceDataParser()
        return cls._parser
    
    @classmethod
    def _load_modifications_data(cls) -> Dict:
        """Загружает данные о модификациях."""
        if not cls._modifications_data:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            mods_dir = os.path.join(project_root, 'data', 'mods')
            
            cls._modifications_data = {}
            
            # Ищем модификации в папке модов
            if os.path.exists(mods_dir):
                for mod_name in os.listdir(mods_dir):
                    mod_path = os.path.join(mods_dir, mod_name)
                    if os.path.isdir(mod_path):
                        race_mod_file = os.path.join(mod_path, 'races_mod.yaml')
                        if os.path.exists(race_mod_file):
                            try:
                                import yaml
                                with open(race_mod_file, 'r', encoding='utf-8') as file:
                                    mod_data = yaml.safe_load(file) or {}
                                    if 'modifications' in mod_data:
                                        cls._modifications_data[mod_name] = mod_data['modifications']
                            except Exception as e:
                                print(f"Предупреждение: Ошибка загрузки модификации {mod_name}: {e}")
        
        return cls._modifications_data
    
    @classmethod
    def _get_parsed_race_data(cls, race_key: str) -> Optional[ParsedRaceData]:
        """Возвращает распарсенные данные расы."""
        parser = cls._get_parser()
        return parser.get_race_data(race_key)
    
    @classmethod
    def _get_parsed_subrace_data(cls, race_key: str, subrace_key: str) -> Optional[ParsedSubraceData]:
        """Возвращает распарсенные данные подрасы."""
        parser = cls._get_parser()
        return parser.get_subrace_data(race_key, subrace_key)
    
    @classmethod
    def get_all_races(cls) -> List:
        """Возвращает список всех доступных рас."""
        parser = cls._get_parser()
        all_race_keys = parser.get_all_race_keys()
        races = []
        
        for race_key in all_race_keys:
            try:
                race = cls.create_race(race_key)
                races.append(race)
            except Exception as e:
                print(f"Предупреждение: Ошибка создания расы {race_key}: {e}")
        
        return races
    
    @classmethod
    def get_race_choices(cls) -> Dict[str, str]:
        """Возвращает словарь для меню выбора основных рас."""
        parser = cls._get_parser()
        all_data = parser.load_data()
        choices = {}
        choice_num = 1

        for race_key, race_data in all_data.items():
            if race_data.name:  # Только добавляем если имя не пустое
                choices[str(choice_num)] = race_data.name
                choice_num += 1

        return choices
    
    @classmethod
    def get_race_key_by_choice(cls, choice_num: int) -> Optional[str]:
        """Возвращает ключ расы по номеру выбора."""
        parser = cls._get_parser()
        all_data = parser.load_data()
        
        race_keys = list(all_data.keys())
        if 1 <= choice_num <= len(race_keys):
            return race_keys[choice_num - 1]

        return None
    
    @classmethod
    def get_subrace_choices(cls, race_key: str) -> Dict[str, str]:
        """Возвращает словарь для меню выбора подрас указанной расы."""
        race_data = cls._get_parsed_race_data(race_key)
        if not race_data:
            return {}
        
        choices = {}
        choice_num = 1

        # Проверяем, есть ли подрасы
        if not race_data.subraces:
            # Если подрас нет, добавляем основную расу как единственный вариант
            if race_data.name:
                choices[str(choice_num)] = race_data.name
                choice_num += 1
        else:
            # Если есть подрасы, добавляем только подрасы (без основной расы)
            for sub_key, sub_data in race_data.subraces.items():
                if sub_data.name:
                    choices[str(choice_num)] = sub_data.name
                    choice_num += 1

        return choices
    
    @classmethod
    def get_subrace_key_by_choice(cls, race_key: str, choice_num: int) -> Optional[str]:
        """Возвращает ключ подрасы по номеру выбора."""
        race_data = cls._get_parsed_race_data(race_key)
        if not race_data:
            return None

        # Проверяем, есть ли подрасы
        if not race_data.subraces:
            # Если подрас нет, choice_num == 1 означает основную расу
            return None if choice_num == 1 else None
        else:
            # Если есть подрасы, то choice_num напрямую соответствует индексу подрасы
            subrace_keys = list(race_data.subraces.keys())
            subrace_index = choice_num - 1  # Индексация с 0
            
            if 0 <= subrace_index < len(subrace_keys):
                return subrace_keys[subrace_index]

        return None
    
    @classmethod
    def get_formatted_race_info(cls, race_key: str, subrace_key: str = None) -> Dict[str, str]:
        """Возвращает отформатированную информацию о расе."""
        race_data = cls._get_parsed_race_data(race_key)
        if not race_data:
            return {}
        
        # Если указана подраса
        if subrace_key:
            subrace_data = cls._get_parsed_subrace_data(race_key, subrace_key)
            if not subrace_data:
                return {}
            
            # Собираем данные для подрасы (ТОЛЬКО уникальные)
            name = subrace_data.name
            description = subrace_data.description
            
            # Бонусы подрасы (только уникальные)
            bonuses = subrace_data.bonuses
            
            # Особенности подрасы (только уникальные)
            features = subrace_data.features
        else:
            # Основная раса - показываем ВСЕ бонусы и особенности
            name = race_data.name
            description = race_data.description
            bonuses = race_data.bonuses
            features = race_data.features
        
        # Форматируем через существующий форматировщик
        formatter = RaceDisplayFormatter()
        
        # Конвертируем в старый формат для совместимости
        legacy_data = {
            'name': name,
            'description': description,
            'bonuses': bonuses,
            'features': features
        }
        
        return formatter.format_race_info(legacy_data, subrace_key)
    
    @classmethod
    def create_race(cls, race_key: str, subrace_key: Optional[str] = None) -> Race:
        """Создает объект расы по ключу с поддержкой модификаций."""
        cache_key = f"{race_key}_{subrace_key}" if subrace_key else race_key

        if cache_key in cls._races_cache:
            return cls._races_cache[cache_key]

        # Получаем отформатированную информацию
        formatted_info = cls.get_formatted_race_info(race_key, subrace_key)
        
        if not formatted_info:
            raise ValueError(f"Раса '{race_key}' не найдена")
        
        # Создаем объект расы
        race = Race(
            name=formatted_info["name"],
            bonuses={},  # Бонусы теперь хранятся в особенностях
            description=formatted_info["description"],
            alternative_features={"features": formatted_info["features"]}
        )
        
        cls._races_cache[cache_key] = race
        return race
    
    @classmethod
    def clear_cache(cls) -> None:
        """Очищает кэш рас."""
        cls._races_cache.clear()
        cls._modifications_data.clear()
        if cls._parser:
            cls._parser.clear_cache()
            cls._parser = None
