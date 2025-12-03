"""
Тесты для основной точки входа
"""
import sys
from unittest.mock import patch
from src.main import main


def test_main_function_exists():
    """Тест что функция main существует"""
    assert callable(main)


def test_main_returns_zero():
    """Тест что main возвращает 0 при успешном выполнении"""
    result = main()
    assert result == 0


def test_main_prints_expected_output(capsys):
    """Тест что main выводит ожидаемый текст"""
    main()
    captured = capsys.readouterr()
    assert "Текстовая MUD-игра" in captured.out
    assert "Инициализация..." in captured.out
    assert "Игра готова к реализации!" in captured.out


@patch('sys.exit')
def test_main_script_execution(mock_exit):
    """Тест что скрипт корректно вызывает sys.exit"""
    # Импортируем модуль как скрипт
    import runpy
    
    with patch('src.main.main', return_value=0) as mock_main:
        try:
            runpy.run_module('src.main', run_name='__main__')
        except SystemExit:
            pass
        
        mock_main.assert_called_once()
