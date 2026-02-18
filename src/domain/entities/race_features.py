# src/domain/entities/race_features.py
"""
Универсальная система обработки особенностей рас для D&D MUD.

Поддерживает различные типы особенностей:
- ability_choice: Выбор характеристик
- skill_choice: Выбор навыков  
- feat_choice: Выбор черт
- trait: Пассивные черты
- proficiency: Владения
- spell: Заклинания
- language: Языки
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..value_objects.attributes import StandardAttributes


@dataclass
class FeatureProcessor:
    """Универсальный процессор особенностей рас."""
    
    @staticmethod
    def format_bonuses(bonuses: Dict[str, int], features: List[Dict] = None) -> str:
        """Форматирует бонусы к характеристикам с учетом особенностей.
        
        Args:
            bonuses: Базовые бонусы расы
            features: Список особенностей расы
            
        Returns:
            Отформатированная строка с бонусами
        """
        # Словарь с русскими названиями характеристик
        russian_names = {
            "strength": "Сила",
            "dexterity": "Ловкость",
            "constitution": "Телосложение",
            "intelligence": "Интеллект",
            "wisdom": "Мудрость",
            "charisma": "Харизма"
        }
        
        if not bonuses and not features:
            return "Нет бонусов"
        
        result_parts = []
        
        # Обрабатываем базовые бонусы
        if bonuses:
            for attr_name, bonus in bonuses.items():
                if bonus > 0:
                    # Используем словарь с русскими названиями
                    russian_name = russian_names.get(attr_name, attr_name.title())
                    bonus_str = f"+{bonus}"
                    result_parts.append(f"\t🎯 {russian_name}: {bonus_str}")
        
        # Обрабатываем особенности с выбором характеристик
        if features:
            for feature in features:
                if feature.get("type") == "ability_choice":
                    max_choices = feature.get("max_choices", 1)
                    bonus_value = feature.get("bonus_value", 1)
                    result_parts.append(f"\t🎯 Бонусы: {max_choices} хар-ки (+{bonus_value} к каждой)")
        
        return "\n".join(result_parts) if result_parts else "Нет бонусов"
    
    @staticmethod
    def format_features(features: List[Dict]) -> List[str]:
        """Форматирует особенности для отображения.
        
        Args:
            features: Список особенностей
            
        Returns:
            Список отформатированных строк с особенностями
        """
        formatted = []
        
        for feature in features:
            feature_type = feature.get("type", "unknown")
            name = feature.get("name", "Неизвестная особенность")
            description = feature.get("description", "")
            
            if feature_type == "traits":
                # Обрабатываем составные черты
                traits = feature.get("traits", [])
                if traits:
                    for trait in traits:
                        trait_name = trait.get("name", "Неизвестная черта")
                        trait_desc = trait.get("description", "")
                        formatted.append(f"\t🎯 {trait_name}: {trait_desc}")
                else:
                    formatted.append(f"\t🎯 {name}: {description}")
            elif feature_type == "trait":
                formatted.append(f"\t🎯 {name}: {description}")
            elif feature_type == "proficiency":
                items = feature.get("weapons", feature.get("skills", []))
                if items:
                    items_str = ", ".join(items) if isinstance(items, list) else str(items)
                    formatted.append(f"\t⚔️ {name}: {items_str}")
                else:
                    formatted.append(f"\t⚔️ {name}: {description}")
            elif feature_type == "spell":
                spells = feature.get("spells", [])
                if spells:
                    spells_str = ", ".join(spells) if isinstance(spells, list) else str(spells)
                    formatted.append(f"\t🔮 {name}: {spells_str}")
                else:
                    formatted.append(f"\t🔮 {name}: {description}")
            elif feature_type == "language":
                languages = feature.get("languages", {})
                if languages:
                    base_langs = languages.get("base", [])
                    choice_count = languages.get("choice", 0)
                    
                    if base_langs:
                        lang_str = ", ".join(base_langs) if isinstance(base_langs, list) else str(base_langs)
                        formatted.append(f"\t🌐 {name}: {lang_str}")
                    
                    if choice_count > 0:
                        formatted.append(f"\t🌐 {name}: {description}")
                else:
                    formatted.append(f"\t🌐 {name}: {description}")
            elif feature_type == "mask_wilderness":
                formatted.append(f"\t🌲 {name}: {description}")
            elif feature_type in ["ability_choice", "skill_choice", "feat_choice"]:
                formatted.append(f"\t⚙️ {name}: {description}")
            else:
                formatted.append(f"\t✨ {name}: {description}")
        
        return formatted
    
    @staticmethod
    def get_effective_bonuses(base_bonuses: Dict[str, int], 
                             subrace_bonuses: Dict[str, int] = None,
                             inherit_bonuses: bool = True) -> Dict[str, int]:
        """Вычисляет эффективные бонусы с учетом наследования.
        
        Args:
            base_bonuses: Бонусы основной расы
            subrace_bonuses: Бонусы подрасы
            inherit_bonuses: Наследовать ли бонусы от основной расы
            
        Returns:
            Словарь с итоговыми бонусами
        """
        result = {}
        
        # Если наследуем бонусы, начинаем с базовых
        if inherit_bonuses:
            result.update(base_bonuses)
        
        # Добавляем бонусы подрасы
        if subrace_bonuses:
            result.update(subrace_bonuses)
        
        return result
    
    @staticmethod
    def get_all_features(base_features: List[Dict], 
                       subrace_features: List[Dict] = None,
                       inherit_features: bool = True) -> List[Dict]:
        """Получает все особенности с учетом наследования.
        
        Args:
            base_features: Особенности основной расы
            subrace_features: Особенности подрасы
            inherit_features: Наследовать ли особенности от основной расы
            
        Returns:
            Список всех особенностей
        """
        result = []
        
        # Если наследуем особенности, начинаем с базовых
        if inherit_features and base_features:
            result.extend(base_features)
        
        # Добавляем особенности подрасы
        if subrace_features:
            result.extend(subrace_features)
        
        return result


class RaceDisplayFormatter:
    """Форматировщик для отображения информации о расах."""
    
    def __init__(self):
        self.processor = FeatureProcessor()
    
    def format_race_info(self, race_data, subrace_key: str = None) -> Dict[str, str]:
        """Форматирует полную информацию о расе для отображения.
        
        Args:
            race_data: Данные расы (ParsedRaceData или Dict из YAML)
            subrace_key: Ключ подрасы (опционально)
            
        Returns:
            Словарь с отформатированной информацией
        """
        # Словарь с русскими названиями характеристик
        russian_names = {
            "strength": "Сила",
            "dexterity": "Ловкость",
            "constitution": "Телосложение",
            "intelligence": "Интеллект",
            "wisdom": "Мудрость",
            "charisma": "Харизма"
        }
        
        # Если указана подраса
        if subrace_key and hasattr(race_data, 'subraces') and subrace_key in race_data.subraces:
            subrace_data = race_data.subraces[subrace_key]
            
            name = subrace_data.name
            description = subrace_data.description
            short_description = subrace_data.short_description
            
            # Вычисляем эффективные бонусы
            effective_bonuses = self.processor.get_effective_bonuses(
                race_data.bonuses, 
                subrace_data.bonuses, 
                subrace_data.inherit_bonuses
            )
            
            # Вычисляем все особенности
            all_features = self.processor.get_all_features(
                race_data.features,
                subrace_data.features,
                subrace_data.inherit_features
            )
            
            # Форматируем бонусы
            bonus_parts = []
            for attr_name, bonus in effective_bonuses.items():
                if bonus > 0:
                    russian_name = russian_names.get(attr_name, attr_name.title())
                    bonus_str = f"+{bonus}"
                    bonus_parts.append(f"\t🎯 {russian_name}: {bonus_str}")
            
            bonuses_str = "\n".join(bonus_parts) if bonus_parts else ""
            
            # Форматируем особенности
            features_list = self.processor.format_features(all_features)
            features_str = "\n".join(feature for feature in features_list) if features_list else ""
            
            return {
                "name": name,
                "description": description,
                "short_description": short_description,
                "bonuses": bonuses_str,
                "features": features_str
            }
        else:
            # Основная раса
            name = getattr(race_data, 'name', 'Неизвестная раса')
            description = getattr(race_data, 'description', '')
            short_description = getattr(race_data, 'short_description', '')
            bonuses = getattr(race_data, 'bonuses', {})
            features = getattr(race_data, 'features', [])
            
            # Собираем все бонусы: базовые + из особенностей
            all_bonus_parts = []
            
            # Базовые бонусы
            for attr_name, bonus in bonuses.items():
                if bonus > 0:
                    russian_name = russian_names.get(attr_name, attr_name.title())
                    bonus_str = f"+{bonus}"
                    all_bonus_parts.append(f"\t🎯 {russian_name}: {bonus_str}")
            
            # Бонусы из особенностей (если есть)
            for feature in features:
                if feature.get("type") == "ability_choice":
                    max_choices = feature.get("max_choices", 1)
                    bonus_value = feature.get("bonus_value", 1)
                    all_bonus_parts.append(f"\t🎯 Бонусы: {max_choices} хар-ки (+{bonus_value} к каждой)")
            
            bonuses_str = "\n".join(all_bonus_parts) if all_bonus_parts else ""
            
            # Форматируем все особенности
            features_list = self.processor.format_features(features)
            features_str = "\n".join(feature for feature in features_list) if features_list else ""
            
            return {
                "name": name,
                "description": description,
                "short_description": short_description,
                "bonuses": bonuses_str,
                "features": features_str
            }
    
    def _get_short_description(self, description: str, yaml_short_desc: str = None) -> str:
        """Получает короткое описание из полного или из YAML поля.
        
        Args:
            description: Полное описание расы
            yaml_short_desc: Короткое описание из YAML (опционально)
            
        Returns:
            Короткое описание
        """
        # Если в YAML есть короткое описание, используем его
        if yaml_short_desc:
            return yaml_short_desc
        
        # Иначе генерируем из полного (старая логика)
        if not description:
            return "Описание отсутствует"
        
        # Разделяем на предложения
        sentences = description.split('.')
        
        # Берем первые 1-2 предложения
        short_sentences = []
        for sentence in sentences[:2]:
            sentence = sentence.strip()
            if sentence:
                short_sentences.append(sentence)
        
        short_desc = '. '.join(short_sentences)
        if short_desc and not short_desc.endswith('.'):
            short_desc += '.'
            
        return short_desc if short_desc else "Описание отсутствует"
