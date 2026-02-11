"""Загрузчик модов - конкретная реализация ContentLoader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

from src.data.content_loader import ContentLoader
from src.data.schemas import ModManifest


class ModLoader(ContentLoader[ModManifest]):
    """Загрузчик модов из data/mods.
    
    Наследует ContentLoader и реализует загрузку YAML файлов
    модов с валидацией манифестов.
    """
    
    def get_content_type(self) -> str:
        """Получить тип контента для отладки."""
        return "mod"
    
    def validate_manifest(self, manifest_data: dict[str, Any]) -> ModManifest:
        """Валидировать манифест мода.
        
        Args:
            manifest_data: Данные из YAML файла
            
        Returns:
            ModManifest: Валидированный манифест мода
        """
        # Проверяем обязательные поля
        required_fields = ['name', 'version', 'description', 'author']
        for field in required_fields:
            if field not in manifest_data:
                raise ValueError(f"Отсутствует обязательное поле: {field}")
        
        # Проверяем структуру манифеста
        if 'manifest' not in manifest_data:
            raise ValueError("Манифест мода должен содержать секцию 'manifest'")
        
        manifest_section = manifest_data['manifest']
        
        return ModManifest(
            name=manifest_section.get('name', ''),
            version=manifest_section.get('version', '0.1.0'),
            description=manifest_section.get('description', ''),
            author=manifest_section.get('author', ''),
            compatible_version=manifest_section.get('compatible_version', '0.1.0'),
            compatibility_level=manifest_section.get('compatibility_level', 'minor'),
            dependencies=manifest_section.get('dependencies', []),
            conflicts=manifest_section.get('conflicts', []),
            load_before=manifest_section.get('load_before', []),
            load_after=manifest_section.get('load_after', []),
            provides=manifest_section.get('provides', [])
        )
    
    def load_content(self, content_path: Path) -> dict[str, ModManifest]:
        """Загрузить мод из указанного пути.
        
        Args:
            content_path: Путь к файлу мода
            
        Returns:
            dict[str, ModManifest]: Словарь {id: manifest}
        """
        return self.load_all_content(content_path)
    
    def load_single_mod(self, mod_path: Path) -> ModManifest | None:
        """Загрузить один мод.
        
        Args:
            mod_path: Путь к директории мода
            
        Returns:
            ModManifest | None: Манифест мода или None
        """
        manifest_file = mod_path / "mod.yaml"
        
        if not manifest_file.exists():
            self.console.print(f"[yellow]Манифест не найден: {manifest_file}[/yellow]")
            return None
        
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = yaml.safe_load(f)
                if manifest_data:
                    manifest = self.validate_manifest(manifest_data)
                    # Загружаем дополнительный контент мода
                    content_files = list(mod_path.glob("*.yaml"))
                    for content_file in content_files:
                        if content_file.name != "mod.yaml":
                            # TODO: Загрузить контент мода
                            pass
                    
                    return {mod_path.stem: manifest}
                    
        except Exception as e:
            self.console.print(f"[red]Ошибка загрузки мода {mod_path}: {e}[/red]")
            return None
