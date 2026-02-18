from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SkillConfig:
    """Конфигурация навыка."""
    name: str
    display_name: str
    attribute: str
    description: str = ""
    penalties: List[str] = None
    
    def __post_init__(self) -> None:
        self.penalties = self.penalties or []


class SkillsManager:
    """Менеджер навыков D&D."""
    
    _skills_config: Dict[str, SkillConfig] = {
        "athletics": SkillConfig("athletics", "Атлетика", "strength", "Прыжки, плавание", ["armor"]),
        "acrobatics": SkillConfig("acrobatics", "Акробатика", "dexterity", "Равновесие", ["armor"]),
        "stealth": SkillConfig("stealth", "Скрытность", "dexterity", "Скрытие", ["armor"]),
        "perception": SkillConfig("perception", "Восприятие", "wisdom", "Заметить скрытых"),
        "persuasion": SkillConfig("persuasion", "Убеждение", "charisma", "Переговоры"),
    }

    @classmethod
    def get_skill(cls, name: str) -> Optional[SkillConfig]:
        """Возвращает конфигурацию навыка по имени."""
        return cls._skills_config.get(name)

    @classmethod
    def get_all_skills(cls) -> Dict[str, SkillConfig]:
        """Возвращает все навыки."""
        return cls._skills_config.copy()

    @classmethod
    def get_skills_by_attribute(cls, attribute: str) -> List[str]:
        """Возвращает список навыков, использующих указанную характеристику."""
        return [
            name for name, config in cls._skills_config.items()
            if config.attribute == attribute
        ]

    @classmethod
    def is_valid_skill(cls, name: str) -> bool:
        """Проверяет, существует ли навык с таким именем."""
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
    def get_saving_throw(cls, attribute: str) -> Optional[SkillConfig]:
        """Возвращает конфигурацию спасброска."""
        return cls.get_skill(f"saving_throw_{attribute}")
