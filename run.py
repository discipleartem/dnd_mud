#!/usr/bin/env python3
"""Запускной скрипт для DnD MUD."""

import subprocess
import sys
from pathlib import Path

def main():
    """Запуск игры через subprocess для избежания артефактов."""
    src_path = Path(__file__).parent / "src"
    main_script = src_path / "main.py"
    
    try:
        # Запускаем main.py напрямую через subprocess
        result = subprocess.run([sys.executable, str(main_script)], 
                          cwd=src_path,
                          check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Ошибка запуска: {e}")
        return False
    except FileNotFoundError:
        print(f"Файл не найден: {main_script}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
