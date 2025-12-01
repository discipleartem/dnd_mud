#!/usr/bin/env python3
"""
Dungeons & Dragons MUD Game
Точка входа в приложение
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from config.config_manager import ConfigManager
from game.core.game_engine import GameEngine
from utils.logger import setup_logger


def main():
    """Главная функция запуска игры"""
    try:
        # Инициализация конфигурации
        config_manager = ConfigManager()
        config_manager.load_config()

        # Настройка логирования
        logger = setup_logger(config_manager.config)
        logger.info("=== Запуск D&D MUD Game ===")

        # Запуск игрового движка
        game = GameEngine(config_manager)
        game.run()

    except KeyboardInterrupt:
        print("\n\nИгра прервана пользователем. До свидания!")
        sys.exit(0)
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()