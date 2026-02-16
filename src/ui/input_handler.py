"""
Модуль обработки пользовательского ввода D&D MUD.
"""

from __future__ import annotations

from typing import Dict, Any


class InputHandler:
    """Класс для обработки пользовательского ввода."""
    
    def __init__(self) -> None:
        """Инициализация обработчика ввода."""
        pass
    
    def get_menu_choice(self, max_options: int) -> int:
        """Получает выбор пункта меню от пользователя."""
        try:
            while True:
                user_input = input(f"Введите номер (1-{max_options}): ").strip()
                
                if not user_input:
                    continue
                
                if user_input.isdigit():
                    choice = int(user_input)
                    if 1 <= choice <= max_options:
                        return choice
                    else:
                        print(f"Пожалуйста, введите число от 1 до {max_options}")
                else:
                    print("Пожалуйста, введите число")
                    
        except (EOFError, KeyboardInterrupt):
            return max_options  # Возвращаем последний пункт (обычно "Выход")
    
    def get_text_input(self, prompt: str = "> ") -> str:
        """Получает текстовый ввод от пользователя."""
        try:
            return input(prompt)
        except (EOFError, KeyboardInterrupt):
            return ""


# Глобальный экземпляр обработчика ввода
input_handler = InputHandler()