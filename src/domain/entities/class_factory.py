# src/core/entities/class_factory.py
from typing import Dict, List, Optional
from .class_ import CharacterClass
from ..interfaces.localization import get_text


class CharacterClassFactory:
    """Фабрика для создания классов из YAML конфигурации."""
    
    _classes_cache: Dict[str, CharacterClass] = {}
    
    @classmethod
    def create_class(cls, class_key: str) -> CharacterClass:
        """Создает объект класса по ключу.
        
        Args:
            class_key: Ключ класса (fighter, rogue, bard, cleric)
            
        Returns:
            Объект класса
        """
        if class_key in cls._classes_cache:
            return cls._classes_cache[class_key]
        
        classes_data = cls.get_all_classes_data()
        
        if class_key not in classes_data:
            raise ValueError(f"Класс '{class_key}' не найден")
        
        class_data = classes_data[class_key]
        
        character_class = CharacterClass(
            name=class_data['name'],
            description=class_data.get('description', ''),
            hit_die=class_data.get('hit_die', 'd10')
        )
        
        # Сохраняем дополнительные данные в атрибутах
        character_class.primary_ability = class_data.get('primary_ability', 'strength')
        character_class.saving_throws = class_data.get('saving_throws', [])
        character_class.armor_proficiencies = class_data.get('armor_proficiencies', [])
        character_class.weapon_proficiencies = class_data.get('weapon_proficiencies', [])
        character_class.spellcasting = class_data.get('spellcasting', {})
        character_class.divine_domain = class_data.get('divine_domain')
        character_class.skills = class_data.get('skills', {})
        
        cls._classes_cache[class_key] = character_class
        return character_class
    
    @classmethod
    def get_all_classes_data(cls) -> Dict[str, Dict]:
        """Возвращает все данные классов из YAML."""
        try:
            path = __import__('pathlib').Path(__file__).parent.parent.parent.parent / "data" / "yaml" / "attributes" / "core_classes.yaml"
            with open(path, 'r', encoding='utf-8') as file:
                import yaml
                data = yaml.safe_load(file) or {}
                return data.get('classes', {})
        except FileNotFoundError:
            print(f"Файл классов не найден, возвращаем пустой словарь")
            return {}
    
    @classmethod
    def get_all_classes(cls) -> List[CharacterClass]:
        """Возвращает список всех доступных классов."""
        classes_data = cls.get_all_classes_data()
        classes = []
        
        for class_key in classes_data:
            classes.append(cls.create_class(class_key))
            
        return classes
    
    @classmethod
    def get_class_choices(cls) -> Dict[str, str]:
        """Возвращает словарь для меню выбора классов."""
        classes_data = cls.get_all_classes_data()
        choices = {}
        choice_num = 1
        
        for class_key, class_data in classes_data.items():
            choices[str(choice_num)] = class_data['name']
            choice_num += 1
        
        return choices
    
    @classmethod
    def find_class_by_name(cls, name: str) -> Optional[CharacterClass]:
        """Находит класс по названию."""
        for character_class in cls.get_all_classes():
            if character_class.name == name:
                return character_class
        return None
    
    @classmethod
    def clear_cache(cls) -> None:
        """Очищает кэш классов."""
        cls._classes_cache.clear()
