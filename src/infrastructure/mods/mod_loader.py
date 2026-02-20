"""
Загрузчик модов для D&D MUD.

Загружает моды из папки data/mods/ и их конфигурации.
"""

from __future__ import annotations
from typing import Dict, List, Union, Optional, TypedDict
from pathlib import Path
import yaml


class ModConfig(TypedDict):
    """Конфигурация мода."""

    name: str
    version: str
    description: str
    author: str
    new_races: Optional[Dict[str, Dict[str, Union[str, int]]]]
    new_classes: Optional[Dict[str, Dict[str, Union[str, int]]]]
    dependencies: Optional[List[str]]
    config: Optional[Dict[str, Union[str, int, bool]]]
    load_order: Optional[int]


class ModAttributes(TypedDict):
    """Атрибуты мода."""

    config: ModConfig
    attributes: Dict[str, Dict[str, Union[str, int]]]
    races: Dict[str, Dict[str, Union[str, int]]]
    classes: Dict[str, Dict[str, Union[str, int]]]


class ModInfo(TypedDict):
    """Информация о моде."""

    config: ModConfig
    attributes: Dict[str, Dict[str, Union[str, int]]]
    races: Dict[str, Dict[str, Union[str, int]]]
    classes: Dict[str, Dict[str, Union[str, int]]]


class ModLoader:
    """Загрузчик модов."""

    def __init__(self) -> None:
        self.mods: Dict[str, ModInfo] = {}
        self._load_all_mods()

    def _load_all_mods(self) -> None:
        """Загружает все моды из папки data/mods/."""
        mods_path = Path(__file__).parent.parent.parent.parent / "data" / "mods"

        if mods_path.exists():
            for mod_folder in mods_path.iterdir():
                if mod_folder.is_dir():
                    mod_name = mod_folder.name
                    self.mods[mod_name] = self._load_single_mod(mod_folder)

    def _load_single_mod(self, mod_folder: Path) -> ModInfo:
        """Загружает один мод."""
        # Загружаем конфигурацию мода
        config = self._load_mod_config(mod_folder)

        # Загружаем атрибуты мода
        attributes = self._load_mod_attributes(mod_folder)

        # Извлекаем новые расы и классы с проверкой типов
        new_races = config.get("new_races")
        new_classes = config.get("new_classes")

        # Убеждаемся что типы правильные
        races_data = {}
        classes_data = {}

        if isinstance(new_races, dict):
            races_data = new_races
        if isinstance(new_classes, dict):
            classes_data = new_classes

        return {
            "config": config,
            "attributes": attributes,
            "races": races_data,
            "classes": classes_data,
        }

    def _load_mod_config(self, mod_folder: Path) -> ModConfig:
        """Загружает конфигурацию мода."""
        config_path = mod_folder / "config.yaml"

        try:
            import yaml

            with open(config_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
                return {
                    "name": data.get("name", mod_folder.name),
                    "version": data.get("version", "1.0.0"),
                    "description": data.get("description", ""),
                    "author": data.get("author", "Unknown"),
                    "new_races": data.get("new_races"),
                    "new_classes": data.get("new_classes"),
                    "dependencies": data.get("dependencies"),
                    "config": data.get("config"),
                    "load_order": data.get("load_order"),
                }
        except FileNotFoundError:
            return {
                "name": mod_folder.name,
                "version": "1.0.0",
                "description": "",
                "author": "Unknown",
                "new_races": None,
                "new_classes": None,
                "dependencies": None,
                "config": None,
                "load_order": None,
            }

    def _load_mod_attributes(
        self, mod_folder: Path
    ) -> Dict[str, Dict[str, Union[str, int]]]:
        """Загружает атрибуты мода."""
        attrs_path = mod_folder / "attributes"

        attrs: Dict[str, Dict[str, Union[str, int]]] = {}

        if attrs_path.exists():
            for attr_file in attrs_path.glob("*.yaml"):
                with open(attr_file, "r", encoding="utf-8") as file:
                    attr_data = yaml.safe_load(file)
                    if isinstance(attr_data, dict):
                        attrs[attr_file.stem] = attr_data

        return attrs

    def get_mod(self, name: str) -> Optional[ModInfo]:
        """Возвращает загруженный мод."""
        return self.mods.get(name)

    def get_all_mods(self) -> Dict[str, ModInfo]:
        """Возвращает все моды."""
        return self.mods.copy()
