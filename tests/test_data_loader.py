"""
tests/test_data_loader.py
"""


class TestDataLoader:
    """Тесты для DataLoader"""

    def test_initialize(self, tmp_path):
        """Тест инициализации DataLoader"""
        from game.core.data.data_loader import DataLoader
        from config.config_manager import ConfigManager

        config = ConfigManager()
        config.load_config()
        config.set('paths.base_data', str(tmp_path / 'data'))

        loader = DataLoader(config)
        loader.initialize()

        # Проверяем создание директорий
        assert Path(config.get('paths.base_data')).exists()

    def test_load_races(self):
        """Тест загрузки рас"""
        from game.core.data.data_loader import DataLoader
        from config.config_manager import ConfigManager

        config = ConfigManager()
        config.load_config()

        loader = DataLoader(config)
        loader.initialize()

        races = loader.load_races()
        assert races is not None
        assert isinstance(races, dict)

    def test_cache_functionality(self):
        """Тест кэширования"""
        from game.core.data.data_loader import DataLoader
        from config.config_manager import ConfigManager

        config = ConfigManager()
        config.load_config()

        loader = DataLoader(config)
        loader.initialize()

        # Первая загрузка
        races1 = loader.load_races()
        # Вторая загрузка (из кэша)
        races2 = loader.load_races()

        assert races1 is races2  # Должны быть тем же объектом

        # Очистка кэша
        loader.clear_cache()
        races3 = loader.load_races()
        assert races1 is not races3  # Должны быть разными объектами