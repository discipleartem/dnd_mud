"""
Менеджер конфигурации характеристик для D&D MUD.

Объединяет базовые характеристики с модификациями от модов.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Union, Optional, TypedDict
from pathlib import Path
import yaml


class AttributeData(TypedDict):
    """Данные атрибута."""

    name: str
    default_value: int
    min_value: int
    max_value: int
    short_name: str
    description: Optional[str]
    enabled: Optional[bool]


class CoreAttributes(TypedDict):
    """Базовые характеристики."""

    base_attributes: Dict[str, AttributeData]


class ModData(TypedDict):
    """Данные мода."""

    config: Dict[str, Union[str, int, bool]]
    attributes: Dict[str, AttributeData]


class Configs(TypedDict):
    """Структура конфигураций."""

    core: CoreAttributes
    mods: Dict[str, ModData]


@dataclass
class AttributeConfig:
    """Конфигурация отдельной характеристики."""

    name: str
    default_value: int
    min_value: int
    max_value: int
    short_name: str
    description: str = ""
    enabled: bool = True


class UnifiedConfigManager:
    """Единый менеджер конфигурации характеристик.

    Объединяет базовые характеристики D&D с модификациями от модов.
    """

    def __init__(self) -> None:
        self.configs: Configs = {"core": {"base_attributes": {}}, "mods": {}}
        self._load_configs()

    def _load_configs(self) -> None:
        """Загружает все конфигурации."""
        # Загружаем базовые характеристики
        self.configs["core"] = self._load_core_attributes()

        # Загружаем модификации
        self.configs["mods"] = self._load_mods_attributes()

    def _load_core_attributes(self) -> CoreAttributes:
        """Загружает базовые характеристики."""
        try:
            path = (
                Path(__file__).parent.parent.parent.parent
                / "data"
                / "yaml"
                / "attributes"
                / "core_attributes.yaml"
            )

            with open(path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data and "base_attributes" in data:
                    return data
                else:
                    return self._get_builtin_core_attributes()
        except FileNotFoundError:
            print("Базовые атрибуты не найдены, используем встроенные")
            return self._get_builtin_core_attributes()

    def _get_builtin_core_attributes(self) -> CoreAttributes:
        """Встроенные базовые характеристики."""
        return {
            "base_attributes": {
                "strength": {
                    "name": "strength",
                    "default_value": 10,
                    "min_value": 1,
                    "max_value": 20,
                    "short_name": "STR",
                    "description": None,
                    "enabled": True,
                },
                "dexterity": {
                    "name": "dexterity",
                    "default_value": 10,
                    "min_value": 1,
                    "max_value": 20,
                    "short_name": "DEX",
                    "description": None,
                    "enabled": True,
                },
                "constitution": {
                    "name": "constitution",
                    "default_value": 10,
                    "min_value": 1,
                    "max_value": 20,
                    "short_name": "CON",
                    "description": None,
                    "enabled": True,
                },
                "intelligence": {
                    "name": "intelligence",
                    "default_value": 10,
                    "min_value": 1,
                    "max_value": 20,
                    "short_name": "INT",
                    "description": None,
                    "enabled": True,
                },
                "wisdom": {
                    "name": "wisdom",
                    "default_value": 10,
                    "min_value": 1,
                    "max_value": 20,
                    "short_name": "WIS",
                    "description": None,
                    "enabled": True,
                },
                "charisma": {
                    "name": "charisma",
                    "default_value": 10,
                    "min_value": 1,
                    "max_value": 20,
                    "short_name": "CHA",
                    "description": None,
                    "enabled": True,
                },
            }
        }

    def _load_mods_attributes(self) -> Dict[str, ModData]:
        """Загружает модификации от модов."""
        mods_path = Path(__file__).parent.parent.parent.parent / "data" / "mods"

        all_mods = {}

        if mods_path.exists():
            for mod_folder in mods_path.iterdir():
                if mod_folder.is_dir():
                    mod_name = mod_folder.name
                    mod_config = self._load_mod_config(mod_folder)
                    mod_attrs = self._load_mod_attributes(mod_folder)

                    all_mods[mod_name] = {"config": mod_config, "attributes": mod_attrs}

        return all_mods  # type: ignore

    def _load_mod_config(self, mod_folder: Path) -> Dict[str, Union[str, int, bool]]:
        """Загружает конфигурацию мода."""
        config_path = mod_folder / "config.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            return {}

    def _load_mod_attributes(self, mod_folder: Path) -> Dict[str, AttributeData]:
        """Загружает атрибуты мода."""
        attrs_path = mod_folder / "attributes"

        attrs: Dict[str, AttributeData] = {}

        if attrs_path.exists():
            for attr_file in attrs_path.glob("*.yaml"):
                with open(attr_file, "r", encoding="utf-8") as file:
                    attr_data = yaml.safe_load(file)
                    # Преобразуем в AttributeData, добавляя недостающие поля
                    if attr_data and isinstance(attr_data, dict):
                        full_attr_data: AttributeData = {
                            "name": attr_data.get("name", attr_file.stem),
                            "default_value": attr_data.get("default_value", 10),
                            "min_value": attr_data.get("min_value", 1),
                            "max_value": attr_data.get("max_value", 20),
                            "short_name": attr_data.get(
                                "short_name", attr_file.stem[:3].upper()
                            ),
                            "description": attr_data.get("description"),
                            "enabled": attr_data.get("enabled", True),
                        }
                        attrs[attr_file.stem] = full_attr_data

        return attrs

    def get_final_attribute_config(self, name: str) -> Optional[AttributeData]:
        """Возвращает финальную конфигурацию характеристики с учетом модов."""
        # 1. Проверяем базовые характеристики
        core_attrs = self.configs.get("core", {}).get("base_attributes", {})

        if name in core_attrs:
            final_config: AttributeData = core_attrs[name].copy()

            # 2. Применяем модификации
            for mod_name, mod_data in self.configs.get("mods", {}).items():
                if "attributes" in mod_data:
                    mod_attrs = mod_data["attributes"]
                    if name in mod_attrs:
                        for key, value in mod_attrs[name].items():
                            if key != "name" and key in final_config:
                                # Явное приведение типа для удовлетворения mypy
                                if key == "default_value":
                                    final_config["default_value"] = value  # type: ignore
                                elif key == "min_value":
                                    final_config["min_value"] = value  # type: ignore
                                elif key == "max_value":
                                    final_config["max_value"] = value  # type: ignore
                                elif key == "short_name":
                                    final_config["short_name"] = value  # type: ignore
                                elif key == "description":
                                    final_config["description"] = value  # type: ignore
                                elif key == "enabled":
                                    final_config["enabled"] = value  # type: ignore

            return final_config

        return None

    def get_all_enabled_attributes(self) -> Dict[str, AttributeData]:
        """Возвращает все включенные характеристики."""
        result: Dict[str, AttributeData] = {}

        # Базовые характеристики
        core_attrs = self.configs.get("core", {}).get("base_attributes", {})

        for name, attr_data in core_attrs.items():
            if attr_data.get("enabled", True):
                result[name] = attr_data.copy()

        # Модифицированные характеристики
        for mod_name, mod_data in self.configs.get("mods", {}).items():
            if "attributes" in mod_data:
                mod_attrs = mod_data["attributes"]
                for name, attr_data in mod_attrs.items():
                    if attr_data.get("enabled", True):
                        result[name] = attr_data.copy()

        return result
