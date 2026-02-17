"""
Загрузчик модов для D&D MUD.

Загружает моды из папки data/mods/ и их конфигурации.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from pathlib import Path


class ModLoader:
    """Загрузчик модов."""
    
    def __init__(self) -> None:
        self.mods = {}
        self._load_all_mods()
    
    def _load_all_mods(self) -> None:
        """Загружает все моды из папки data/mods/."""
        mods_path = Path(__file__).parent.parent.parent.parent / "data" / "mods"
        
        if mods_path.exists():
            for mod_folder in mods_path.iterdir():
                if mod_folder.is_dir():
                    mod_name = mod_folder.name
                    self.mods[mod_name] = self._load_single_mod(mod_folder)
    
    def _load_single_mod(self, mod_folder: Path) -> Dict[str, Any]:
        """Загружает один мод."""
        # Загружаем конфигурацию мода
        config = self._load_mod_config(mod_folder)
        
        # Загружаем атрибуты мода
        attributes = self._load_mod_attributes(mod_folder)
        
        return {
            'config': config,
            'attributes': attributes,
            'races': config.get('new_races', {}),
            'classes': config.get('new_classes', {})
        }
    
    def _load_mod_config(self, mod_folder: Path) -> Dict[str, Any]:
        """Загружает конфигурацию мода."""
        config_path = mod_folder / "config.yaml"
        
        try:
            import yaml
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
    
    def get_mod(self, name: str) -> Optional[Dict[str, Any]]:
        """Возвращает загруженный мод."""
        return self.mods.get(name)
    
    def get_all_mods(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает все моды."""
        return self.mods.copy()