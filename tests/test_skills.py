"""
Тесты для модуля навыков (skills.py).

Тестируем:
- SkillConfig TypedDict
- SkillsManager методы
- Загрузку конфигурации
- Fallback конфигурацию
- Поиск и фильтрацию навыков
"""

import pytest
from unittest.mock import patch
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
            penalties=["armor"],
        )

        assert config["name"] == "athletics"
        assert config["display_name"] == "Атлетика"
        assert config["attribute"] == "strength"
        assert config["description"] == "Прыжки, плавание"
        assert config["penalties"] == ["armor"]

    def test_skill_config_default_penalties(self):
        """Тестирует значения по умолчанию для штрафов."""
        config = SkillConfig(
            name="perception",
            display_name="Восприятие",
            attribute="wisdom",
            description="Заметить скрытых",
            penalties=[],
        )

        assert config["penalties"] == []


class TestSkillsManagerBasic:
    """Тесты базовых методов SkillsManager."""

    def test_skills_manager_initialization(self):
        """Тестирует инициализацию менеджера навыков."""
        assert hasattr(SkillsManager, "_skills_config")
        assert hasattr(SkillsManager, "_config_loaded")
        assert SkillsManager._config_loaded is False
        assert SkillsManager._skills_config == {}

    def test_load_config_first_time(self):
        """Тестирует первую загрузку конфигурации."""
        # Сбрасываем состояние
        SkillsManager._config_loaded = False
        SkillsManager._skills_config = {}

        # Загружаем конфигурацию
        SkillsManager._load_config()

        assert SkillsManager._config_loaded is True
        assert len(SkillsManager._skills_config) > 0

    def test_load_config_already_loaded(self):
        """Тестирует повторную загрузку конфигурации."""
        # Устанавливаем флаг загрузки
        SkillsManager._config_loaded = True
        original_config = SkillsManager._skills_config.copy()

        # Пытаемся загрузить снова
        SkillsManager._load_config()

        # Конфигурация не должна измениться
        assert SkillsManager._skills_config == original_config

    def test_from_dict_valid_data(self):
        """Тестирует создание конфигурации из валидного словаря."""
        data = {
            "name": "athletics",
            "display_name": "Атлетика",
            "attribute": "strength",
            "description": "Прыжки, плавание",
            "penalties": ["armor"],
        }

        config = SkillsManager.from_dict(data)

        assert config["name"] == "athletics"
        assert config["display_name"] == "Атлетика"
        assert config["attribute"] == "strength"
        assert config["description"] == "Прыжки, плавание"
        assert config["penalties"] == ["armor"]

    def test_from_dict_empty_data(self):
        """Тестирует создание конфигурации из пустого словаря."""
        data = {}

        config = SkillsManager.from_dict(data)

        assert config["name"] == ""
        assert config["display_name"] == ""
        assert config["attribute"] == ""
        assert config["description"] == ""
        assert config["penalties"] == []

    def test_from_dict_type_conversion(self):
        """Тестирует преобразование типов в from_dict."""
        data = {
            "name": 123,  # Число должно стать строкой
            "display_name": None,  # None должно стать пустой строкой
            "attribute": "strength",
            "description": 456,  # Число должно стать строкой
            "penalties": "armor",  # Строка должна стать списком
        }

        config = SkillsManager.from_dict(data)

        assert config["name"] == "123"
        assert config["display_name"] == ""
        assert config["attribute"] == "strength"
        assert config["description"] == "456"
        assert config["penalties"] == ["armor"]

    def test_get_skill_existing(self):
        """Тестирует получение существующего навыка."""
        SkillsManager._load_config()

        skill = SkillsManager.get_skill("athletics")

        assert skill is not None
        assert skill["name"] == "athletics"
        assert "display_name" in skill
        assert "attribute" in skill
        assert "description" in skill
        assert "penalties" in skill

    def test_get_skill_nonexistent(self):
        """Тестирует получение несуществующего навыка."""
        SkillsManager._load_config()

        skill = SkillsManager.get_skill("nonexistent_skill")

        assert skill is None

    def test_get_all_skills(self):
        """Тестирует получение всех навыков."""
        SkillsManager._load_config()

        all_skills = SkillsManager.get_all_skills()

        assert isinstance(all_skills, dict)
        assert len(all_skills) > 0

        for skill_name, skill_config in all_skills.items():
            assert isinstance(skill_name, str)
            assert isinstance(skill_config, dict)
            assert "name" in skill_config
            assert "display_name" in skill_config
            assert "attribute" in skill_config

    def test_get_skill_names(self):
        """Тестирует получение всех имен навыков."""
        SkillsManager._load_config()

        skill_names = SkillsManager.get_skill_names()

        assert isinstance(skill_names, list)
        assert len(skill_names) > 0

        for name in skill_names:
            assert isinstance(name, str)
            assert len(name) > 0

    def test_has_penalty(self):
        """Тестирует проверку наличия штрафов."""
        SkillsManager._load_config()

        # Проверяем навык с штрафами (если такой есть в конфигурации)
        all_skills = SkillsManager.get_all_skills()

        # Находим навык с штрафами для теста
        skill_with_penalties = None
        for skill_config in all_skills.values():
            if skill_config["penalties"]:
                skill_with_penalties = skill_config["name"]
                break

        if skill_with_penalties:
            assert SkillsManager.has_penalty(skill_with_penalties, "armor") is True
        else:
            # Если нет навыков с штрафами, проверяем что метод работает
            assert (
                SkillsManager.has_penalty("athletics", "nonexistent_penalty") is False
            )

    def test_get_penalties(self):
        """Тестирует получение штрафов навыка."""
        SkillsManager._load_config()

        penalties = SkillsManager.get_penalties("athletics")

        assert isinstance(penalties, list)

    def test_get_skill_list_for_display(self):
        """Тестирует получение списка навыков для отображения."""
        SkillsManager._load_config()

        skill_list = SkillsManager.get_skill_list_for_display()

        assert isinstance(skill_list, list)
        assert len(skill_list) > 0

        for skill_info in skill_list:
            assert isinstance(skill_info, dict)
            assert "name" in skill_info
            assert "display_name" in skill_info
            assert "attribute" in skill_info


class TestSkillsManagerConfigLoading:
    """Тесты загрузки конфигурации SkillsManager."""

    def test_load_config_from_yaml_file_exists(self):
        """Тестирует загрузку конфигурации из существующего YAML файла."""
        # Мокируем существование файла
        with patch("pathlib.Path.exists", return_value=True):
            with patch(
                "yaml.safe_load",
                return_value={
                    "skills": {
                        "test_skill": {
                            "name": "test_skill",
                            "display_name": "Тестовый навык",
                            "attribute": "strength",
                            "description": "Тестовое описание",
                            "penalties": ["test_penalty"],
                        }
                    }
                },
            ):
                # Сбрасываем состояние
                SkillsManager._config_loaded = False
                SkillsManager._skills_config = {}

                SkillsManager._load_config()

                assert SkillsManager._config_loaded is True
                assert "test_skill" in SkillsManager._skills_config

                skill = SkillsManager._skills_config["test_skill"]
                assert skill["name"] == "test_skill"
                assert skill["display_name"] == "Тестовый навык"

    def test_load_config_file_not_found(self):
        """Тестирует загрузку конфигурации при отсутствии файла."""
        # Мокируем отсутствие файла
        with patch("pathlib.Path.exists", return_value=False):
            # Сбрасываем состояние
            SkillsManager._config_loaded = False
            SkillsManager._skills_config = {}

            SkillsManager._load_config()

            assert SkillsManager._config_loaded is True
            # Должна загрузиться fallback конфигурация
            assert len(SkillsManager._skills_config) > 0

    def test_load_config_already_loaded(self):
        """Тестирует что конфигурация не перезагружается если уже загружена."""
        # Устанавливаем состояние "загружено"
        SkillsManager._config_loaded = True
        original_config = SkillsManager._skills_config.copy()

        # Пытаемся загрузить снова
        SkillsManager._load_config()

        # Конфигурация не должна измениться
        assert SkillsManager._skills_config == original_config

    def test_load_config_missing_skills_section(self):
        """Тестирует загрузку конфигурации с отсутствующей секцией skills."""
        # Мокируем файл без секции skills
        with patch("pathlib.Path.exists", return_value=True):
            with patch("yaml.safe_load", return_value={"other_section": {}}):
                # Сбрасываем состояние
                SkillsManager._config_loaded = False
                SkillsManager._skills_config = {}

                SkillsManager._load_config()

                assert SkillsManager._config_loaded is True
                # Должна загрузиться fallback конфигурация
                assert len(SkillsManager._skills_config) > 0

    def test_load_config_invalid_yaml(self):
        """Тестирует загрузку конфигурации с невалидным YAML."""
        # Мокируем ошибку при чтении YAML
        with patch("pathlib.Path.exists", return_value=True):
            with patch("yaml.safe_load", side_effect=Exception("Invalid YAML")):
                # Сбрасываем состояние
                SkillsManager._config_loaded = False
                SkillsManager._skills_config = {}

                SkillsManager._load_config()

                assert SkillsManager._config_loaded is True
                # Должна загрузиться fallback конфигурация
                assert len(SkillsManager._skills_config) > 0


class TestSkillsManagerReload:
    """Тесты перезагрузки конфигурации."""

    def test_reload_config(self):
        """Тестирует перезагрузку конфигурации."""
        # Сначала загружаем конфигурацию
        SkillsManager._load_config()

        # Перезагружаем
        SkillsManager.reload_config()

        # Конфигурация должна быть перезагружена
        assert SkillsManager._config_loaded is True
        assert len(SkillsManager._skills_config) > 0

    def test_reload_config_clears_cache(self):
        """Тестирует что перезагрузка очищает кэш."""
        # Загружаем конфигурацию
        SkillsManager._load_config()

        # Добавляем что-то в кэш
        SkillsManager._skills_config["test"] = {"name": "test"}

        # Перезагружаем
        SkillsManager.reload_config()

        # Кэш должен быть очищен
        assert "test" not in SkillsManager._skills_config


class TestSkillsManagerEdgeCases:
    """Тесты граничных случаев SkillsManager."""

    def test_get_skills_by_attribute_empty_result(self):
        """Тестирует получение навыков по характеристике с пустым результатом."""
        SkillsManager._load_config()

        # Запрашиваем навыки для несуществующей характеристики
        skills = SkillsManager.get_skills_by_attribute("nonexistent_attribute")

        assert isinstance(skills, list)
        assert len(skills) == 0

    def test_multiple_calls_ensure_single_load(self):
        """Тестирует что множественные вызовы не вызывают повторную загрузку."""
        # Сбрасываем состояние
        SkillsManager._config_loaded = False
        SkillsManager._skills_config = {}

        # Мокируем метод загрузки для подсчета вызовов
        original_load = SkillsManager._load_config
        call_count = 0

        def mock_load():
            nonlocal call_count
            call_count += 1
            return original_load()

        with patch.object(SkillsManager, "_load_config", side_effect=mock_load):
            # Вызываем несколько раз
            SkillsManager._load_config()
            SkillsManager._load_config()
            SkillsManager._load_config()

            # Должен быть вызван только один раз
            assert call_count == 1

    def test_from_dict_with_none_values(self):
        """Тестирует from_dict с None значениями."""
        data = {
            "name": None,
            "display_name": None,
            "attribute": None,
            "description": None,
            "penalties": None,
        }

        config = SkillsManager.from_dict(data)

        assert config["name"] == ""
        assert config["display_name"] == ""
        assert config["attribute"] == ""
        assert config["description"] == ""
        assert config["penalties"] == []


class TestSkillsManagerRealData:
    """Тесты с реальными данными из fallback конфигурации."""

    def test_real_yaml_skills_count(self):
        """Тестирует количество навыков в реальной конфигурации."""
        SkillsManager._load_config()

        all_skills = SkillsManager.get_all_skills()

        # Проверяем что есть хотя бы несколько навыков
        assert len(all_skills) >= 5  # Минимальное ожидаемое количество

    def test_real_yaml_attributes_coverage(self):
        """Тестирует покрытие всех характеристик в реальной конфигурации."""
        SkillsManager._load_config()

        all_skills = SkillsManager.get_all_skills()
        attributes = set()

        for skill_config in all_skills.values():
            attributes.add(skill_config["attribute"])

        # Проверяем что есть навыки для основных характеристик
        expected_attributes = {
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        }

        # Не все характеристики должны быть обязательно, но хотя бы несколько
        assert len(attributes.intersection(expected_attributes)) >= 3

    def test_real_yaml_skill_structure(self):
        """Тестирует структуру навыков в реальной конфигурации."""
        SkillsManager._load_config()

        all_skills = SkillsManager.get_all_skills()

        for skill_name, skill_config in all_skills.items():
            # Проверяем обязательные поля
            assert "name" in skill_config
            assert "display_name" in skill_config
            assert "attribute" in skill_config
            assert "description" in skill_config
            assert "penalties" in skill_config

            # Проверяем типы
            assert isinstance(skill_config["name"], str)
            assert isinstance(skill_config["display_name"], str)
            assert isinstance(skill_config["attribute"], str)
            assert isinstance(skill_config["description"], str)
            assert isinstance(skill_config["penalties"], list)

            # Проверяем что имя совпадает с ключом
            assert skill_config["name"] == skill_name

    def test_real_yaml_penalties_consistency(self):
        """Тестирует консистентность штрафов в реальной конфигурации."""
        SkillsManager._load_config()

        all_skills = SkillsManager.get_all_skills()

        for skill_config in all_skills.values():
            penalties = skill_config["penalties"]

            # Штрафы должны быть списком
            assert isinstance(penalties, list)

            # Все элементы штрафов должны быть строками
            for penalty in penalties:
                assert isinstance(penalty, str)
                assert len(penalty) > 0
