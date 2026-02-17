# src/core/mechanics/saving_throws.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml
from pathlib import Path


@dataclass
class SavingThrowConfig:
    """Конфигурация спасброска."""

    name: str  # "strength_save"
    display_name: str  # "Спасбросок Силы"
    attribute: str  # "strength"
    description: str  # "Сопротивление силовым эффектам"


class SavingThrowsManager:
    """Менеджер спасбросков D&D."""

    _saves_config: Dict[str, SavingThrowConfig] = {}
    _config_loaded: bool = False

    @classmethod
    def _load_config(cls) -> None:
        """Загружает конфигурацию из YAML."""
        if cls._config_loaded:
            return

        try:
            config_path = (
                Path(__file__).parent.parent.parent.parent
                / "data"
                / "yaml"
                / "attributes"
                / "saving_throws.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)

            # Загружаем спасброски
            if "saving_throws" in config:
                for save_name, save_data in config["saving_throws"].items():
                    cls._saves_config[save_name] = SavingThrowConfig(
                        name=save_data["name"],
                        display_name=save_data["display_name"],
                        attribute=save_data["attribute"],
                        description=save_data["description"],
                    )

        except FileNotFoundError:
            print(
                "Конфигурация спасбросков не найдена, используем значения по умолчанию"
            )
            cls._load_fallback_config()

        cls._config_loaded = True

    @classmethod
    def _load_fallback_config(cls) -> None:
        """Загружает базовую конфигурацию если YAML не найден."""
        # Базовые спасброски
        basic_saves = {
            "strength": SavingThrowConfig(
                "strength_save", "Спасбросок Силы", "strength", "Сопротивление силе"
            ),
            "dexterity": SavingThrowConfig(
                "dexterity_save", "Спасбросок Ловкости", "dexterity", "Уворот"
            ),
            "constitution": SavingThrowConfig(
                "constitution_save",
                "Спасбросок Телосложения",
                "constitution",
                "Сопротивление ядам",
            ),
            "intelligence": SavingThrowConfig(
                "intelligence_save",
                "Спасбросок Интеллекта",
                "intelligence",
                "Сопротивление ментальным атакам",
            ),
            "wisdom": SavingThrowConfig(
                "wisdom_save", "Спасбросок Мудрости", "wisdom", "Сопротивление иллюзиям"
            ),
            "charisma": SavingThrowConfig(
                "charisma_save",
                "Спасбросок Харизмы",
                "charisma",
                "Сопротивление проклятиям",
            ),
        }
        cls._saves_config.update(basic_saves)

    @classmethod
    def get_saving_throw(cls, attribute: str) -> Optional[SavingThrowConfig]:
        """Возвращает конфигурацию спасброска по характеристике."""
        cls._load_config()
        return cls._saves_config.get(attribute)

    @classmethod
    def get_all_saving_throws(cls) -> Dict[str, SavingThrowConfig]:
        """Возвращает все спасброски."""
        cls._load_config()
        return cls._saves_config.copy()

    @classmethod
    def is_valid_saving_throw(cls, attribute: str) -> bool:
        """Проверяет, существует ли спасбросок для характеристики."""
        cls._load_config()
        return attribute in cls._saves_config

    @classmethod
    def get_saving_throw_attribute(cls, save_name: str) -> Optional[str]:
        """Возвращает характеристику спасброска."""
        save = cls.get_saving_throw(save_name)
        return save.attribute if save else None

    @classmethod
    def get_saving_throws_list_for_display(cls) -> List[tuple]:
        """Возвращает список спасбросков для отображения (имя, отображаемое имя, характеристика)."""
        cls._load_config()
        return [
            (name, config.display_name, config.attribute)
            for name, config in cls._saves_config.items()
        ]

    @classmethod
    def reload_config(cls) -> None:
        """Перезагружает конфигурацию (полезно для разработки)."""
        cls._saves_config.clear()
        cls._config_loaded = False
        cls._load_config()
