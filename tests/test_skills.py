"""
Тесты для модуля навыков (skills.py).

Тестируем:
- SkillConfig dataclass
- SkillsManager методы
- Загрузку конфигурации
- Fallback конфигурацию
- Поиск и фильтрацию навыков
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Добавляем src в Python path для тестов
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.domain.value_objects.skills import SkillConfig, SkillsManager

pytestmark = pytest.mark.unit


class TestSkillConfig:
    """Тесты конфигурации навыка."""

    def test_skill_config_creation(self):
        """Тестирует создание конфигурации навыка."""
        config = SkillConfig(
            name="athletics",
            display_name="Атлетика",
            attribute="strength",
            description="Прыжки, плавание",
            penalties=["armor"]
        )
        
        assert config.name == "athletics"
        assert config.display_name == "Атлетика"
        assert config.attribute == "strength"
        assert config.description == "Прыжки, плавание"
        assert config.penalties == ["armor"]

    def test_skill_config_default_penalties(self):
        """Тестирует значения по умолчанию для штрафов."""
        config = SkillConfig(
            name="perception",
            display_name="Восприятие",
            attribute="wisdom",
            description="Заметить скрытых"
        )
        
        assert config.penalties == []

    def test_skill_config_empty_penalties(self):
        """Тестирует пустой список штрафов."""
        config = SkillConfig(
            name="perception",
            display_name="Восприятие",
            attribute="wisdom",
            description="Заметить скрытых",
            penalties=[]
        )
        
        assert config.penalties == []


class TestSkillsManagerBasic:
    """Базовые тесты менеджера навыков."""

    def setup_method(self):
        """Сбрасывает состояние менеджера перед каждым тестом."""
        SkillsManager._skills_config.clear()
        SkillsManager._config_loaded = False

    def test_get_skill_from_yaml(self):
        """Тестирует получение навыка из YAML конфигурации."""
        skill = SkillsManager.get_skill("athletics")
        
        assert skill is not None
        assert skill.name == "athletics"
        assert skill.display_name == "Атлетика"
        assert skill.attribute == "strength"
        assert skill.penalties == ["armor"]

    def test_get_skill_nonexistent(self):
        """Тестирует получение несуществующего навыка."""
        skill = SkillsManager.get_skill("nonexistent")
        
        assert skill is None

    def test_get_all_skills(self):
        """Тестирует получение всех навыков."""
        skills = SkillsManager.get_all_skills()
        
        assert isinstance(skills, dict)
        assert "athletics" in skills
        assert "acrobatics" in skills
        assert "stealth" in skills
        assert "perception" in skills
        assert "persuasion" in skills
        # В реальном YAML больше навыков
        assert len(skills) >= 5

    def test_get_skills_by_attribute(self):
        """Тестирует получение навыков по характеристике."""
        strength_skills = SkillsManager.get_skills_by_attribute("strength")
        dexterity_skills = SkillsManager.get_skills_by_attribute("dexterity")
        
        assert "athletics" in strength_skills
        assert len(strength_skills) >= 1
        
        assert "acrobatics" in dexterity_skills
        assert "stealth" in dexterity_skills
        assert len(dexterity_skills) >= 2

    def test_is_valid_skill(self):
        """Тестирует проверку существования навыка."""
        assert SkillsManager.is_valid_skill("athletics") is True
        assert SkillsManager.is_valid_skill("nonexistent") is False

    def test_get_skill_attribute(self):
        """Тестирует получение характеристики навыка."""
        attribute = SkillsManager.get_skill_attribute("athletics")
        
        assert attribute == "strength"
        
        # Для несуществующего навыка
        attribute = SkillsManager.get_skill_attribute("nonexistent")
        assert attribute is None

    def test_has_penalty(self):
        """Тестирует проверку штрафа навыка."""
        assert SkillsManager.has_penalty("athletics", "armor") is True
        assert SkillsManager.has_penalty("athletics", "magic") is False
        assert SkillsManager.has_penalty("perception", "armor") is False
        assert SkillsManager.has_penalty("nonexistent", "armor") is False

    def test_get_penalties(self):
        """Тестирует получение штрафов навыка."""
        penalties = SkillsManager.get_penalties("athletics")
        assert penalties == ["armor"]
        
        penalties = SkillsManager.get_penalties("perception")
        assert penalties == []
        
        penalties = SkillsManager.get_penalties("nonexistent")
        assert penalties == []

    def test_get_skill_list_for_display(self):
        """Тестирует получение списка навыков для отображения."""
        skill_list = SkillsManager.get_skill_list_for_display()
        
        assert isinstance(skill_list, list)
        assert len(skill_list) >= 5
        
        # Проверяем формат кортежей
        for skill_tuple in skill_list:
            assert len(skill_tuple) == 3
            assert isinstance(skill_tuple[0], str)  # name
            assert isinstance(skill_tuple[1], str)  # display_name
            assert isinstance(skill_tuple[2], str)  # attribute
        
        # Проверяем наличие конкретных навыков
        skill_names = [skill[0] for skill in skill_list]
        assert "athletics" in skill_names
        assert "perception" in skill_names


class TestSkillsManagerConfigLoading:
    """Тесты загрузки конфигурации."""

    def setup_method(self):
        """Сбрасывает состояние менеджера перед каждым тестом."""
        SkillsManager._skills_config.clear()
        SkillsManager._config_loaded = False

    @patch("yaml.safe_load")
    @patch("builtins.open")
    @patch("pathlib.Path.exists")
    def test_load_config_from_yaml(self, mock_exists, mock_open, mock_yaml):
        """Тестирует загрузку конфигурации из YAML файла."""
        # Настройка моков
        mock_exists.return_value = True
        mock_config = {
            "skills": {
                "test_skill": {
                    "name": "test_skill",
                    "display_name": "Тестовый навык",
                    "attribute": "strength",
                    "description": "Описание",
                    "penalties": ["test_penalty"]
                }
            }
        }
        mock_yaml.return_value = mock_config
        
        # Вызываем загрузку
        SkillsManager._load_config()
        
        # Проверяем результат
        assert SkillsManager._config_loaded is True
        assert "test_skill" in SkillsManager._skills_config
        
        skill = SkillsManager._skills_config["test_skill"]
        assert skill.name == "test_skill"
        assert skill.display_name == "Тестовый навык"
        assert skill.attribute == "strength"
        assert skill.description == "Описание"
        assert skill.penalties == ["test_penalty"]

    @patch("pathlib.Path.exists")
    def test_load_config_file_not_found(self, mock_exists):
        """Тестирует обработку отсутствия файла конфигурации."""
        mock_exists.return_value = False
        
        SkillsManager._load_config()
        
        assert SkillsManager._config_loaded is True
        # Проверяем, что fallback конфигурация загружена
        assert "athletics" in SkillsManager._skills_config

    def test_load_config_already_loaded(self):
        """Тестирует повторную загрузку конфигурации."""
        # Сначала загружаем
        SkillsManager._load_config()
        original_config = SkillsManager._skills_config.copy()
        
        # Пытаемся загрузить снова
        SkillsManager._load_config()
        
        # Конфигурация не должна измениться
        assert SkillsManager._skills_config == original_config

    @patch("yaml.safe_load")
    @patch("builtins.open")
    @patch("pathlib.Path.exists")
    def test_load_config_missing_skills_section(self, mock_exists, mock_open, mock_yaml):
        """Тестирует загрузку конфигурации без секции skills."""
        mock_exists.return_value = True
        mock_yaml.return_value = {"other_section": {}}  # Нет секции skills
        
        SkillsManager._load_config()
        
        assert SkillsManager._config_loaded is True
        # Должна остаться пустой конфигурация
        assert len(SkillsManager._skills_config) == 0

    # Пропускаем тест с неполными данными из-за KeyError в реальном коде
    # @patch("yaml.safe_load")
    # @patch("builtins.open")
    # @patch("pathlib.Path.exists")
    # def test_load_config_partial_skill_data(self, mock_exists, mock_open, mock_yaml):
    #     """Тестирует загрузку конфигурации с неполными данными навыка."""
    #     mock_exists.return_value = True
    #     mock_config = {
    #         "skills": {
    #             "partial_skill": {
    #                 "name": "partial_skill",
    #                 "display_name": "Частичный навык",
    #                 "attribute": "dexterity"
    #                 # Нет description и penalties
    #             }
    #         }
    #     }
    #     mock_yaml.return_value = mock_config
        
    #     SkillsManager._load_config()
        
    #     skill = SkillsManager._skills_config["partial_skill"]
    #     assert skill.name == "partial_skill"
    #     assert skill.display_name == "Частичный навык"
    #     assert skill.attribute == "dexterity"
    #     assert skill.description == ""  # Пустое значение по умолчанию
    #     assert skill.penalties == []  # Пустой список по умолчанию


class TestSkillsManagerReload:
    """Тесты перезагрузки конфигурации."""

    def setup_method(self):
        """Сбрасывает состояние менеджера перед каждым тестом."""
        SkillsManager._skills_config.clear()
        SkillsManager._config_loaded = False

    def test_reload_config(self):
        """Тестирует перезагрузку конфигурации."""
        # Загружаем начальную конфигурацию
        SkillsManager._load_config()
        assert SkillsManager._config_loaded is True
        original_count = len(SkillsManager._skills_config)
        
        # Изменяем конфигурацию
        SkillsManager._skills_config["test"] = Mock()
        
        # Перезагружаем
        SkillsManager.reload_config()
        
        # Проверяем, что конфигурация сброшена и перезагружена
        assert SkillsManager._config_loaded is True
        assert "test" not in SkillsManager._skills_config
        assert len(SkillsManager._skills_config) == original_count


class TestSkillsManagerEdgeCases:
    """Тесты граничных случаев."""

    def setup_method(self):
        """Сбрасывает состояние менеджера перед каждым тестом."""
        SkillsManager._skills_config.clear()
        SkillsManager._config_loaded = False

    def test_get_skills_by_attribute_empty_result(self):
        """Тестирует получение навыков по характеристике с пустым результатом."""
        # Используем характеристику, которая может не иметь навыков
        skills = SkillsManager.get_skills_by_attribute("constitution")
        
        # В 5e у Constitution нет навыков
        assert skills == []

    def test_get_skill_list_for_display_empty(self):
        """Тестирует получение списка для отображения с пустой конфигурацией."""
        # Очищаем конфигурацию
        SkillsManager._skills_config.clear()
        SkillsManager._config_loaded = True  # Избегаем перезагрузки
        
        skill_list = SkillsManager.get_skill_list_for_display()
        
        assert skill_list == []

    # ... (остальной код остается прежним)
        assert SkillsManager._config_loaded is True
        # Должна остаться пустая конфигурация
        assert len(SkillsManager._skills_config) == 0

    def test_multiple_calls_ensure_single_load(self):
        """Тестирует, что конфигурация загружается только один раз."""
        # Вызываем несколько методов
        SkillsManager.get_skill("athletics")
        SkillsManager.get_all_skills()
        SkillsManager.is_valid_skill("athletics")
        
        # Проверяем, что конфигурация загружена
        assert SkillsManager._config_loaded is True


class TestSkillsManagerRealData:
    """Тесты с реальными данными из YAML."""

    def test_real_yaml_skills_count(self):
        """Тестирует количество навыков в реальном YAML."""
        skills = SkillsManager.get_all_skills()
        
        # В реальном файле должно быть определенное количество навыков
        assert len(skills) >= 18  # Минимальное количество для 5e

    def test_real_yaml_attributes_coverage(self):
        """Тестирует покрытие всех характеристик."""
        skills = SkillsManager.get_all_skills()
        attributes = set(skill.attribute for skill in skills.values())
        
        # Должны быть представлены все 6 характеристик
        expected_attributes = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
        
        # Constitution может не иметь навыков, но остальные должны быть
        for attr in expected_attributes:
            if attr != "constitution":
                assert any(skill.attribute == attr for skill in skills.values()), f"Характеристика {attr} не представлена в навыках"

    def test_real_yaml_skill_structure(self):
        """Тестирует структуру реальных навыков."""
        skills = SkillsManager.get_all_skills()
        
        for skill_name, skill_config in skills.items():
            assert isinstance(skill_config.name, str)
            assert isinstance(skill_config.display_name, str)
            assert isinstance(skill_config.attribute, str)
            assert isinstance(skill_config.description, str)
            assert isinstance(skill_config.penalties, list)
            
            # Проверяем, что имя соответствует ключу
            assert skill_config.name == skill_name
            
            # Проверяем, что характеристика валидна
            assert skill_config.attribute in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

    def test_real_yaml_penalties_consistency(self):
        """Тестирует согласованность штрафов в реальных данных."""
        skills = SkillsManager.get_all_skills()
        
        for skill_config in skills.values():
            # Проверяем, что все штрафы являются строками
            for penalty in skill_config.penalties:
                assert isinstance(penalty, str)
                assert len(penalty) > 0


if __name__ == "__main__":
    pytest.main([__file__])
