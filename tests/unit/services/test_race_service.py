"""Unit тесты для RaceService.

Тестируют загрузку рас, получение данных и применение бонусов.
"""

import pytest
from unittest.mock import patch, mock_open

from src.services.race_service import RaceService
from src.entities.race_entity import Race, Subrace


class TestRaceService:
    """Тесты сервиса рас."""

    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.race_service = RaceService()

    def test_load_races_success(self):
        """Тест успешной загрузки рас."""
        races = self.race_service.load_races()
        
        assert len(races) > 0
        assert any(race.name == "Человек" for race in races)
        assert any(race.name == "Эльф" for race in races)
        assert any(race.name == "Полуорк" for race in races)

    def test_get_race_existing(self):
        """Тест получения существующей расы."""
        race = self.race_service.get_race("Человек")
        
        assert race is not None
        assert race.name == "Человек"
        assert race.speed == 30
        assert race.size == "medium"
        assert race.ability_bonuses.get("strength") == 1

    def test_get_race_nonexistent(self):
        """Тест получения несуществующей расы."""
        race = self.race_service.get_race("НесуществующаяРаса")
        
        assert race is None

    def test_get_race_case_insensitive(self):
        """Тест получения расы без учёта регистра."""
        race_lower = self.race_service.get_race("человек")
        race_upper = self.race_service.get_race("ЧЕЛОВЕК")
        
        assert race_lower is not None
        assert race_upper is not None
        assert race_lower.name == race_upper.name

    def test_get_subrace_existing(self):
        """Тест получения существующей подрасы."""
        subrace = self.race_service.get_subrace("elf", "high_elf")
        
        assert subrace is not None
        assert subrace.name == "Высший эльф"
        assert subrace.parent_race == "elf"
        assert subrace.ability_bonuses.get("intelligence") == 1

    def test_get_subrace_nonexistent(self):
        """Тест получения несуществующей подрасы."""
        subrace = self.race_service.get_subrace("human", "nonexistent")
        
        assert subrace is None

    def test_apply_race_bonuses_human(self):
        """Тест применения бонусов человека."""
        base_abilities = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
        
        race = self.race_service.get_race("Человек")
        result = self.race_service.apply_race_bonuses(base_abilities, race)
        
        # Человек получает +1 ко всем характеристикам
        assert result["strength"] == 11
        assert result["dexterity"] == 11
        assert result["constitution"] == 11
        assert result["intelligence"] == 11
        assert result["wisdom"] == 11
        assert result["charisma"] == 11

    def test_apply_race_bonuses_elf(self):
        """Тест применения бонусов эльфа."""
        base_abilities = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
        
        race = self.race_service.get_race("Эльф")
        result = self.race_service.apply_race_bonuses(base_abilities, race)
        
        # Эльф получает +2 к ловкости
        assert result["strength"] == 10
        assert result["dexterity"] == 12
        assert result["constitution"] == 10
        assert result["intelligence"] == 10
        assert result["wisdom"] == 10
        assert result["charisma"] == 10

    def test_apply_race_bonuses_with_subrace(self):
        """Тест применения бонусов расы и подрасы."""
        base_abilities = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
        
        race = self.race_service.get_race("Эльф")
        subrace = self.race_service.get_subrace("elf", "high_elf")
        result = self.race_service.apply_race_bonuses(base_abilities, race, subrace)
        
        # Эльф: +2 к ловкости, Высший эльф: +1 к интеллекту
        assert result["strength"] == 10
        assert result["dexterity"] == 12
        assert result["constitution"] == 10
        assert result["intelligence"] == 11  # 10 + 1
        assert result["wisdom"] == 10
        assert result["charisma"] == 10

    def test_create_race_selection_success(self):
        """Тест успешного создания выбора расы."""
        result = self.race_service.create_race_selection("Человек")
        
        assert result.race_name == "Человек"
        assert result.subrace_name is None
        assert result.race.name == "Человек"
        assert result.subrace is None
        assert result.final_abilities["strength"] == 11  # 10 + 1
        assert result.final_abilities["dexterity"] == 11  # 10 + 1

    def test_create_race_selection_with_subrace(self):
        """Тест создания выбора расы с подрасой."""
        result = self.race_service.create_race_selection("Эльф", "high_elf")
        
        assert result.race_name == "Эльф"
        assert result.subrace_name == "high_elf"
        assert result.race.name == "Эльф"
        assert result.subrace.name == "Высший эльф"
        assert result.final_abilities["intelligence"] == 11  # 10 + 1
        assert result.final_abilities["dexterity"] == 12  # 10 + 2

    def test_create_race_selection_invalid_race(self):
        """Тест создания выбора с несуществующей расой."""
        with pytest.raises(ValueError, match="Раса не найдена"):
            self.race_service.create_race_selection("НесуществующаяРаса")

    def test_create_race_selection_invalid_subrace(self):
        """Тест создания выбора с несуществующей подрасой."""
        with pytest.raises(ValueError, match="Подраса не найдена"):
            self.race_service.create_race_selection("Эльф", "НесуществующаяПодраса")

    def test_validate_race_choice_valid(self):
        """Тест валидации корректного выбора."""
        assert self.race_service.validate_race_choice("Человек") is True
        assert self.race_service.validate_race_choice("Эльф", "high_elf") is True

    def test_validate_race_choice_invalid_race(self):
        """Тест валидации несуществующей расы."""
        assert self.race_service.validate_race_choice("НесуществующаяРаса") is False

    def test_validate_race_choice_invalid_subrace(self):
        """Тест валидации несуществующей подрасы."""
        assert self.race_service.validate_race_choice("Эльф", "НесуществующаяПодраса") is False

    def test_validate_race_choice_base_not_allowed(self):
        """Тест валидации запрета выбора базовой расы."""
        # Эльфы не позволяют выбирать базовую расу (allow_base_race_choice: false)
        assert self.race_service.validate_race_choice("Эльф") is False
        assert self.race_service.validate_race_choice("Эльф", "high_elf") is True

    @patch("builtins.open", new_callable=mock_open)
    def test_load_races_file_not_found(self, mock_file):
        """Тест обработки отсутствующего файла."""
        mock_file.side_effect = FileNotFoundError("Файл не найден")
        
        service = RaceService("nonexistent.yaml")
        
        with pytest.raises(RuntimeError, match="Файл с расами не найден"):
            service.load_races()

    @patch("builtins.open", new_callable=mock_open)
    def test_load_races_invalid_yaml(self, mock_file):
        """Тест обработки некорректного YAML."""
        import yaml
        mock_file.side_effect = yaml.YAMLError("Invalid YAML")
        
        service = RaceService("invalid.yaml")
        
        with pytest.raises(RuntimeError, match="Ошибка загрузки рас"):
            service.load_races()


if __name__ == "__main__":
    pytest.main([__file__])
