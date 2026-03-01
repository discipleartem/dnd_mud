"""Тесты консоли без colorama."""

import pytest
import sys
from unittest.mock import patch
from io import StringIO


def test_console_without_colorama():
    """Тест консоли в режиме без colorama."""
    # Полностью отключаем colorama
    import sys
    from unittest.mock import patch
    from io import StringIO
    
    # Удаляем colorama из всех возможных мест
    modules_to_remove = [k for k in sys.modules.keys() if 'colorama' in k]
    for module in modules_to_remove:
        del sys.modules[module]
    
    # Блокируем повторную импортацию colorama
    with patch('builtins.__import__', side_effect=ImportError()):
        # Импортируем консоль (должна работать без colorama)
        from ui.console import Console
        
        captured_output = StringIO()
        console = Console()
        
        # Тестируем базовые функции
        console.clear()
        console.print_info("Тестовое сообщение")
        console.print_success("Успех")
        console.print_error("Ошибка")
        
        output = captured_output.getvalue()
        
        # Проверяем, что все сообщения присутствуют
        assert "Тестовое сообщение" in output
        assert "Успех" in output  
        assert "Ошибка" in output
        
        # Проверяем, что нет colorama кодов
        assert "\u001b[" not in output  # ANSI escape последовательности
        assert "[0m" not in output     # Reset последовательности