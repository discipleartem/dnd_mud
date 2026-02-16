"""
Менеджер конфигурации характеристик для D&D MUD.

Объединяет базовые характеристики с модификациями от модов.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path

from ..localization.loader import localization
from ..attributes import StandardAttributes


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
        self.configs = {}
        self._load_configs()
    
    def _load_configs(self) -> None:
        """Загружает все конфигурации."""
        # Загружаем базовые характеристики
        self.configs['core'] = self._load_core_attributes()
        
        # Загружаем модификации
        self.configs['mods'] = self._load_mods_attributes()
    
    def _load_core_attributes(self) -> Dict[str, Any]:
        """Загружает базовые характеристики."""
        try:
            path = Path(__file__).parent.parent.parent.parent / "data" / "yaml" / "attributes" / "core_attributes.yaml"
            
            with open(path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Базовые атрибуты не найдены, используем встроенные")
            return self._get_builtin_core_attributes()
    
    def _get_builtin_core_attributes(self) -> Dict[str, Any]:
        """Встроенные базовые характеристики."""
        return {
            'base_attributes': {
                'strength': {
                    'name': 'strength',
                    'default_value': 10,
                    'min_value': 1,
                    'max_value': 20,
                    'short_name': 'STR'
                },
                'dexterity': {
                    'name': 'dexterity',
                    'default_value': 10,
                    'min_value': 1,
                    'max_value': 20,
                    'short_name': 'DEX'
                },
                'constitution': {
                    'name': 'constitution',
                    'default_value': 10,
                    'min_value': 1,
                    'max_value': 20,
                    'short_name': 'CON'
                },
                'intelligence': {
                    'name': 'intelligence',
                    'default_value': 10,
                    'min_value': 1,
                    'max_value': 20,
                    'short_name': 'INT'
                },
                'wisdom': {
                    'name': 'wisdom',
                    'default_value': 10,
                    'min_value': 1,
                    'max_value': 20,
                    'short_name': 'WIS'
                },
                'charisma': {
                    'name': 'charisma',
                    'default_value': 10,
                    'min_value': 1,
                    'max_value': 20,
                    'short_name': 'CHA'
                }
            }
        }
    
    def _load_mods_attributes(self) -> Dict[str, Any]:
        """Загружает модификации от модов."""
        mods_path = Path(__file__).parent.parent.parent.parent / "data" / "mods"
        
        all_mods = {}
        
        if mods_path.exists():
            for mod_folder in mods_path.iterdir():
                if mod_folder.is_dir():
                    mod_name = mod_folder.name
                    mod_config = self._load_mod_config(mod_folder)
                    mod_attrs = self._load_mod_attributes(mod_folder)
                    
                    all_mods[mod_name] = {
                        'config': mod_config,
                        'attributes': mod_attrs
                    }
        
        return all_mods
    
    def _load_mod_config(self, mod_folder: Path) -> Dict[str, Any]:
        """Загружает конфигурацию мода."""
        config_path = mod_folder / "config.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            return {}
    
    def _load_mod_attributes(self, mod_folder: Path) -> Dict[str, Any]:
        """Загружает атрибуты мода."""
        attrs_path = mod_folder / "attributes"
        
        attrs = {}
        
        if attrs_path.exists():
            for attr_file in attrs_path.glob("*.yaml"):
                with open(attr_file, 'r', encoding='utf-8') as file:
                    attr_data = yaml.safe_load(file)
                    attrs[attr_file.stem] = attr_data
        
        return attrs
    
    def get_final_attribute_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Возвращает финальную конфигурацию характеристики с учетом модов."""
        # 1. Проверяем базовые характеристики
        core_attrs = self.configs.get('core', {}).get('base_attributes', {})
        
        if name in core_attrs:
            final_config = core_attrs[name].copy()
            
            # 2. Применяем модификации
            for mod_name, mod_data in self.configs.get('mods', {}).items():
                if 'attributes' in mod_data:
                    mod_attrs = mod_data['attributes']
                    if name in mod_attrs:
                        for key, value in mod_attrs[name].items():
                            if key != 'name':
                                final_config[key] = value
            
            return final_config
        
        return None
    
    def get_all_enabled_attributes(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает все включенные характеристики."""
        result = {}
        
        # Базовые характеристики
        core_attrs = self.configs.get('core', {}).get('base_attributes', {})
        
        for name, attr_data in core_attrs.items():
            if attr_data.get('enabled', True):
                result[name] = attr_data.copy()
        
        # Модифицированные характеристики
        for mod_name, mod_data in self.configs.get('mods', {}).items():
            if 'attributes' in mod_data:
                mod_attrs = mod_data['attributes']
                for name, attr_data in mod_attrs.items():
                    if attr_data.get('enabled', True):
                        result[name] = attr_data.copy()
        
        return result