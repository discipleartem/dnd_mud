# src/domain/value_objects/saving_throws.py
"""Менеджер спасбросков D&D 5e."""

from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass
class SavingThrowConfig:
    """Конфигурация спасброска."""

    name: str
    display_name: str
    attribute: str
    description: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "SavingThrowConfig":
        """Создает конфигурацию из словаря."""
        return cls(
            name=data.get("name", ""),
            display_name=data.get("display_name", ""),
            attribute=data.get("attribute", ""),
            description=data.get("description", ""),
        )


class SavingThrowsManager:
    """Менеджер спасбросков с загрузкой из YAML."""

    _throws_config: Dict[str, SavingThrowConfig] = {}
    _config_loaded: bool = False

    @classmethod
    def _load_config(cls) -> None:
        """Загружает конфигурацию спасбросков из YAML файла."""
        if cls._config_loaded:
            return

        try:
            # Временно используем встроенную конфигурацию
            cls._load_fallback_config()
        except Exception:
            cls._load_fallback_config()

        cls._config_loaded = True

    @classmethod
    def _load_fallback_config(cls) -> None:
        """Загружает встроенную конфигурацию спасбросков."""
        fallback_data = {
            "strength": {
                "name": "strength_save",
                "display_name": "Спасбросок Силы",
                "attribute": "strength",
                "description": "Сопротивление силовым эффектам, удержание, вырывание из захвата",
            },
            "dexterity": {
                "name": "dexterity_save",
                "display_name": "Спасбросок Ловкости",
                "attribute": "dexterity",
                "description": "Уворот от ловушек, снарядов, взрывов, эффектов области",
            },
            "constitution": {
                "name": "constitution_save",
                "display_name": "Спасбросок Телосложения",
                "attribute": "constitution",
                "description": "Сопротивление ядам, болезням, истощению, эффектам выносливости",
            },
            "intelligence": {
                "name": "intelligence_save",
                "display_name": "Спасбросок Интеллекта",
                "attribute": "intelligence",
                "description": "Сопротивление ментальным атакам, магии разума, эффектам памяти",
            },
            "wisdom": {
                "name": "wisdom_save",
                "display_name": "Спасбросок Мудрости",
                "attribute": "wisdom",
                "description": "Сопротивление иллюзиям, очарованию, страху, эффектам восприятия",
            },
            "charisma": {
                "name": "charisma_save",
                "display_name": "Спасбросок Харизмы",
                "attribute": "charisma",
                "description": "Сопротивление проклятиям, изгнанию, эффектам личности",
            },
        }

        cls._throws_config = {
            key: SavingThrowConfig.from_dict(data)
            for key, data in fallback_data.items()
        }

    @classmethod
    def get_saving_throw(cls, name: str) -> Optional[SavingThrowConfig]:
        """Возвращает конфигурацию спасброска по имени."""
        cls._load_config()
        return cls._throws_config.get(name)

    @classmethod
    def get_all_saving_throws(cls) -> Dict[str, SavingThrowConfig]:
        """Возвращает все спасброски."""
        cls._load_config()
        return cls._throws_config.copy()

    @classmethod
    def get_saving_throws_by_attribute(cls, attribute: str) -> List[SavingThrowConfig]:
        """Возвращает спасброски для указанной характеристики."""
        cls._load_config()
        return [
            config
            for config in cls._throws_config.values()
            if config.attribute == attribute
        ]

    @classmethod
    def reload_config(cls) -> None:
        """Перезагружает конфигурацию."""
        cls._config_loaded = False
        cls._throws_config.clear()
        cls._load_config()

    @classmethod
    def is_valid_saving_throw(cls, name: str) -> bool:
        """Проверяет, существует ли спасбросок."""
        cls._load_config()
        return name in cls._throws_config

    @classmethod
    def get_saving_throw_names(cls) -> List[str]:
        """Возвращает список всех имен спасбросков."""
        cls._load_config()
        return list(cls._throws_config.keys())
