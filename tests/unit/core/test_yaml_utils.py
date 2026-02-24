#!/usr/bin/env python3
"""Тесты для модуля yaml_utils."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import pytest
import yaml

from src.core.yaml_utils import BaseYamlLoader


class TestBaseYamlLoader:
    """Тесты для базового класса загрузчика YAML."""

    def test_init_with_valid_path(self) -> None:
        """Тест инициализации с валидным путем."""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"test": "data"}, f)
            f.flush()
            
            loader = BaseYamlLoader(Path(f.name))
            assert loader.data_path == Path(f.name)
            
            # Очистка
            Path(f.name).unlink()

    def test_load_yaml_data_success(self) -> None:
        """Тест успешной загрузки YAML данных."""
        test_data = {"races": {"human": {"name": "Человек"}}, "metadata": {"version": "1.0"}}
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            loader = BaseYamlLoader(Path(f.name))
            result = loader._load_yaml_data()
            
            assert result == test_data
            
            # Очистка
            Path(f.name).unlink()

    def test_load_yaml_data_empty_file(self) -> None:
        """Тест загрузки пустого YAML файла."""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()
            
            loader = BaseYamlLoader(Path(f.name))
            result = loader._load_yaml_data()
            
            assert result == {}
            
            # Очистка
            Path(f.name).unlink()

    def test_load_yaml_data_file_not_found(self) -> None:
        """Тест загрузки несуществующего файла."""
        loader = BaseYamlLoader(Path("nonexistent.yaml"))
        
        with pytest.raises(FileNotFoundError):
            loader._load_yaml_data()

    def test_load_yaml_data_invalid_yaml(self) -> None:
        """Тест загрузки невалидного YAML."""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            loader = BaseYamlLoader(Path(f.name))
            
            with pytest.raises(yaml.YAMLError):
                loader._load_yaml_data()
            
            # Очистка
            Path(f.name).unlink()

    def test_load_yaml_data_with_unicode(self) -> None:
        """Тест загрузки YAML с юникод символами."""
        test_data = {"races": {"эльф": {"name": "Эльф"}, "дварф": {"name": "Дварф"}}}
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
            yaml.dump(test_data, f, allow_unicode=True)
            f.flush()
            
            loader = BaseYamlLoader(Path(f.name))
            result = loader._load_yaml_data()
            
            assert result == test_data
            
            # Очистка
            Path(f.name).unlink()

    def test_load_yaml_data_complex_structure(self) -> None:
        """Тест загрузки сложной YAML структуры."""
        test_data = {
            "races": {
                "human": {
                    "name": "Человек",
                    "features": [
                        {"name": "额外技能", "type": "skill"},
                        {"name": "Versatility", "type": "trait"}
                    ],
                    "subraces": {
                        "hill_dwarf": {"name": "Hill Dwarf", "bonus": "+1 HP"}
                    }
                }
            },
            "metadata": {
                "version": "1.0",
                "author": "Test Author",
                "tags": ["dnd", "rpg", "character"]
            }
        }
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            loader = BaseYamlLoader(Path(f.name))
            result = loader._load_yaml_data()
            
            assert result == test_data
            
            # Очистка
            Path(f.name).unlink()


class TestYamlLoaderImplementation:
    """Тесты для конкретной реализации загрузчика."""

    def test_custom_loader_implementation(self) -> None:
        """Тест пользовательской реализации загрузчика."""
        
        class TestRaceLoader(BaseYamlLoader):
            """Тестовый загрузчик рас."""
            
            def load_races(self) -> dict[str, Any]:
                """Загрузить расы."""
                data = self._load_yaml_data()
                return data.get("races", {})
            
            def load_metadata(self) -> dict[str, Any]:
                """Загрузить метаданные."""
                data = self._load_yaml_data()
                return data.get("metadata", {})
        
        test_data = {
            "races": {
                "human": {"name": "Человек", "speed": 30},
                "elf": {"name": "Эльф", "speed": 35}
            },
            "metadata": {"version": "1.0", "total_races": 2}
        }
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            loader = TestRaceLoader(Path(f.name))
            
            races = loader.load_races()
            metadata = loader.load_metadata()
            
            assert len(races) == 2
            assert "human" in races
            assert "elf" in races
            assert races["human"]["name"] == "Человек"
            assert races["elf"]["speed"] == 35
            assert metadata["version"] == "1.0"
            assert metadata["total_races"] == 2
            
            # Очистка
            Path(f.name).unlink()

    def test_inheritance_and_polymorphism(self) -> None:
        """Тест наследования и полиморфизма."""
        
        class TestLoader(BaseYamlLoader):
            """Базовый тестовый загрузчик."""
            
            def get_data(self) -> dict[str, Any]:
                return self._load_yaml_data()
        
        class ExtendedLoader(TestLoader):
            """Расширенный загрузчик."""
            
            def get_keys(self) -> list[str]:
                data = self.get_data()
                return list(data.keys())
            
            def get_value(self, key: str) -> Any:
                data = self.get_data()
                return data.get(key)
        
        test_data = {"key1": "value1", "key2": "value2", "nested": {"subkey": "subvalue"}}
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            loader = ExtendedLoader(Path(f.name))
            
            keys = loader.get_keys()
            value1 = loader.get_value("key1")
            nested = loader.get_value("nested")
            
            assert set(keys) == {"key1", "key2", "nested"}
            assert value1 == "value1"
            assert nested == {"subkey": "subvalue"}
            
            # Очистка
            Path(f.name).unlink()
