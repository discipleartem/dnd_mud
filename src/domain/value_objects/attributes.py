# src/core/mechanics/attributes.py
from dataclasses import dataclass
from typing import Dict
import yaml
from pathlib import Path


@dataclass
class StandardAttribute:
    """Стандартная характеристика D&D."""

    name: str  # "strength"
    default_value: int  # 10
    min_value: int  # 1
    max_value: int  # 20
    short_name: str  # "STR"
    description: str = ""  # Описание характеристики


class StandardAttributes:
    """Стандартный набор характеристик D&D."""

    _config: Dict[str, "StandardAttribute"] = {}

    @classmethod
    def _load_config(cls) -> None:
        """Загружает конфигурацию из YAML."""
        if cls._config:
            return

        try:
            config_path = (
                Path(__file__).parent.parent.parent.parent
                / "data"
                / "yaml"
                / "attributes"
                / "core_attributes.yaml"
            )
            with open(config_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)

            for attr_name, attr_data in config["base_attributes"].items():
                cls._config[attr_name] = StandardAttribute(
                    name=attr_data["name"],
                    default_value=attr_data["default_value"],
                    min_value=attr_data["min_value"],
                    max_value=attr_data["max_value"],
                    short_name=attr_data["short_name"],
                    description=attr_data.get("description", ""),
                )
        except FileNotFoundError:
            print("Конфигурация атрибутов не найдена, используем значения по умолчанию")
            # Fallback значения если YAML не найден
            default_attrs = {
                "strength": StandardAttribute("strength", 10, 1, 20, "STR", "Сила"),
                "dexterity": StandardAttribute("dexterity", 10, 1, 20, "DEX", "Ловкость"),
                "constitution": StandardAttribute("constitution", 10, 1, 20, "CON", "Телосложение"),
                "intelligence": StandardAttribute("intelligence", 10, 1, 20, "INT", "Интеллект"),
                "wisdom": StandardAttribute("wisdom", 10, 1, 20, "WIS", "Мудрость"),
                "charisma": StandardAttribute("charisma", 10, 1, 20, "CHA", "Харизма"),
            }
            cls._config.update(default_attrs)

    @classmethod
    def get_all(cls) -> Dict[str, "StandardAttribute"]:
        """Возвращает все стандартные характеристики."""
        cls._load_config()  # Загружаем конфигурацию при первом запросе
        return cls._config

    @classmethod
    def get_attribute(cls, name: str) -> "StandardAttribute":
        """Возвращает атрибут по имени."""
        cls._load_config()
        return cls._config.get(name)

    @classmethod
    def validate_value(cls, name: str, value: int) -> bool:
        """Проверяет значение характеристики по правилам из конфига."""
        attr = cls.get_attribute(name)
        if attr:
            return attr.min_value <= value <= attr.max_value
        return False
