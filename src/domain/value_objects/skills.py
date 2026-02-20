# src/domain/value_objects/skills.py
"""Менеджер навыков D&D 5e."""

from typing import Dict, List, Optional, Union, TypedDict


class SkillConfig(TypedDict):
    """Конфигурация навыка."""

    name: str
    display_name: str
    attribute: str
    description: str
    penalties: List[str]


class SkillsManager:
    """Менеджер навыков с загрузкой из YAML."""

    _skills_config: Dict[str, SkillConfig] = {}
    _config_loaded: bool = False

    @classmethod
    def _load_config(cls) -> None:
        """Загружает конфигурацию навыков из YAML файла."""
        if cls._config_loaded:
            return

        # Временно используем встроенную конфигурацию
        cls._load_fallback_config()
        cls._config_loaded = True

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, List[str]]]) -> SkillConfig:
        """Создает конфигурацию из словаря."""
        name_data = data.get("name", "")
        display_name_data = data.get("display_name", "")
        attribute_data = data.get("attribute", "")
        description_data = data.get("description", "")
        penalties_data = data.get("penalties", [])

        # Преобразуем в правильные типы
        name = str(name_data) if name_data else ""
        display_name = str(display_name_data) if display_name_data else ""
        attribute = str(attribute_data) if attribute_data else ""
        description = str(description_data) if description_data else ""
        penalties = list(penalties_data) if isinstance(penalties_data, list) else []

        return SkillConfig(
            name=name,
            display_name=display_name,
            attribute=attribute,
            description=description,
            penalties=penalties,
        )

    @classmethod
    def _load_fallback_config(cls) -> None:
        """Загружает встроенную конфигурацию навыков."""
        fallback_data = {
            "skills": {
                "athletics": {
                    "name": "athletics",
                    "display_name": "Атлетика",
                    "attribute": "strength",
                    "description": "Прыжки, плавание, лазание, силовые проверки",
                    "penalties": ["armor"],
                },
                "acrobatics": {
                    "name": "acrobatics",
                    "display_name": "Акробатика",
                    "attribute": "dexterity",
                    "description": "Равновесие, уклонение, гимнастические трюки",
                    "penalties": ["armor"],
                },
                "sleight_of_hand": {
                    "name": "sleight_of_hand",
                    "display_name": "Ловкость рук",
                    "attribute": "dexterity",
                    "description": "Воровство, жонглирование, скрытые манипуляции",
                    "penalties": ["armor"],
                },
                "stealth": {
                    "name": "stealth",
                    "display_name": "Скрытность",
                    "attribute": "dexterity",
                    "description": "Скрытие, передвижение без обнаружения",
                    "penalties": ["armor"],
                },
                "arcana": {
                    "name": "arcana",
                    "display_name": "Магия",
                    "attribute": "intelligence",
                    "description": "Знание магических предметов, заклинаний, существ",
                    "penalties": [],
                },
                "history": {
                    "name": "history",
                    "display_name": "История",
                    "attribute": "intelligence",
                    "description": "Знание исторических событий, легенд, культур",
                    "penalties": [],
                },
                "investigation": {
                    "name": "investigation",
                    "display_name": "Расследование",
                    "attribute": "intelligence",
                    "description": "Поиск улик, анализ доказательств, допросы",
                    "penalties": [],
                },
                "nature": {
                    "name": "nature",
                    "display_name": "Природа",
                    "attribute": "wisdom",
                    "description": "Выживание в дикой природе, знания о животных и растениях",
                    "penalties": [],
                },
                "religion": {
                    "name": "religion",
                    "display_name": "Религия",
                    "attribute": "wisdom",
                    "description": "Знание о божествах, ритуалах, теологических концепциях",
                    "penalties": [],
                },
                "animal_handling": {
                    "name": "animal_handling",
                    "display_name": "Дрессировка животных",
                    "attribute": "wisdom",
                    "description": "Уход за животными, тренировка, лечение",
                    "penalties": [],
                },
                "insight": {
                    "name": "insight",
                    "display_name": "Проницательность",
                    "attribute": "wisdom",
                    "description": "Понимание намерений, обнаружение лжи, эмпатия",
                    "penalties": [],
                },
                "medicine": {
                    "name": "medicine",
                    "display_name": "Медицина",
                    "attribute": "wisdom",
                    "description": "Лечение ран, диагностика болезней, аптечество",
                    "penalties": [],
                },
                "perception": {
                    "name": "perception",
                    "display_name": "Внимательность",
                    "attribute": "wisdom",
                    "description": "Зрение, слух, обоняние, обнаружение угроз",
                    "penalties": [],
                },
                "survival": {
                    "name": "survival",
                    "display_name": "Выживание",
                    "attribute": "wisdom",
                    "description": "Выживание в экстремальных условиях, поиск ресурсов",
                    "penalties": [],
                },
                "deception": {
                    "name": "deception",
                    "display_name": "Обман",
                    "attribute": "charisma",
                    "description": "Ложь, маскировка, социальная инженерия",
                    "penalties": [],
                },
                "intimidation": {
                    "name": "intimidation",
                    "display_name": "Запугивание",
                    "attribute": "charisma",
                    "description": "Угрозы, социальное давление, демонстрация силы",
                    "penalties": [],
                },
                "performance": {
                    "name": "performance",
                    "display_name": "Выступление",
                    "attribute": "charisma",
                    "description": "Актерское мастерство, музыка, танцы, ораторство",
                    "penalties": [],
                },
                "persuasion": {
                    "name": "persuasion",
                    "display_name": "Убеждение",
                    "attribute": "charisma",
                    "description": "Аргументация, переговоры, социальное влияние",
                    "penalties": [],
                },
            }
        }

        cls._skills_config = {
            key: SkillConfig.from_dict(data)
            for key, data in fallback_data["skills"].items()
        }

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
    def get_skills_by_attribute(cls, attribute: str) -> List[SkillConfig]:
        """Возвращает навыки для указанной характеристики."""
        cls._load_config()
        return [
            config
            for config in cls._skills_config.values()
            if config.attribute == attribute
        ]

    @classmethod
    def get_skill_list_for_display(cls) -> List[tuple[str, str, str]]:
        """Возвращает список навыков для отображения."""
        cls._load_config()
        return [
            (config.name, config.display_name, config.attribute)
            for config in cls._skills_config.values()
        ]

    @classmethod
    def is_valid_skill(cls, name: str) -> bool:
        """Проверяет, существует ли навык."""
        cls._load_config()
        return name in cls._skills_config

    @classmethod
    def get_skill_names(cls) -> List[str]:
        """Возвращает список всех имен навыков."""
        cls._load_config()
        return list(cls._skills_config.keys())

    @classmethod
    def get_penalties(cls, skill_name: str) -> List[str]:
        """Возвращает список штрафов для навыка."""
        cls._load_config()
        skill_config = cls._skills_config.get(skill_name)
        return skill_config.penalties if skill_config else []

    @classmethod
    def has_penalty(cls, skill_name: str, penalty_type: str) -> bool:
        """Проверяет, применяется ли к навыку указанный штраф."""
        cls._load_config()
        skill_config = cls._skills_config.get(skill_name)
        return penalty_type in skill_config.penalties if skill_config else False

    @classmethod
    def reload_config(cls) -> None:
        """Перезагружает конфигурацию."""
        cls._config_loaded = False
        cls._skills_config.clear()
        cls._load_config()
