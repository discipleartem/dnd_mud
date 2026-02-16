"""
Модуль рендеринга D&D MUD.

Простая консольная отрисовка.
"""

from __future__ import annotations

import sys
from typing import List, Dict, Any


class Renderer:
    """Простой консольный рендерер."""
    
    def clear_screen(self) -> None:
        """Очищает экран."""
        if sys.platform != "win32":
            print("\033[2J\033[H", end="")
        else:
            import os
            os.system('cls')
    
    def show_title(self, title: str, subtitle: str = "") -> None:
        """Отображает заголовок."""
        width = 70
        border = "=" * width
        
        print(border)
        print(f"{title:^{width}}")
        if subtitle:
            print(f"{subtitle:^{width}}")
        print(border)
        print()
    
    def show_menu(self, title: str, options: List[Dict[str, Any]]) -> None:
        """Отображает меню."""
        width = 50
        border = "-" * width
        
        print(f"{title:^{width}}")
        print(border)
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option['text']}")
        
        print(border)
        print()
    
    def show_error(self, message: str) -> None:
        """Отображает сообщение об ошибке."""
        print(f"\033[1;31m❌ ОШИБКА: {message}\033[0m")
    
    def show_success(self, message: str) -> None:
        """Отображает сообщение об успехе."""
        print(f"\033[1;32m✓ {message}\033[0m")
    
    def show_info(self, message: str) -> None:
        """Отображает информационное сообщение."""
        print(f"\033[1;34mℹ {message}\033[0m")
    
    def get_input(self, prompt: str = "> ") -> str:
        """Получает ввод от пользователя."""
        return input(prompt)


# Глобальный экземпляр рендерера
renderer = Renderer()