"""Реализация сервиса ASCII art.

Следует Clean Architecture - реализация интерфейса для ASCII искусства.
Легко заменяемая реализация для разных источников ASCII art.
"""

from typing import Dict

from src.interfaces.services.ascii_art_service import AsciiArtService, AsciiArtError
from src.value_objects.ascii_art import AsciiArt


class SimpleAsciiArtService(AsciiArtService):
    """Реализация сервиса ASCII art с встроенными изображениями.
    
    Следует Clean Architecture - конкретная реализация
    для предоставления ASCII искусства без внешних зависимостей.
    """
    
    def __init__(self) -> None:
        """Инициализация сервиса."""
        self._dnd_logo = AsciiArt.create_dnd_logo().get_value()
        self._dice_art = self._create_dice_art()
        self._character_frames = self._create_character_frames()
    
    def get_dnd_logo(self) -> str:
        """Получить ASCII логотип D&D.
        
        Returns:
            ASCII логотип
        """
        return self._dnd_logo
    
    def get_dice_art(self, dice_type: int) -> str:
        """Получить ASCII изображение кубика.
        
        Args:
            dice_type: Тип кубика
            
        Returns:
            ASCII изображение кубика
        """
        dice_art = self._dice_art.get(dice_type)
        if not dice_art:
            raise AsciiArtError(f"Неподдерживаемый тип кубика: {dice_type}")
        
        return dice_art
    
    def get_character_frame(self, character_name: str) -> str:
        """Получить рамку для персонажа.
        
        Args:
            character_name: Имя персонажа
            
        Returns:
            ASCII рамка с именем
        """
        frame_template = self._character_frames["default"]
        
        # Центрирование имени
        max_width = 50
        centered_name = character_name.center(max_width)
        
        return frame_template.format(name=centered_name)
    
    def get_separator(self, length: int, char: str = "=") -> str:
        """Получить разделитель.
        
        Args:
            length: Длина разделителя
            char: Символ разделителя
            
        Returns:
            ASCII разделитель
        """
        if length <= 0:
            raise AsciiArtError("Длина разделителя должна быть положительной")
        
        if len(char) != 1:
            raise AsciiArtError("Символ разделителя должен быть одним символом")
        
        return char * length
    
    def _create_dice_art(self) -> Dict[int, str]:
        """Создать ASCII изображения кубиков.
        
        Returns:
            Словарь с изображениями кубиков
        """
        return {
            4: """
      /\\
     /  \\
    /____\\
            """,
            
            6: """
    +-------+
    |       |
    |   o   |
    |       |
    +-------+
            """,
            
            8: """
       /\\
      /  \\
     /____\\
     \\    /
      \\  /
       \\/
            """,
            
            10: """
      /\\
     /  \\
    /____\\
    \\    /
     \\  /
      \\/
            """,
            
            12: """
      /\\
     /  \\
    /____\\
    \\    /
     \\  /
      \\/
            """,
            
            20: """
        /\\
       /  \\
      /____\\
      \\    /
       \\  /
        \\/
            """
        }
    
    def _create_character_frames(self) -> Dict[str, str]:
        """Создать рамки для персонажей.
        
        Returns:
            Словарь с шаблонами рамок
        """
        return {
            "default": """
    +------------------------------------------------+
    |                                                |
    |  {name}  |
    |                                                |
    +------------------------------------------------+
            """,
            
            "simple": """
    ================================
    {name}
    ================================
            """
        }
    
    def get_hp_bar(self, current: int, maximum: int, length: int = 20) -> str:
        """Получить полоску хит-поинтов.
        
        Args:
            current: Текущие HP
            maximum: Максимум HP
            length: Длина полоски
            
        Returns:
            ASCII полоска HP
        """
        if maximum <= 0:
            raise AsciiArtError("Максимум HP должен быть положительным")
        
        if length <= 0:
            raise AsciiArtError("Длина полоски должна быть положительной")
        
        filled_length = int(length * current / maximum)
        filled_length = max(0, min(length, filled_length))
        
        bar = "█" * filled_length + "░" * (length - filled_length)
        
        return f"[{bar}] {current}/{maximum}"
    
    def get_ability_score_display(self, score: int, modifier: int) -> str:
        """Получить отображение характеристики.
        
        Args:
            score: Значение характеристики
            modifier: Модификатор
            
        Returns:
            Отформатированная характеристика
        """
        modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        
        return f"""
    +-------+
    | {score:2} |
    | {modifier_str:>3} |
    +-------+
        """
    
    def get_critical_hit(self) -> str:
        """Получить ASCII для критического попадания.
        
        Returns:
            ASCII критического попадания
        """
        return """
    💥 CRITICAL HIT! 💥
        
        ██████ ██    ██ ███████ ██████  
    ██      ██    ██ ██      ██   ██ 
    ██      ██    ██ █████   ██████  
    ██       ██  ██  ██      ██   ██ 
     ██████   ████   ███████ ██   ██ 
        """
    
    def get_critical_miss(self) -> str:
        """Получить ASCII для критического промаха.
        
        Returns:
            ASCII критического промаха
        """
        return """
    💀 CRITICAL MISS! 💀
        
         ██    ██ ███████ ███████ ███████ ███████     
         ██    ██ ██      ██      ██      ██          
         ██    ██ ███████ █████   ███████ ███████     
         ██    ██      ██ ██           ██      ██     
          ██████  ███████ ███████ ███████ ███████     
        """