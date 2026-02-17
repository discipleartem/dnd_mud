# src/domain/entities/race_data_parser.py
"""
Оптимизированный парсер данных рас из YAML.

Применяемые паттерны:
- Parser (Парсер) - преобразование YAML в структурированные данные
- Template Method (Шаблонный метод) - унифицированная обработка особенностей
- Builder (Строитель) - пошаговое построение данных расы

Применяемые принципы:
- Single Responsibility - каждая функция отвечает за свою часть парсинга
- DRY - избегаем дублирования кода
- Open/Closed - легко добавлять новые типы особенностей
"""

import yaml
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class ParsedRaceData:
    """Структурированные данные расы после парсинга."""
    key: str
    name: str
    description: str
    bonuses: Dict[str, int]
    features: List[Dict]
    subraces: Dict[str, 'ParsedSubraceData']
    templates: Dict[str, Any]


@dataclass
class ParsedSubraceData:
    """Структурированные данные подрасы после парсинга."""
    key: str
    name: str
    description: str
    bonuses: Dict[str, int]
    features: List[Dict]
    inherit_bonuses: bool
    inherit_features: bool


class RaceDataParser:
    """Оптимизированный парсер данных рас с поддержкой шаблонов."""
    
    def __init__(self):
        self._races_data: Optional[Dict] = None
        self._templates: Optional[Dict] = None
    
    def load_data(self) -> Dict[str, ParsedRaceData]:
        """Загружает и парсит все данные о расах."""
        if self._races_data is None:
            raw_data = self._load_raw_data()
            self._templates = raw_data.get('templates', {})
            races_raw = raw_data.get('races', {})
            
            self._races_data = {}
            for race_key, race_data in races_raw.items():
                parsed_race = self._parse_race(race_key, race_data)
                self._races_data[race_key] = parsed_race
        
        return self._races_data
    
    def _load_raw_data(self) -> Dict:
        """Загружает сырые данные из YAML файла."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        races_file = os.path.join(project_root, 'data', 'yaml', 'races', 'races.yaml')
        
        try:
            with open(races_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл с расами не найден: {races_file}")
    
    def _parse_race(self, race_key: str, race_data: Dict) -> ParsedRaceData:
        """Парсит данные основной расы."""
        # Базовые поля
        name = race_data.get('name', 'Безымянная раса')
        description = race_data.get('description', '')
        
        # Парсим бонусы
        bonuses = self._parse_bonuses(race_data.get('bonuses', {}))
        
        # Парсим особенности с применением шаблонов
        features = self._parse_features(race_data.get('features', []))
        
        # Создаём временный объект для передачи в _parse_subraces
        temp_race_data = ParsedRaceData(
            key=race_key,
            name=name,
            description=description,
            bonuses=bonuses,
            features=features,
            subraces={},  # Заполним ниже
            templates=self._templates
        )
        
        # Парсим подрасы
        subraces = self._parse_subraces(race_data.get('subraces', {}), temp_race_data)
        
        return ParsedRaceData(
            key=race_key,
            name=name,
            description=description,
            bonuses=bonuses,
            features=features,
            subraces=subraces,
            templates=self._templates
        )
    
    def _parse_subraces(self, subraces_raw: Dict, parent_race_data: ParsedRaceData) -> Dict[str, ParsedSubraceData]:
        """Парсит подрасы."""
        subraces = {}
        
        for subrace_key, subrace_data in subraces_raw.items():
            parsed_subrace = self._parse_subrace(subrace_key, subrace_data, parent_race_data)
            subraces[subrace_key] = parsed_subrace
        
        return subraces
    
    def _parse_subrace(self, subrace_key: str, subrace_data: Dict, parent_race_data: ParsedRaceData) -> ParsedSubraceData:
        """Парсит данные подрасы с вычислением уникальных особенностей."""
        name = subrace_data.get('name', 'Безымянная подраса')
        description = subrace_data.get('description', '')
        
        # Бонусы подрасы (всегда уникальные)
        bonuses = self._parse_bonuses(subrace_data.get('bonuses', {}))
        
        # Особенности подрасы - вычисляем только уникальные
        raw_features = subrace_data.get('features', [])
        parsed_features = self._parse_features(raw_features)
        
        # Вычисляем уникальные особенности (которых нет у родительской расы)
        unique_features = self._compute_unique_features(parsed_features, parent_race_data.features)
        
        # Параметры наследования
        inherit_bonuses = subrace_data.get('inherit_bonuses', True)
        inherit_features = subrace_data.get('inherit_features', True)
        
        return ParsedSubraceData(
            key=subrace_key,
            name=name,
            description=description,
            bonuses=bonuses,
            features=unique_features,
            inherit_bonuses=inherit_bonuses,
            inherit_features=inherit_features
        )
    
    def _compute_unique_features(self, subrace_features: List[Dict], parent_features: List[Dict]) -> List[Dict]:
        """Вычисляет уникальные особенности подрасы, которых нет у родительской расы."""
        unique_features = []
        
        for sub_feature in subrace_features:
            feature_type = sub_feature.get('type')
            feature_name = sub_feature.get('name')
            
            # Особая логика для владения оружием
            if feature_type == 'proficiency' and 'Владение оружием' in feature_name:
                # Для владения оружием вычисляем разницу списков
                sub_weapons = set(sub_feature.get('weapons', []))
                parent_weapons = set()
                
                # Ищем владение оружием у родительской расы
                for parent_feature in parent_features:
                    if (parent_feature.get('type') == 'proficiency' and 
                        'Владение оружием' in parent_feature.get('name', '')):
                        parent_weapons = set(parent_feature.get('weapons', []))
                        break
                
                # Вычисляем только дополнительное оружие
                additional_weapons = sub_weapons - parent_weapons
                
                # Если есть дополнительное оружие, добавляем особенность
                if additional_weapons:
                    unique_feature = sub_feature.copy()
                    unique_feature['weapons'] = list(additional_weapons)
                    unique_features.append(unique_feature)
                # Если дополнительного оружия нет, пропускаем эту особенность
            elif feature_type == 'language':
                # Для языков проверяем на дубликаты
                sub_languages = set(sub_feature.get('languages', []))
                parent_languages = set()
                
                # Ищем языки у родительской расы
                for parent_feature in parent_features:
                    if parent_feature.get('type') == 'language':
                        parent_languages = set(parent_feature.get('languages', []))
                        break
                
                # Проверяем, есть ли уникальные языки
                if sub_languages - parent_languages or 'choice' in str(sub_languages):
                    unique_feature = sub_feature.copy()
                    unique_features.append(unique_feature)
            else:
                # Для остальных особенностей проверяем по типу и имени
                is_unique = True
                for parent_feature in parent_features:
                    if (parent_feature.get('type') == feature_type and 
                        parent_feature.get('name') == feature_name):
                        is_unique = False
                        break
                
                if is_unique:
                    unique_features.append(sub_feature)
        
        return unique_features
    
    def _parse_bonuses(self, bonuses_raw: Dict) -> Dict[str, int]:
        """Парсит бонусы характеристик."""
        if not bonuses_raw:
            return {}
        
        # Фильтруем только валидные характеристики
        valid_attrs = {'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'}
        return {
            attr: int(bonus) 
            for attr, bonus in bonuses_raw.items() 
            if attr in valid_attrs and isinstance(bonus, (int, str))
        }
    
    def _parse_features(self, features_raw: List[Dict]) -> List[Dict]:
        """Парсит особенности с применением шаблонов."""
        if not features_raw:
            return []
        
        parsed_features = []
        
        for feature_raw in features_raw:
            # Если есть ссылка на шаблон
            if 'template' in feature_raw:
                feature = self._apply_template(feature_raw)
            else:
                feature = self._parse_single_feature(feature_raw)
            
            if feature:
                parsed_features.append(feature)
        
        return parsed_features
    
    def _apply_template(self, feature_data: Dict) -> Optional[Dict]:
        """Применяет шаблон к особенности."""
        template_name = feature_data.get('template')
        if not template_name or not self._templates:
            return None
        
        template = self._templates.get(template_name)
        if not template:
            return None
        
        # Копируем шаблон
        feature = template.copy()
        
        # Применяем переопределения из feature_data
        for key, value in feature_data.items():
            if key != 'template':
                feature[key] = value
        
        # Обрабатываем шаблонные строки
        feature = self._process_template_strings(feature)
        
        return feature
    
    def _process_template_strings(self, feature: Dict) -> Dict:
        """Обрабатывает шаблонные строки в особенностях."""
        for key, value in feature.items():
            if isinstance(value, str) and '{' in value:
                # Заменяем шаблонные переменные
                processed_value = value.format(**feature)
                feature[key] = processed_value
        
        return feature
    
    def _parse_single_feature(self, feature_raw: Dict) -> Dict:
        """Парсит одиночную особенность."""
        feature_type = feature_raw.get('type', 'unknown')
        
        # Валидация обязательных полей
        if not feature_raw.get('name'):
            feature_raw['name'] = 'Неизвестная особенность'
        
        if not feature_raw.get('description'):
            feature_raw['description'] = 'Описание отсутствует'
        
        # Специфичная обработка для разных типов
        if feature_type == 'proficiency':
            return self._parse_proficiency_feature(feature_raw)
        elif feature_type == 'spell':
            return self._parse_spell_feature(feature_raw)
        elif feature_type == 'language':
            return self._parse_language_feature(feature_raw)
        elif feature_type in ['ability_choice', 'skill_choice', 'feat_choice']:
            return self._parse_choice_feature(feature_raw)
        else:
            return self._parse_trait_feature(feature_raw)
    
    def _parse_proficiency_feature(self, feature: Dict) -> Dict:
        """Парсит особенности владения."""
        # Нормализуем список владений
        if 'weapons' in feature:
            weapons = feature['weapons']
            if isinstance(weapons, str):
                feature['weapons'] = [weapons]
            elif not isinstance(weapons, list):
                feature['weapons'] = []
        
        if 'skills' in feature:
            skills = feature['skills']
            if isinstance(skills, str):
                feature['skills'] = [skills]
            elif not isinstance(skills, list):
                feature['skills'] = []
        
        return feature
    
    def _parse_spell_feature(self, feature: Dict) -> Dict:
        """Парсит особенности заклинаний."""
        if 'spells' in feature:
            spells = feature['spells']
            if isinstance(spells, str):
                feature['spells'] = [spells]
            elif not isinstance(spells, list):
                feature['spells'] = []
        
        return feature
    
    def _parse_language_feature(self, feature: Dict) -> Dict:
        """Парсит особенности языков."""
        if 'languages' in feature:
            languages = feature['languages']
            if isinstance(languages, str):
                feature['languages'] = [languages]
            elif not isinstance(languages, list):
                feature['languages'] = []
        
        return feature
    
    def _parse_choice_feature(self, feature: Dict) -> Dict:
        """Парсит особенности с выбором."""
        # Валидация параметров выбора
        if 'max_choices' not in feature:
            feature['max_choices'] = 1
        
        if 'bonus_value' not in feature and feature.get('type') == 'ability_choice':
            feature['bonus_value'] = 1
        
        return feature
    
    def _parse_trait_feature(self, feature: Dict) -> Dict:
        """Парсит черты характера."""
        return feature
    
    def get_race_data(self, race_key: str) -> Optional[ParsedRaceData]:
        """Возвращает распарсенные данные расы."""
        all_data = self.load_data()
        return all_data.get(race_key)
    
    def get_subrace_data(self, race_key: str, subrace_key: str) -> Optional[ParsedSubraceData]:
        """Возвращает распарсенные данные подрасы."""
        race_data = self.get_race_data(race_key)
        if not race_data:
            return None
        
        return race_data.subraces.get(subrace_key)
    
    def get_all_race_keys(self) -> List[str]:
        """Возвращает список всех ключей рас."""
        all_data = self.load_data()
        return list(all_data.keys())
    
    def clear_cache(self) -> None:
        """Очищает кэш парсера."""
        self._races_data = None
        self._templates = None
