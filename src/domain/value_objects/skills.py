# src/core/mechanics/skills.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml
from pathlib import Path


@dataclass
class SkillConfig:
    """Конфигурация навыка."""
    name: str                    # "athletics"
    display_name: str            # "Атлетика"
    attribute: str               # "strength"
    description: str             # "Прыжки, плавание..."
    penalties: List[str] = None  # Список штрафов (например ["armor"])
    
    def __post_init__(self):
        if self.penalties is None:
            self.penalties = []


class SkillsManager:
    """Менеджер навыков D&D."""
    
    _skills_config: Dict[str, SkillConfig] = {}
    _config_loaded: bool = False
    
    @classmethod
    def _load_config(cls) -> None:
        """Загружает конфигурацию из YAML."""
        if cls._config_loaded:
            return
            
        try:
            config_path = Path(__file__).parent.parent.parent.parent / "data" / "yaml" / "attributes" / "skills.yaml"
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # Загружаем навыки
            if 'skills' in config:
                for skill_name, skill_data in config['skills'].items():
                    cls._skills_config[skill_name] = SkillConfig(
                        name=skill_data['name'],
                        display_name=skill_data['display_name'],
                        attribute=skill_data['attribute'],
                        description=skill_data['description'],
                        penalties=skill_data.get('penalties', [])
                    )
            
                    
        except FileNotFoundError:
            print(f"Конфигурация навыков не найдена, используем значения по умолчанию")
            cls._load_fallback_config()
        
        cls._config_loaded = True
    
    @classmethod
    def _load_fallback_config(cls) -> None:
        """Загружает базовую конфигурацию если YAML не найден."""
        # Базовые навыки
        basic_skills = {
            'athletics': SkillConfig('athletics', 'Атлетика', 'strength', 'Прыжки, плавание', ['armor']),
            'acrobatics': SkillConfig('acrobatics', 'Акробатика', 'dexterity', 'Равновесие', ['armor']),
            'stealth': SkillConfig('stealth', 'Скрытность', 'dexterity', 'Скрытие', ['armor']),
            'perception': SkillConfig('perception', 'Восприятие', 'wisdom', 'Заметить скрытых', []),
            'persuasion': SkillConfig('persuasion', 'Убеждение', 'charisma', 'Переговоры', []),
        }
        cls._skills_config.update(basic_skills)
        
    
    @classmethod
    def get_skill(cls, name: str) -> Optional[SkillConfig]:
        """Возвращает конфигурацию навыка по имени."""
        cls._load_config()
        return cls._skills_config.get(name)
    
    @classmethod
    def get_all_skills(cls) -> Dict[str, SkillConfig]:
        """Возвращает все навыки."""
        cls._load_config()
        return cls._skills_config.copy()
    
    @classmethod
    def get_skills_by_attribute(cls, attribute: str) -> List[str]:
        """Возвращает список навыков, использующих указанную характеристику."""
        cls._load_config()
        return [name for name, config in cls._skills_config.items() 
                if config.attribute == attribute]
    
    @classmethod
    def is_valid_skill(cls, name: str) -> bool:
        """Проверяет, существует ли навык с таким именем."""
        cls._load_config()
        return name in cls._skills_config
    
    @classmethod
    def get_skill_attribute(cls, skill_name: str) -> Optional[str]:
        """Возвращает характеристику навыка."""
        skill = cls.get_skill(skill_name)
        return skill.attribute if skill else None
    
    @classmethod
    def has_penalty(cls, skill_name: str, penalty_type: str) -> bool:
        """Проверяет, применяется ли к навыку указанный штраф."""
        skill = cls.get_skill(skill_name)
        return penalty_type in skill.penalties if skill else False
    
    @classmethod
    def get_penalties(cls, skill_name: str) -> List[str]:
        """Возвращает список штрафов для навыка."""
        skill = cls.get_skill(skill_name)
        return skill.penalties.copy() if skill else []
    
    @classmethod
    def get_skill_list_for_display(cls) -> List[tuple]:
        """Возвращает список навыков для отображения (имя, отображаемое имя, характеристика)."""
        cls._load_config()
        return [(name, config.display_name, config.attribute) 
                for name, config in cls._skills_config.items()]
    
    @classmethod
    def reload_config(cls) -> None:
        """Перезагружает конфигурацию (полезно для разработки)."""
        cls._skills_config.clear()
        cls._config_loaded = False
        cls._load_config()
