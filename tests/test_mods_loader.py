"""
tests/test_mods_loader.py
"""


class TestModsLoader:
    """Тесты для ModsLoader"""

    def test_initialization(self, tmp_path):
        """Тест инициализации ModsLoader"""
        from utils.mods_loader import ModsLoader
        from config.config_manager import ConfigManager

        config = ConfigManager()
        config.load_config()
        config.set('paths.mods', str(tmp_path / 'mods'))
        config.set('mods.enabled', True)

        loader = ModsLoader(config)
        loader.initialize()

        # Проверяем создание директории модов
        assert Path(config.get('paths.mods')).exists()

    def test_apply_mods(self, tmp_path):
        """Тест применения модов"""
        from utils.mods_loader import ModsLoader
        from config.config_manager import ConfigManager
        import yaml

        # Создаем тестовый мод
        mods_dir = tmp_path / 'mods'
        mods_dir.mkdir()

        test_mod = {
            'mod_info': {
                'name': 'Test Mod',
                'version': '1.0.0',
                'author': 'Tester'
            },
            'races': {
                'test_race': {
                    'name': 'Test Race',
                    'description': 'Test'
                }
            }
        }

        with open(mods_dir / 'test_mod.yaml', 'w') as f:
            yaml.dump(test_mod, f)

        config = ConfigManager()
        config.load_config()
        config.set('paths.mods', str(mods_dir))
        config.set('mods.enabled', True)

        loader = ModsLoader(config)
        loader.initialize()

        # Применяем моды
        base_data = {'races': {}}
        modified = loader.apply_mods(base_data, 'races')

        assert 'test_race' in modified['races']


# Фикстуры для pytest
@pytest.fixture
def temp_config(tmp_path):
    """Временная конфигурация для тестов"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


if __name__ == '__main__':
    pytest.main([__file__, '-v'])