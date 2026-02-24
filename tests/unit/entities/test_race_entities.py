#!/usr/bin/env python3
"""Тесты для сущностей рас."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from unittest.mock import Mock, patch

import pytest
import yaml

from src.ui.entities.race import (
    Feature,
    Race,
    RaceLoader,
    SubRace,
)
from src.ui.entities.character import Size


class TestFeature:
    """Тесты для класса Feature."""

    def test_feature_init(self) -> None:
        """Тест инициализации Feature."""
        mechanics = {"type": "skill_bonus", "value": 2, "skills": ["stealth", "perception"]}
        
        feature = Feature(
            name="Коварство",
            description="Вы получаете преимущество на проверки Ловкости (Скрытность)",
            mechanics=mechanics
        )
        
        assert feature.name == "Коварство"
        assert feature.description == "Вы получаете преимущество на проверки Ловкости (Скрытность)"
        assert feature.mechanics == mechanics

    def test_feature_init_minimal(self) -> None:
        """Тест минимальной инициализации Feature."""
        feature = Feature(
            name="Test Feature",
            description="Test Description",
            mechanics={}
        )
        
        assert feature.name == "Test Feature"
        assert feature.description == "Test Description"
        assert feature.mechanics == {}


class TestSubRace:
    """Тесты для класса SubRace."""

    def test_subrace_init_full(self) -> None:
        """Тест полной инициализации SubRace."""
        features = [
            Feature("Feature 1", "Description 1", {"type": "bonus"}),
            Feature("Feature 2", "Description 2", {"type": "skill"})
        ]
        
        subrace = SubRace(
            name="Высший эльф",
            description="Изящный и мудрый эльф с магическими способностями",
            ability_bonuses={"intelligence": 2, "dexterity": 1},
            ability_bonuses_description="+2 к Интеллекту, +1 к Ловкости",
            languages=["elvish", "common"],
            features=features,
            inherit_base_abilities=True
        )
        
        assert subrace.name == "Высший эльф"
        assert subrace.description == "Изящный и мудрый эльф с магическими способностями"
        assert subrace.ability_bonuses == {"intelligence": 2, "dexterity": 1}
        assert subrace.ability_bonuses_description == "+2 к Интеллекту, +1 к Ловкости"
        assert subrace.languages == ["elvish", "common"]
        assert len(subrace.features) == 2
        assert subrace.inherit_base_abilities is True

    def test_subrace_init_minimal(self) -> None:
        """Тест минимальной инициализации SubRace."""
        subrace = SubRace(
            name="Test SubRace",
            description="Test Description"
        )
        
        assert subrace.name == "Test SubRace"
        assert subrace.description == "Test Description"
        assert subrace.ability_bonuses == {}
        assert subrace.ability_bonuses_description == ""
        assert subrace.languages == []
        assert subrace.features == []
        assert subrace.inherit_base_abilities is True


class TestRace:
    """Тесты для класса Race."""

    def test_race_init_full(self) -> None:
        """Тест полной инициализации Race."""
        features = [
            Feature("Darkvision", "Вы можете видеть в темноте", {"range": 60}),
            Feature("Fey Ancestry", "Преимущество против очарования", {"type": "charm_resistance"})
        ]
        
        subraces = {
            "high_elf": SubRace(
                name="Высший эльф",
                description="Магический эльф",
                ability_bonuses={"intelligence": 1},
                features=[Feature("Cantrip", "Знание заклинания", {"type": "magic"})]
            ),
            "wood_elf": SubRace(
                name="Лесной эльф", 
                description="Лесной охотник",
                ability_bonuses={"wisdom": 1},
                features=[Feature("Mask of the Wild", "Маскировка в лесу", {"type": "stealth"})]
            )
        }
        
        race = Race(
            name="Эльф",
            description="Изящное и долгоживущее существо",
            ability_bonuses={"dexterity": 2},
            ability_bonuses_description="+2 к Ловкости",
            size=Size.MEDIUM,
            speed=30,
            age={"adult": 100, "max": 750},
            languages=["elvish", "common"],
            features=features,
            subraces=subraces,
            allow_base_race_choice=True
        )
        
        assert race.name == "Эльф"
        assert race.description == "Изящное и долгоживущее существо"
        assert race.ability_bonuses == {"dexterity": 2}
        assert race.ability_bonuses_description == "+2 к Ловкости"
        assert race.size == Size.MEDIUM
        assert race.speed == 30
        assert race.age == {"adult": 100, "max": 750}
        assert race.languages == ["elvish", "common"]
        assert len(race.features) == 2
        assert len(race.subraces) == 2
        assert race.allow_base_race_choice is True

    def test_race_init_minimal(self) -> None:
        """Тест минимальной инициализации Race."""
        race = Race(
            name="Человек",
            description="Универсальная раса"
        )
        
        assert race.name == "Человек"
        assert race.description == "Универсальная раса"
        assert race.ability_bonuses == {}
        assert race.ability_bonuses_description == ""
        assert race.size == Size.MEDIUM
        assert race.speed == 30
        assert race.age == {}
        assert race.languages == []
        assert race.features == []
        assert race.subraces == {}
        assert race.allow_base_race_choice is False

    @patch('src.ui.entities.race.get_language_service')
    @patch('src.ui.entities.race.LanguageDisplayService')
    @patch('src.ui.entities.race.t')
    def test_get_languages_display_with_languages(self, mock_t, mock_display_service, mock_lang_service) -> None:
        """Тест отображения языков когда они есть."""
        # Настройка моков
        mock_language = Mock()
        mock_language.code = "common"
        mock_display_service.get_language_name.return_value = "Общий"
        
        mock_lang_instance = Mock()
        mock_lang_instance.get_language_by_code.return_value = mock_language
        mock_lang_service.return_value = mock_lang_instance
        
        race = Race(
            name="Человек",
            description="Универсальная раса",
            languages=["common", "elvish"]
        )
        
        result = race.get_languages_display()
        
        # Проверяем вызовы
        mock_lang_service.assert_called_once()
        assert mock_lang_instance.get_language_by_code.call_count == 2
        assert mock_display_service.get_language_name.call_count == 2

    @patch('src.ui.entities.race.t')
    def test_get_languages_display_empty(self, mock_t) -> None:
        """Тест отображения языков когда их нет."""
        mock_t.return_value = "Нет доступных языков"
        
        race = Race(
            name="Тестовая раса",
            description="Тестовое описание",
            languages=[]
        )
        
        result = race.get_languages_display()
        
        assert result == "Нет доступных языков"
        mock_t.assert_called_once_with("errors.no_languages")

    def test_get_effective_ability_bonuses_no_subrace(self) -> None:
        """Тест получения бонусов без подрасы."""
        race = Race(
            name="Человек",
            description="Универсальная раса",
            ability_bonuses={"strength": 1, "dexterity": 1}
        )
        
        bonuses = race.get_effective_ability_bonuses()
        
        assert bonuses == {"strength": 1, "dexterity": 1}

    def test_get_effective_ability_bonuses_with_inheriting_subrace(self) -> None:
        """Тест получения бонусов с наследующей подрасой."""
        subrace = SubRace(
            name="Высший человек",
            description="Умный человек",
            ability_bonuses={"intelligence": 2},
            inherit_base_abilities=True
        )
        
        race = Race(
            name="Человек",
            description="Универсальная раса",
            ability_bonuses={"strength": 1, "dexterity": 1}
        )
        
        bonuses = race.get_effective_ability_bonuses(subrace)
        
        assert bonuses == {"strength": 1, "dexterity": 1, "intelligence": 2}

    def test_get_effective_ability_bonuses_with_non_inheriting_subrace(self) -> None:
        """Тест получения бонусов с не наследующей подрасой."""
        subrace = SubRace(
            name="Особый человек",
            description="Особый человек",
            ability_bonuses={"intelligence": 3, "wisdom": 2},
            inherit_base_abilities=False
        )
        
        race = Race(
            name="Человек",
            description="Универсальная раса",
            ability_bonuses={"strength": 1, "dexterity": 1}
        )
        
        bonuses = race.get_effective_ability_bonuses(subrace)
        
        assert bonuses == {"intelligence": 3, "wisdom": 2}

    def test_should_include_base_abilities(self) -> None:
        """Тест проверки включения базовых способностей."""
        race = Race(name="Тест", description="Тест")
        
        # Без подрасы
        assert race._should_include_base_abilities(None) is True
        
        # С наследующей подрасой
        inheriting_subrace = SubRace("Test", "Test", inherit_base_abilities=True)
        assert race._should_include_base_abilities(inheriting_subrace) is True
        
        # С не наследующей подрасой
        non_inheriting_subrace = SubRace("Test", "Test", inherit_base_abilities=False)
        assert race._should_include_base_abilities(non_inheriting_subrace) is False

    @patch('src.ui.entities.race.Race.get_all_races')
    def test_get_race_by_name_success(self, mock_get_all) -> None:
        """Тест успешного получения расы по имени."""
        mock_race1 = Race(name="Человек", description="Человек")
        mock_race2 = Race(name="Эльф", description="Эльф")
        mock_race3 = Race(name="Дварф", description="Дварф")
        
        mock_get_all.return_value = {
            "human": mock_race1,
            "elf": mock_race2,
            "dwarf": mock_race3
        }
        
        result = Race.get_race_by_name("эльф")
        
        assert result is mock_race2
        mock_get_all.assert_called_once()

    @patch('src.ui.entities.race.Race.get_all_races')
    def test_get_race_by_name_not_found(self, mock_get_all) -> None:
        """Тест получения расы по имени когда не найдено."""
        mock_race = Race(name="Человек", description="Человек")
        mock_get_all.return_value = {"human": mock_race}
        
        result = Race.get_race_by_name("орк")
        
        assert result is None
        mock_get_all.assert_called_once()

    @patch('src.ui.entities.race.Race.get_all_races')
    def test_get_race_by_name_case_insensitive(self, mock_get_all) -> None:
        """Тест получения расы по имени без учета регистра."""
        mock_race = Race(name="Человек", description="Человек")
        mock_get_all.return_value = {"human": mock_race}
        
        result1 = Race.get_race_by_name("человек")
        result2 = Race.get_race_by_name("ЧЕЛОВЕК")
        result3 = Race.get_race_by_name("ЧеЛоВеК")
        
        assert result1 is mock_race
        assert result2 is mock_race
        assert result3 is mock_race


class TestRaceLoader:
    """Тесты для класса RaceLoader."""

    def create_test_race_data(self) -> dict[str, Any]:
        """Создать тестовые данные рас."""
        return {
            "races": {
                "human": {
                    "name": "Человек",
                    "description": "Универсальная и адаптивная раса",
                    "ability_bonuses": {"strength": 1, "dexterity": 1, "constitution": 1, "intelligence": 1, "wisdom": 1, "charisma": 1},
                    "ability_bonuses_description": "+1 ко всем характеристикам",
                    "size": "medium",
                    "speed": 30,
                    "age": {"adult": 18, "max": 100},
                    "languages": ["common"],
                    "features": [
                        {
                            "name": "Дополнительная мастерство",
                            "description": "Вы получаете дополнительное мастерство",
                            "mechanics": {"type": "skill_bonus", "count": 1}
                        }
                    ],
                    "subraces": {
                        "variant_human": {
                            "name": "Вариантный человек",
                            "description": "Человек с дополнительными навыками",
                            "ability_bonuses": {"strength": 1, "dexterity": 1},
                            "ability_bonuses_description": "+2 к двум характеристикам",
                            "features": [
                                {
                                    "name": "Мастерство",
                                    "description": "Вы получаете одно мастерство",
                                    "mechanics": {"type": "proficiency", "count": 1}
                                }
                            ],
                            "inherit_base_abilities": False
                        }
                    },
                    "allow_base_race_choice": True
                },
                "elf": {
                    "name": "Эльф",
                    "description": "Изящное долгоживущее существо",
                    "ability_bonuses": {"dexterity": 2},
                    "ability_bonuses_description": "+2 к Ловкости",
                    "size": "medium",
                    "speed": 30,
                    "languages": ["elvish", "common"],
                    "features": [
                        {
                            "name": "Темное зрение",
                            "description": "Вы можете видеть в условиях слабого освещения",
                            "mechanics": {"type": "darkvision", "range": 60}
                        }
                    ]
                }
            }
        }

    def test_init_with_custom_path(self) -> None:
        """Тест инициализации с кастомным путем."""
        test_data = self.create_test_race_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            loader = RaceLoader(Path(f.name))
            
            assert loader.data_path == Path(f.name)
            
            # Очистка
            Path(f.name).unlink()

    def test_get_default_data_path(self) -> None:
        """Тест получения пути по умолчанию."""
        loader = RaceLoader()
        path = loader._get_default_data_path()
        
        assert path.name == "races.yaml"
        assert path.parent.name == "data"

    def test_load_races_success(self) -> None:
        """Тест успешной загрузки рас."""
        test_data = self.create_test_race_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            loader = RaceLoader(Path(f.name))
            races = loader.load_races()
            
            assert len(races) == 2
            assert "human" in races
            assert "elf" in races
            
            # Проверяем человека
            human = races["human"]
            assert human.name == "Человек"
            assert human.description == "Универсальная и адаптивная раса"
            assert human.ability_bonuses == {"strength": 1, "dexterity": 1, "constitution": 1, "intelligence": 1, "wisdom": 1, "charisma": 1}
            assert human.size == Size.MEDIUM
            assert human.speed == 30
            assert len(human.features) == 1
            assert len(human.subraces) == 1
            assert human.allow_base_race_choice is True
            
            # Проверяем эльфа
            elf = races["elf"]
            assert elf.name == "Эльф"
            assert elf.ability_bonuses == {"dexterity": 2}
            assert len(elf.features) == 1
            assert len(elf.subraces) == 0
            
            # Очистка
            Path(f.name).unlink()

    def test_create_race_from_data(self) -> None:
        """Тест создания расы из данных."""
        race_data = {
            "name": "Тестовая раса",
            "description": "Тестовое описание",
            "ability_bonuses": {"strength": 2},
            "ability_bonuses_description": "+2 к Силе",
            "size": "small",
            "speed": 25,
            "age": {"adult": 20, "max": 200},
            "languages": ["common", "test"],
            "features": [
                {
                    "name": "Тестовая черта",
                    "description": "Описание черты",
                    "mechanics": {"type": "test"}
                }
            ],
            "subraces": {
                "test_subrace": {
                    "name": "Тестовая подраса",
                    "description": "Описание подрасы",
                    "ability_bonuses": {"dexterity": 1},
                    "inherit_base_abilities": False
                }
            },
            "allow_base_race_choice": False
        }
        
        loader = RaceLoader()
        race = loader._create_race_from_data("test_race", race_data)
        
        assert race.name == "Тестовая раса"
        assert race.description == "Тестовое описание"
        assert race.ability_bonuses == {"strength": 2}
        assert race.ability_bonuses_description == "+2 к Силе"
        assert race.size == Size.SMALL
        assert race.speed == 25
        assert race.age == {"adult": 20, "max": 200}
        assert race.languages == ["common", "test"]
        assert len(race.features) == 1
        assert len(race.subraces) == 1
        assert race.allow_base_race_choice is False
        
        # Проверяем черту
        feature = race.features[0]
        assert feature.name == "Тестовая черта"
        assert feature.description == "Описание черты"
        assert feature.mechanics == {"type": "test"}
        
        # Проверяем подрасу
        subrace = race.subraces["test_subrace"]
        assert subrace.name == "Тестовая подраса"
        assert subrace.description == "Описание подрасы"
        assert subrace.ability_bonuses == {"dexterity": 1}
        assert subrace.inherit_base_abilities is False

    def test_create_features_list(self) -> None:
        """Тест создания списка черт."""
        features_data = [
            {
                "name": "Черта 1",
                "description": "Описание 1",
                "mechanics": {"type": "bonus", "value": 1}
            },
            {
                "name": "Черта 2",
                "description": "Описание 2",
                "mechanics": {"type": "skill", "skills": ["stealth"]}
            }
        ]
        
        loader = RaceLoader()
        features = loader._create_features_list(features_data)
        
        assert len(features) == 2
        
        assert features[0].name == "Черта 1"
        assert features[0].description == "Описание 1"
        assert features[0].mechanics == {"type": "bonus", "value": 1}
        
        assert features[1].name == "Черта 2"
        assert features[1].description == "Описание 2"
        assert features[1].mechanics == {"type": "skill", "skills": ["stealth"]}

    def test_create_subraces_dict(self) -> None:
        """Тест создания словаря подрас."""
        subraces_data = {
            "subrace1": {
                "name": "Подраса 1",
                "description": "Описание подрасы 1",
                "ability_bonuses": {"strength": 1},
                "ability_bonuses_description": "+1 к Силе",
                "languages": ["common"],
                "features": [
                    {
                        "name": "Черта подрасы",
                        "description": "Описание черты",
                        "mechanics": {"type": "trait"}
                    }
                ],
                "inherit_base_abilities": False
            },
            "subrace2": {
                # Минимальные данные
                "description": "Описание подрасы 2"
            }
        }
        
        loader = RaceLoader()
        subraces = loader._create_subraces_dict(subraces_data)
        
        assert len(subraces) == 2
        assert "subrace1" in subraces
        assert "subrace2" in subraces
        
        # Проверяем первую подрасу
        subrace1 = subraces["subrace1"]
        assert subrace1.name == "Подраса 1"
        assert subrace1.description == "Описание подрасы 1"
        assert subrace1.ability_bonuses == {"strength": 1}
        assert subrace1.ability_bonuses_description == "+1 к Силе"
        assert subrace1.languages == ["common"]
        assert len(subrace1.features) == 1
        assert subrace1.inherit_base_abilities is False
        
        # Проверяем вторую подрасу (минимальные данные)
        subrace2 = subraces["subrace2"]
        assert subrace2.name == "subrace2"  # Используется ID как имя
        assert subrace2.description == "Описание подрасы 2"
        assert subrace2.ability_bonuses == {}
        assert subrace2.ability_bonuses_description == ""
        assert subrace2.languages == []
        assert len(subrace2.features) == 0
        assert subrace2.inherit_base_abilities is True  # Значение по умолчанию

    def test_get_size_from_string_valid(self) -> None:
        """Тест получения размера из валидной строки."""
        loader = RaceLoader()
        
        assert loader._get_size_from_string("tiny") == Size.TINY
        assert loader._get_size_from_string("small") == Size.SMALL
        assert loader._get_size_from_string("medium") == Size.MEDIUM
        assert loader._get_size_from_string("large") == Size.LARGE
        assert loader._get_size_from_string("huge") == Size.HUGE
        assert loader._get_size_from_string("gargantuan") == Size.GARGANTUAN
        assert loader._get_size_from_string("colossal") == Size.COLOSSAL

    def test_get_size_from_string_invalid(self) -> None:
        """Тест получения размера из невалидной строки."""
        loader = RaceLoader()
        
        assert loader._get_size_from_string("invalid") == Size.MEDIUM
        assert loader._get_size_from_string("unknown") == Size.MEDIUM
        assert loader._get_size_from_string("") == Size.MEDIUM

    def test_get_race(self) -> None:
        """Тест получения расы по ID."""
        test_data = self.create_test_race_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            loader = RaceLoader(Path(f.name))
            
            # Существующая раса
            human = loader.get_race("human")
            assert human is not None
            assert human.name == "Человек"
            
            # Несуществующая раса
            unknown = loader.get_race("unknown")
            assert unknown is None
            
            # Очистка
            Path(f.name).unlink()

    def test_get_all_race_names(self) -> None:
        """Тест получения всех названий рас."""
        test_data = self.create_test_race_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            loader = RaceLoader(Path(f.name))
            names = loader.get_all_race_names()
            
            assert len(names) == 2
            assert "Человек" in names
            assert "Эльф" in names
            
            # Очистка
            Path(f.name).unlink()

    def test_load_races_file_not_found(self) -> None:
        """Тест загрузки рас из несуществующего файла."""
        loader = RaceLoader(Path("nonexistent.yaml"))
        
        with pytest.raises(FileNotFoundError):
            loader.load_races()

    def test_load_races_invalid_yaml(self) -> None:
        """Тест загрузки рас из невалидного YAML."""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            loader = RaceLoader(Path(f.name))
            
            with pytest.raises(yaml.YAMLError):
                loader.load_races()
            
            # Очистка
            Path(f.name).unlink()
