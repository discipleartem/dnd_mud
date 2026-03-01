"""Минимальные тесты валидации YAML файлов."""

import unittest
import yaml
from pathlib import Path


class TestYamlMinimal(unittest.TestCase):
    """Минимальные тесты YAML."""

    def test_ui_yaml_exists(self):
        """Тест существования UI YAML файла."""
        ui_file = Path("data/i18n/ru.yaml")
        self.assertTrue(ui_file.exists(), "UI YAML файл должен существовать")

    def test_ui_yaml_structure(self):
        """Тест структуры UI YAML файла."""
        ui_file = Path("data/i18n/ru.yaml")
        
        with open(ui_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Проверяем основные секции
        self.assertIn("ui", data, "UI секция должна существовать")
        self.assertIn("character", data, "Character секция должна существовать")

    def test_module_files_exist(self):
        """Тест существования модульных файлов."""
        modules = ["races", "classes", "skills", "backgrounds", "abilities", "sizes", "languages"]
        
        for module in modules:
            module_file = Path(f"data/{module}/ru.yaml")
            self.assertTrue(module_file.exists(), f"Файл локализации {module} должен существовать")

    def test_races_yaml_structure(self):
        """Тест структуры файла локализации рас."""
        races_file = Path("data/races/ru.yaml")
        
        with open(races_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        races_data = data.get("races", {})
        
        # Проверяем наличие основных рас
        self.assertIn("human", races_data, "Человек должен быть в локализации")
        self.assertIn("elf", races_data, "Эльф должен быть в локализации")
        
        # Проверяем структуру
        human_data = races_data["human"]
        self.assertIn("name", human_data, "У человека должно быть имя")
        self.assertIn("description", human_data, "У человека должно быть описание")


if __name__ == "__main__":
    unittest.main()
