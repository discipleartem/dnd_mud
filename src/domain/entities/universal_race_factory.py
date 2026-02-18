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
        """Загружает данные о модификациях, учитывая только активные моды."""
        if not cls._modifications_data:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            mods_dir = os.path.join(project_root, 'data', 'mods')
            
            cls._modifications_data = {}
            
            # Импортируем GameConfig для проверки активных модов
            try:
                from ..services.game_config import game_config
                active_mods = game_config.get_active_mods_info()
                active_mod_names = [mod.folder_name for mod in active_mods]
            except Exception:
                # Если не удалось загрузить конфигурацию, считаем все моды неактивными
                active_mod_names = []
            
            # Ищем модификации в папке модов
            if os.path.exists(mods_dir):
                for mod_name in os.listdir(mods_dir):
                    # Загружаем только активные моды
                    if mod_name not in active_mod_names:
                        continue
                        
                    mod_path = os.path.join(mods_dir, mod_name)
                    if os.path.isdir(mod_path):
                        race_mod_file = os.path.join(mod_path, 'races_mod.yaml')
                        if os.path.exists(race_mod_file):
                            try:
                                import yaml
                                with open(race_mod_file, 'r', encoding='utf-8') as file:
                                    mod_data = yaml.safe_load(file) or {}
                                    # Сохраняем весь файл как модификацию
                                    cls._modifications_data[mod_name] = mod_data
                            except Exception as e:
                                print(f"Предупреждение: Ошибка загрузки модификации {mod_name}: {e}")
        
        return cls._modifications_data
    
    @classmethod
    def _apply_modifications(cls, race_data: ParsedRaceData) -> ParsedRaceData:
        """Применяет модификации к данным расы."""
        modifications = cls._load_modifications_data()
        
        if not modifications:
            return race_data
        
        # Создаем копию данных для модификации
        modified_data = ParsedRaceData(
            key=race_data.key,
            name=race_data.name,
            description=race_data.description,
            short_description=race_data.short_description,
            size=race_data.size,
            speed=race_data.speed,
            age=race_data.age.copy(),
            languages=race_data.languages.copy(),
            bonuses=race_data.bonuses.copy(),
            features=race_data.features.copy(),
            subraces=race_data.subraces.copy(),
            templates=race_data.templates
        )
        
        # Применяем модификации от всех модов
        for mod_name, mod_data in modifications.items():
            if 'modifications' in mod_data and race_data.key in mod_data['modifications']:
                changes = mod_data['modifications'][race_data.key]
                
                # Применяем бонусы
                if 'bonuses' in changes:
                    for attr, bonus in changes['bonuses'].items():
                        modified_data.bonuses[attr] = modified_data.bonuses.get(attr, 0) + bonus
                
                # Применяем особенности
                if 'features' in changes:
                    modified_data.features.extend(changes['features'])
                
                # Применяем подрасы
                if 'subraces' in changes:
                    for subrace_key, subrace_changes in changes['subraces'].items():
                        if subrace_key in modified_data.subraces:
                            # Обновляем существующую подрасу
                            existing_subrace = modified_data.subraces[subrace_key]
                            if 'bonuses' in subrace_changes:
                                for attr, bonus in subrace_changes['bonuses'].items():
                                    existing_subrace.bonuses[attr] = existing_subrace.bonuses.get(attr, 0) + bonus
                            if 'features' in subrace_changes:
                                existing_subrace.features.extend(subrace_changes['features'])
                        else:
                            # Добавляем новую подрасу
                            # Создаем базовую подрасу на основе основной расы
                            new_subrace = ParsedSubraceData(
                                key=subrace_key,
                                name=subrace_changes.get('name', f'Новая подраса {subrace_key}'),
                                description=subrace_changes.get('description', ''),
                                short_description=subrace_changes.get('short_description', ''),
                                bonuses=subrace_changes.get('bonuses', {}),
                                features=subrace_changes.get('features', []),
                                inherit_bonuses=subrace_changes.get('inherit_bonuses', True),
                                inherit_features=subrace_changes.get('inherit_features', True)
                            )
                            modified_data.subraces[subrace_key] = new_subrace
        
        return modified_data
    
    @classmethod
    def _get_parsed_race_data(cls, race_key: str) -> Optional[ParsedRaceData]:
        """Возвращает распарсенные данные расы с примененными модификациями."""
        parser = cls._get_parser()
        base_data = parser.get_race_data(race_key)
        
        if not base_data:
            return None
        
        # Применяем модификации
        return cls._apply_modifications(base_data)
    
    @classmethod
    def _get_parsed_subrace_data(cls, race_key: str, subrace_key: str) -> Optional[ParsedSubraceData]:
        """Возвращает распарсенные данные подрасы с примененными модификациями."""
        # Сначала получаем модифицированные данные основной расы
        modified_race_data = cls._get_parsed_race_data(race_key)
        
        if not modified_race_data or subrace_key not in modified_race_data.subraces:
            return None
        
        return modified_race_data.subraces[subrace_key]
    
    @classmethod
    def get_race_choices(cls) -> Dict[str, str]:
        """Возвращает словарь для меню выбора основных рас."""
        parser = cls._get_parser()
        all_data = parser.load_data()
        choices = {}
        choice_num = 1

        for race_key, race_data in all_data.items():
            # Получаем модифицированные данные
            modified_data = cls._get_parsed_race_data(race_key)
            if modified_data and modified_data.name:  # Только добавляем если имя не пустое
                choices[str(choice_num)] = modified_data.name
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
        
        # Используем форматировщик для работы с новыми структурами
        formatter = RaceDisplayFormatter()
        
        # Если указана подраса
        if subrace_key:
            return formatter.format_race_info(race_data, subrace_key)
        else:
            # Основная раса
            return formatter.format_race_info(race_data)
    
    @classmethod
    def get_subrace_only_info(cls, race_key: str, subrace_key: str) -> Dict[str, str]:
        """Возвращает информацию только о подрасе (без унаследованных бонусов и особенностей)."""
        race_data = cls._get_parsed_race_data(race_key)
        if not race_data or subrace_key not in race_data.subraces:
            return {}
        
        subrace_data = race_data.subraces[subrace_key]
        
        # Словарь с русскими названиями характеристик
        russian_names = {
            "strength": "Сила",
            "dexterity": "Ловкость",
            "constitution": "Телосложение",
            "intelligence": "Интеллект",
            "wisdom": "Мудрость",
            "charisma": "Харизма"
        }
        
        name = subrace_data.name
        description = subrace_data.description
        short_description = subrace_data.short_description
        
        # Форматируем только бонусы подрасы (без унаследованных)
        bonus_parts = []
        for attr_name, bonus in subrace_data.bonuses.items():
            if bonus > 0:
                russian_name = russian_names.get(attr_name, attr_name.title())
                bonus_str = f"+{bonus}"
                bonus_parts.append(f"\t🎯 {russian_name}: {bonus_str}")
        
        bonuses_str = "\n".join(bonus_parts) if bonus_parts else ""
        
        # Форматируем только особенности подрасы (без унаследованных)
        formatter = RaceDisplayFormatter()
        features_list = formatter.processor.format_features(subrace_data.features)
        features_str = "\n".join(feature for feature in features_list) if features_list else ""
        
        return {
            "name": name,
            "description": description,
            "short_description": short_description,
            "bonuses": bonuses_str,
            "features": features_str
        }
    
    @classmethod
    def create_race(cls, race_key: str, subrace_key: Optional[str] = None) -> Race:
        """Создает объект расы по ключу с поддержкой модификаций."""
        cache_key = f"{race_key}_{subrace_key}" if subrace_key else race_key

        if cache_key in cls._races_cache:
            return cls._races_cache[cache_key]

        # Получаем распарсенные данные
        if subrace_key:
            race_data = cls._get_parsed_race_data(race_key)
            subrace_data = cls._get_parsed_subrace_data(race_key, subrace_key)
            
            if not race_data or not subrace_data:
                raise ValueError(f"Подраса '{subrace_key}' для расы '{race_key}' не найдена")
            
            # Вычисляем эффективные бонусы
            effective_bonuses = {}
            if subrace_data.inherit_bonuses:
                effective_bonuses.update(race_data.bonuses)
            effective_bonuses.update(subrace_data.bonuses)
            
            # Вычисляем все особенности
            all_features = []
            if subrace_data.inherit_features:
                all_features.extend(race_data.features)
            all_features.extend(subrace_data.features)
            
            race = Race(
                name=subrace_data.name,
                bonuses=effective_bonuses,
                description=subrace_data.description,
                short_description=subrace_data.short_description,
                size=race_data.size,  # Наследуем от основной расы
                speed=race_data.speed,  # Наследуем от основной расы
                age=race_data.age,  # Наследуем от основной расы
                languages=race_data.languages,  # Наследуем от основной расы
                features=all_features,
                inherit_bonuses=subrace_data.inherit_bonuses,
                inherit_features=subrace_data.inherit_features
            )
        else:
            race_data = cls._get_parsed_race_data(race_key)
            if not race_data:
                raise ValueError(f"Раса '{race_key}' не найдена")
            
            race = Race(
                name=race_data.name,
                bonuses=race_data.bonuses,
                description=race_data.description,
                short_description=race_data.short_description,
                size=race_data.size,
                speed=race_data.speed,
                age=race_data.age,
                languages=race_data.languages,
                features=race_data.features
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
