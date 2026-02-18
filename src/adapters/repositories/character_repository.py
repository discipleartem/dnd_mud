"""Менеджер персонажей D&D MUD."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from ...domain.entities.character import Character


class CharacterManager:
    """Простой менеджер персонажей."""
    
    _instance: Optional['CharacterManager'] = None
    
    def __new__(cls) -> 'CharacterManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._saves_dir = Path(__file__).parent.parent.parent / "data" / "saves"
            cls._instance._saves_dir.mkdir(exist_ok=True)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'CharacterManager':
        """Возвращает единственный экземпляр менеджера."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def save_character(self, character: Character) -> bool:
        """Сохраняет персонажа."""
        try:
            filename = f"{character.name}_{character.race.name}_{character.character_class.name}.json"
            filepath = self._saves_dir / filename
            
            save_data = {
                "name": character.name,
                "level": character.level,
                "race_name": character.race.name,
                "class_name": character.character_class.name,
                "strength": character.strength.value,
                "dexterity": character.dexterity.value,
                "constitution": character.constitution.value,
                "intelligence": character.intelligence.value,
                "wisdom": character.wisdom.value,
                "charisma": character.charisma.value,
                "hp_max": character.hp_max,
                "hp_current": character.hp_current,
                "ac": character.ac,
                "gold": getattr(character, 'gold', 0),
                "created_at": datetime.now().isoformat(),
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def load_character(self, filename: str) -> Optional[Character]:
        """Загружает персонажа."""
        try:
            filepath = self._saves_dir / filename
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            from ...domain.entities.universal_race_factory import UniversalRaceFactory
            from ...domain.entities.class_factory import CharacterClassFactory
            from ...domain.entities.attribute import Attribute
            
            # Создаем персонажа из сохраненных данных
            character = Character(
                name=data["name"],
                level=data["level"],
                race=UniversalRaceFactory.create_race(data["race_name"]),
                character_class=CharacterClassFactory.create_class(data["class_name"]),
                strength=Attribute("strength", data["strength"]),
                dexterity=Attribute("dexterity", data["dexterity"]),
                constitution=Attribute("constitution", data["constitution"]),
                intelligence=Attribute("intelligence", data["intelligence"]),
                wisdom=Attribute("wisdom", data["wisdom"]),
                charisma=Attribute("charisma", data["charisma"]),
                hp_max=data["hp_max"],
                hp_current=data["hp_current"],
                ac=data["ac"],
                gold=data.get("gold", 0),
            )
            
            return character
        except Exception:
            return None
    
    def list_characters(self) -> List[str]:
        """Возвращает список сохраненных персонажей."""
        try:
            return [f.name for f in self._saves_dir.glob("*.json")]
        except Exception:
            return []
    
    def get_character_info(self, filename: str) -> Optional[Dict]:
        """Возвращает базовую информацию о персонаже."""
        try:
            filepath = self._saves_dir / filename
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                "name": data["name"],
                "race": data["race_name"],
                "class": data["class_name"],
                "level": data["level"],
            }
        except Exception:
            return None
