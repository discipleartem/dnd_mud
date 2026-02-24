#!/usr/bin/env python3
"""Глобальные фикстуры для pytest."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import pytest
import yaml

from src.services.language_service import Language, LanguageMechanics
from src.ui.entities.character import Size
from src.ui.entities.race import Feature, Race, SubRace


@pytest.fixture
def temp_yaml_file():
    """Фикстура для создания временного YAML файла."""
    def _create_temp_yaml(content: dict[str, Any]) -> Path:
        temp_file = NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8")
        yaml.dump(content, temp_file, allow_unicode=True)
        temp_file.flush()
        temp_file.close()
        
        # Очистка после теста
        yield Path(temp_file.name)
        Path(temp_file.name).unlink()
    
    return _create_temp_yaml


@pytest.fixture
def sample_language():
    """Фикстура для создания образца языка."""
    return Language(
        code="common",
        type="standard",
        difficulty="easy",
        localization_keys={"name": "language.common.name"},
        mechanics=LanguageMechanics(
            is_default=True,
            learnable_by_all=True
        ),
        fallback_data={"name": "Common"}
    )


@pytest.fixture
def sample_languages():
    """Фикстура для создания набора образцов языков."""
    return {
        "common": Language(
            code="common",
            type="standard",
            difficulty="easy",
            localization_keys={"name": "language.common.name"},
            mechanics=LanguageMechanics(is_default=True, learnable_by_all=True),
            fallback_data={"name": "Common"}
        ),
        "elvish": Language(
            code="elvish",
            type="standard",
            difficulty="medium",
            localization_keys={"name": "language.elvish.name"},
            mechanics=LanguageMechanics(learnable_by=["elf", "half_elf"]),
            fallback_data={"name": "Elvish"}
        ),
        "draconic": Language(
            code="draconic",
            type="exotic",
            difficulty="hard",
            localization_keys={"name": "language.draconic.name"},
            mechanics=LanguageMechanics(magic_language=True, learnable_by_special=["wizard"]),
            fallback_data={"name": "Draconic"}
        )
    }


@pytest.fixture
def sample_feature():
    """Фикстура для создания образца черты."""
    return Feature(
        name="Темное зрение",
        description="Вы можете видеть в условиях слабого освещения",
        mechanics={"type": "darkvision", "range": 60}
    )


@pytest.fixture
def sample_features():
    """Фикстура для создания набора образцов черт."""
    return [
        Feature(
            name="Темное зрение",
            description="Вы можете видеть в условиях слабого освещения",
            mechanics={"type": "darkvision", "range": 60}
        ),
        Feature(
            name="Мастерство",
            description="Вы получаете дополнительное мастерство",
            mechanics={"type": "proficiency", "count": 1}
        ),
        Feature(
            name="Устойчивость к магии",
            description="Вы получаете преимущество против заклинаний",
            mechanics={"type": "magic_resistance", "advantage": True}
        )
    ]


@pytest.fixture
def sample_subrace():
    """Фикстура для создания образца подрасы."""
    return SubRace(
        name="Высший эльф",
        description="Магически одаренный эльф",
        ability_bonuses={"intelligence": 1},
        ability_bonuses_description="+1 к Интеллекту",
        languages=["elvish", "common"],
        features=[
            Feature(
                name="Заклинание",
                description="Вы знаете одно канtrip",
                mechanics={"type": "cantrip", "count": 1}
            )
        ],
        inherit_base_abilities=True
    )


@pytest.fixture
def sample_race(sample_features, sample_subrace):
    """Фикстура для создания образца расы."""
    return Race(
        name="Эльф",
        description="Изящное долгоживущее существо",
        ability_bonuses={"dexterity": 2},
        ability_bonuses_description="+2 к Ловкости",
        size=Size.MEDIUM,
        speed=30,
        age={"adult": 100, "max": 750},
        languages=["elvish", "common"],
        features=sample_features,
        subraces={"high_elf": sample_subrace},
        allow_base_race_choice=True
    )


@pytest.fixture
def sample_races():
    """Фикстура для создания набора образцов рас."""
    human_subrace = SubRace(
        name="Вариантный человек",
        description="Человек с дополнительными навыками",
        ability_bonuses={"strength": 1, "dexterity": 1},
        ability_bonuses_description="+2 к двум характеристикам",
        inherit_base_abilities=False
    )
    
    return {
        "human": Race(
            name="Человек",
            description="Универсальная и адаптивная раса",
            ability_bonuses={"strength": 1, "dexterity": 1, "constitution": 1, "intelligence": 1, "wisdom": 1, "charisma": 1},
            ability_bonuses_description="+1 ко всем характеристикам",
            size=Size.MEDIUM,
            speed=30,
            age={"adult": 18, "max": 100},
            languages=["common"],
            features=[
                Feature(
                    name="Дополнительное мастерство",
                    description="Вы получаете дополнительное мастерство",
                    mechanics={"type": "skill_bonus", "count": 1}
                )
            ],
            subraces={"variant": human_subrace},
            allow_base_race_choice=True
        ),
        "elf": Race(
            name="Эльф",
            description="Изящное долгоживущее существо",
            ability_bonuses={"dexterity": 2},
            ability_bonuses_description="+2 к Ловкости",
            size=Size.MEDIUM,
            speed=30,
            age={"adult": 100, "max": 750},
            languages=["elvish", "common"],
            features=[
                Feature(
                    name="Темное зрение",
                    description="Вы можете видеть в условиях слабого освещения",
                    mechanics={"type": "darkvision", "range": 60}
                )
            ],
            subraces={},
            allow_base_race_choice=False
        ),
        "dwarf": Race(
            name="Дварф",
            description="Стойкий и выносливый воин",
            ability_bonuses={"constitution": 2},
            ability_bonuses_description="+2 к Телосложению",
            size=Size.MEDIUM,
            speed=25,
            age={"adult": 50, "max": 350},
            languages=["common", "dwarvish"],
            features=[
                Feature(
                    name="Стойкость дварфов",
                    description="Вы получаете преимущество против ядов",
                    mechanics={"type": "poison_resistance", "advantage": True}
                )
            ],
            subraces={},
            allow_base_race_choice=False
        )
    }


@pytest.fixture
def sample_language_data():
    """Фикстура для создания образца данных языков."""
    return {
        "language_metadata": {
            "types": {
                "standard": "Standard",
                "exotic": "Exotic",
                "secret": "Secret"
            },
            "difficulties": {
                "easy": "Easy",
                "medium": "Medium",
                "hard": "Hard"
            }
        },
        "languages": {
            "common": {
                "code": "common",
                "type": "standard",
                "difficulty": "easy",
                "localization_keys": {"name": "language.common.name"},
                "mechanics": {"is_default": True, "learnable_by_all": True},
                "fallback_data": {"name": "Common"}
            },
            "elvish": {
                "code": "elvish",
                "type": "standard",
                "difficulty": "medium",
                "localization_keys": {"name": "language.elvish.name"},
                "mechanics": {"learnable_by": ["elf", "half_elf"]},
                "fallback_data": {"name": "Elvish"}
            }
        }
    }


@pytest.fixture
def sample_race_data():
    """Фикстура для создания образца данных рас."""
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
                        "name": "Дополнительное мастерство",
                        "description": "Вы получаете дополнительное мастерство",
                        "mechanics": {"type": "skill_bonus", "count": 1}
                    }
                ],
                "subraces": {
                    "variant": {
                        "name": "Вариантный человек",
                        "description": "Человек с дополнительными навыками",
                        "ability_bonuses": {"strength": 1, "dexterity": 1},
                        "ability_bonuses_description": "+2 к двум характеристикам",
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
                ],
                "subraces": {},
                "allow_base_race_choice": False
            }
        }
    }


@pytest.fixture
def mock_i18n():
    """Фикстура для мока i18n функций."""
    from unittest.mock import Mock
    
    mock_t = Mock()
    mock_t.return_value = "Translated text"
    
    return mock_t


@pytest.fixture
def temp_locale_file():
    """Фикстура для создания временного файла локализации."""
    def _create_locale_file(content: dict[str, Any], language: str = "test") -> Path:
        temp_file = NamedTemporaryFile(mode="w", suffix=f".{language}.yaml", delete=False, encoding="utf-8")
        yaml.dump(content, temp_file, allow_unicode=True)
        temp_file.flush()
        temp_file.close()
        
        # Очистка после теста
        yield Path(temp_file.name)
        Path(temp_file.name).unlink()
    
    return _create_locale_file


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Автоматическая очистка временных файлов после каждого теста."""
    yield
    # Здесь можно добавить логику очистки если необходимо


# Маркеры для тестов теперь определяются в pyproject.toml
# в секции [tool.pytest.ini_options]
