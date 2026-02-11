"""Загрузчик приключений - конкретная реализация ContentLoader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from rich.console import Console

from src.data.content_loader import ContentLoader
from src.data.schemas import AdventureManifest, Location, Quest, Npc, Event


class AdventureLoader(ContentLoader[AdventureManifest]):
    """Загрузчик приключений из data/adventures.
    
    Наследует ContentLoader и реализует загрузку YAML файлов
    приключений с валидацией манифестов и контента.
    """
    
    def get_content_type(self) -> str:
        """Получить тип контента для отладки."""
        return "adventure"
    
    def validate_manifest(self, manifest_data: dict[str, Any]) -> AdventureManifest:
        """Валидировать манифест приключения.
        
        Args:
            manifest_data: Данные из YAML файла
            
        Returns:
            AdventureManifest: Валидированный манифест приключения
        """
        # Проверяем обязательные поля
        required_fields = ['name', 'version', 'description', 'author']
        for field in required_fields:
            if field not in manifest_data:
                raise ValueError(f"Отсутствует обязательное поле: {field}")
        
        # Проверяем структуру манифеста
        if 'manifest' not in manifest_data:
            raise ValueError("Манифест приключения должен содержать секцию 'manifest'")
        
        manifest_section = manifest_data['manifest']
        
        return AdventureManifest(
            name=manifest_section.get('name', ''),
            version=manifest_section.get('version', '1.0.0'),
            description=manifest_section.get('description', ''),
            author=manifest_section.get('author', ''),
            min_level=manifest_section.get('min_level', 1),
            max_level=manifest_section.get('max_level', 20),
            recommended_level=manifest_section.get('recommended_level', 5),
            requires_items=manifest_section.get('requires_items', []),
            requires_abilities=manifest_section.get('requires_abilities', []),
            estimated_hours=manifest_section.get('estimated_hours', 0),
            start_location=manifest_section.get('start_location', 'start'),
            quest_count=manifest_section.get('quest_count', 0)
        )
    
    def load_content(self, content_path: Path) -> dict[str, AdventureManifest]:
        """Загрузить приключение из указанного пути.
        
        Args:
            content_path: Путь к директории приключения
            
        Returns:
            dict[str, AdventureManifest]: Словарь {id: manifest}
        """
        return self.load_all_content(content_path)
    
    def load_single_adventure(self, adventure_path: Path) -> AdventureManifest | None:
        """Загрузить одно приключение.
        
        Args:
            adventure_path: Путь к директории приключения
            
        Returns:
            AdventureManifest | None: Манифест приключения или None
        """
        manifest_file = adventure_path / "adventure.yaml"
        
        if not manifest_file.exists():
            self.console.print(f"[yellow]Манифест не найден: {manifest_file}[/yellow]")
            return None
        
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = yaml.safe_load(f)
                if manifest_data:
                    manifest = self.validate_manifest(manifest_data)
                    # Загружаем контент приключения
                    content = self._load_adventure_content(adventure_path)
                    
                    return {adventure_path.stem: manifest, "content": content}
                    
        except Exception as e:
            self.console.print(f"[red]Ошибка загрузки приключения {adventure_path}: {e}[/red]")
            return None
    
    def _load_adventure_content(self, adventure_path: Path) -> dict[str, Any]:
        """Загрузить контент приключения.
        
        Args:
            adventure_path: Путь к директории приключения
            
        Returns:
            dict[str, Any]: Контент приключения
        """
        content: dict[str, Any] = {}
        
        # Загружаем локации
        locations_dir = adventure_path / "locations"
        if locations_dir.exists():
            content["locations"] = {}
            for location_file in locations_dir.glob("*.yaml"):
                location_data = self._load_yaml_file(location_file)
                if location_data:
                    content["locations"][location_file.stem] = location_data
        
        # Загружаем квесты
        quests_dir = adventure_path / "quests"
        if quests_dir.exists():
            content["quests"] = {}
            for quest_file in quests_dir.glob("*.yaml"):
                quest_data = self._load_yaml_file(quest_file)
                if quest_data:
                    content["quests"][quest_file.stem] = quest_data
        
        # Загружаем NPC
        npcs_dir = adventure_path / "npcs"
        if npcs_dir.exists():
            content["npcs"] = {}
            for npc_file in npcs_dir.glob("*.yaml"):
                npc_data = self._load_yaml_file(npc_file)
                if npc_data:
                    content["npcs"][npc_file.stem] = npc_data
        
        # Загружаем события
        events_dir = adventure_path / "events"
        if events_dir.exists():
            content["events"] = {}
            for event_file in events_dir.glob("*.yaml"):
                event_data = self._load_yaml_file(event_file)
                if event_data:
                    content["events"][event_file.stem] = event_data
        
        return content
    
    def _load_yaml_file(self, yaml_file: Path) -> dict[str, Any] | None:
        """Загрузить YAML файл с обработкой ошибок.
        
        Args:
            yaml_file: Путь к YAML файлу
            
        Returns:
            dict[str, Any] | None: Данные из YAML или None
        """
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.console.print(f"[red]Ошибка загрузки {yaml_file}: {e}[/red]")
            return None
