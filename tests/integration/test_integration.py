#!/usr/bin/env python3
"""Интеграционные тесты для всего проекта."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from unittest.mock import patch

import pytest
import yaml

from src.services.language_service import LanguageService
from src.ui.entities.character import Character
from src.ui.entities.race import RaceLoader
from src.ui.services.language_display_service import LanguageDisplayService
from src.ui.services.race_display_service import RaceDisplayService


@pytest.mark.integration
class TestRaceLanguageIntegration:
    """Интеграционные тесты для рас и языков."""

    def create_complete_test_data(self) -> dict[str, Any]:
        """Создать полные тестовые данные для рас и языков."""
        return {
            "races": {
                "human": {
                    "name": "Человек",
                    "description": "Универсальная и адаптивная раса",
                    "ability_bonuses": {
                        "strength": 1,
                        "dexterity": 1,
                        "constitution": 1,
                        "intelligence": 1,
                        "wisdom": 1,
                        "charisma": 1
                    },
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
                    "age": {"adult": 100, "max": 750},
                    "languages": ["elvish", "common"],
                    "features": [
                        {
                            "name": "Темное зрение",
                            "description": (
                                "Вы можете видеть в условиях "
                                "слабого освещения"
                            ),
                            "mechanics": {"type": "darkvision", "range": 60}
                        }
                    ],
                    "subraces": {
                        "high_elf": {
                            "name": "Высший эльф",
                            "description": "Магически одаренный эльф",
                            "ability_bonuses": {"intelligence": 1},
                            "ability_bonuses_description": "+1 к Интеллекту",
                            "languages": ["elvish"],
                            "features": [
                                {
                                    "name": "Заклинание",
                                    "description": "Вы знаете одно канtrip",
                                    "mechanics": {"type": "cantrip", "count": 1}
                                }
                            ],
                            "inherit_base_abilities": True
                        }
                    },
                    "allow_base_race_choice": False
                }
            },
            "language_metadata": {
                "types": {
                    "standard": "Standard",
                    "exotic": "Exotic"
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

    def test_complete_race_language_workflow(self) -> None:
        """Тест полного рабочего процесса с расами и языками."""
        test_data = self.create_complete_test_data()

        # Создаем временные файлы
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as races_file:
            yaml.dump({"races": test_data["races"]}, races_file)
            races_file.flush()

            with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as languages_file:
                yaml.dump(
                    {
                        "language_metadata": test_data["language_metadata"],
                        "languages": test_data["languages"]
                    },
                    languages_file
                )
                languages_file.flush()

                try:
                    # Инициализируем сервисы
                    race_loader = RaceLoader(Path(races_file.name))
                    language_service = LanguageService(Path(languages_file.name))

                    # Загружаем расы
                    races = race_loader.load_races()
                    assert len(races) == 2
                    assert "human" in races
                    assert "elf" in races

                    # Загружаем языки
                    languages = language_service.get_all_languages()
                    assert len(languages) == 2
                    assert "common" in languages
                    assert "elvish" in languages

                    # Проверяем интеграцию рас и языков
                    human = races["human"]
                    elf = races["elf"]

                    # Проверяем языки человека
                    assert human.languages == ["common"]
                    common_lang = language_service.get_language_by_code("common")
                    assert common_lang is not None

                    # Проверяем языки эльфа
                    assert elf.languages == ["elvish", "common"]
                    elvish_lang = language_service.get_language_by_code("elvish")
                    assert elvish_lang is not None

                    # Проверяем доступность языков для рас
                    human_available = language_service.get_available_languages_for_race("human")
                    elf_available = language_service.get_available_languages_for_race("elf")

                    # Человек должен иметь доступ к common (learnable_by_all=True)
                    assert common_lang in human_available

                    # Эльф должен иметь доступ к elvish (learnable_by=["elf"]) и common
                    assert elvish_lang in elf_available
                    assert common_lang in elf_available

                    # Проверяем подрасы
                    human_variant = human.subraces["variant"]
                    elf_high = elf.subraces["high_elf"]

                    # Проверяем бонусы способностей
                    human_bonuses = human.get_effective_ability_bonuses(human_variant)
                    assert human_bonuses == {"strength": 1, "dexterity": 1}

                    elf_bonuses = elf.get_effective_ability_bonuses(elf_high)
                    assert elf_bonuses == {"dexterity": 2, "intelligence": 1}

                finally:
                    # Очистка
                    Path(races_file.name).unlink()
                    Path(languages_file.name).unlink()

    @patch('src.ui.entities.race.t')
    @patch('src.ui.services.language_display_service.t')
    def test_display_services_integration(self, mock_lang_t, mock_race_t) -> None:
        """Тест интеграции сервисов отображения."""
        test_data = self.create_complete_test_data()

        # Настройка моков
        mock_lang_t.side_effect = lambda key: {
            "language.common.name": "Общий",
            "language.elvish.name": "Эльфийский",
            "language.types.standard": "Стандартный",
            "language.difficulties.easy": "Легкая",
            "language.difficulties.medium": "Средняя"
        }.get(key, key)

        mock_race_t.side_effect = lambda key: {
            "new_game.details_section.features_label": "Черты:",
            "new_game.details_section.abilities_label": "Бонусы:"
        }.get(key, key)

        # Создаем временные файлы
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as races_file:
            yaml.dump({"races": test_data["races"]}, races_file)
            races_file.flush()

            with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as languages_file:
                yaml.dump(
                    {
                        "language_metadata": test_data["language_metadata"],
                        "languages": test_data["languages"]
                    },
                    languages_file
                )
                languages_file.flush()

                try:
                    # Инициализируем сервисы
                    race_loader = RaceLoader(Path(races_file.name))
                    language_service = LanguageService(Path(languages_file.name))

                    # Загружаем данные
                    races = race_loader.load_races()
                    languages = language_service.get_all_languages()

                    # Тестируем отображение языков
                    common_lang = languages["common"]
                    elvish_lang = languages["elvish"]

                    common_name = LanguageDisplayService.get_language_name(common_lang)
                    elvish_name = LanguageDisplayService.get_language_name(elvish_lang)

                    assert common_name == "Общий"
                    assert elvish_name == "Эльфийский"

                    common_type = LanguageDisplayService.get_language_type_name(common_lang)
                    elvish_difficulty = LanguageDisplayService.get_language_difficulty_name(elvish_lang)

                    assert common_type == "Стандартный"
                    assert elvish_difficulty == "Средняя"

                    # Тестируем отображение рас
                    elf = races["elf"]

                    with patch('builtins.print') as mock_print:
                        # Отображаем черты
                        RaceDisplayService.display_features_with_emoji(elf.features)

                        # Отображаем бонусы
                        RaceDisplayService.display_abilities_description(elf.ability_bonuses_description)

                        # Проверяем вызовы print
                        print_calls = [str(call) for call in mock_print.call_args_list]

                        # Отладочный вывод
                        print(f"DEBUG: Print calls: {print_calls}")

                        # Проверяем черты (более гибкая проверка)
                        features_found = any("Темное зрение" in call for call in print_calls)
                        assert features_found, f"Expected 'Темное зрение' in print calls, got: {print_calls}"

                        # Проверяем наличие эмодзи для черты
                        emoji_found = any("🌙" in call for call in print_calls)
                        assert emoji_found, f"Expected '🌙' emoji in print calls, got: {print_calls}"

                        # Проверяем бонусы
                        bonuses_found = any("+2 к Ловкости" in call for call in print_calls)
                        assert bonuses_found, f"Expected '+2 к Ловкости' in print calls, got: {print_calls}"

                finally:
                    # Очистка
                    Path(races_file.name).unlink()
                    Path(languages_file.name).unlink()


@pytest.mark.integration
class TestCharacterCreationIntegration:
    """Интеграционные тесты для создания персонажа."""

    def test_complete_character_creation(self) -> None:
        """Тест полного процесса создания персонажа."""
        test_data = {
            "races": {
                "human": {
                    "name": "Человек",
                    "description": "Универсальная раса",
                    "ability_bonuses": {"strength": 1, "dexterity": 1},
                    "ability_bonuses_description": "+1 к Силе и Ловкости",
                    "size": "medium",
                    "speed": 30,
                    "languages": ["common"],
                    "features": [
                        {
                            "name": "Мастерство",
                            "description": "Дополнительное мастерство",
                            "mechanics": {"type": "proficiency"}
                        }
                    ],
                    "subraces": {}
                }
            },
            "language_metadata": {"types": {}, "difficulties": {}},
            "languages": {
                "common": {
                    "code": "common",
                    "type": "standard",
                    "difficulty": "easy",
                    "localization_keys": {},
                    "mechanics": {"learnable_by_all": True},
                    "fallback_data": {"name": "Common"}
                }
            }
        }

        # Создаем временные файлы
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as races_file:
            yaml.dump({"races": test_data["races"]}, races_file)
            races_file.flush()

            with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as languages_file:
                yaml.dump(
                    {
                        "language_metadata": test_data["language_metadata"],
                        "languages": test_data["languages"]
                    },
                    languages_file
                )
                languages_file.flush()

                try:
                    # Инициализируем сервисы
                    race_loader = RaceLoader(Path(races_file.name))
                    language_service = LanguageService(Path(languages_file.name))

                    # Создаем персонажа
                    character = Character(name="Тестовый персонаж")

                    # Выбираем расу
                    races = race_loader.load_races()
                    human_race = races["human"]
                    character.race = human_race

                    # Проверяем базовые свойства персонажа
                    assert character.name == "Тестовый персонаж"
                    assert character.race is human_race
                    assert character.size == human_race.size

                    # Проверяем бонусы от расы
                    effective_bonuses = human_race.get_effective_ability_bonuses()
                    assert effective_bonuses == {"strength": 1, "dexterity": 1}

                    # Проверяем языки расы
                    assert human_race.languages == ["common"]
                    common_lang = language_service.get_language_by_code("common")
                    assert common_lang is not None

                    # Проверяем доступные языки для расы персонажа
                    available_languages = language_service.get_available_languages_for_race("human")
                    assert common_lang in available_languages

                    # Проверяем черты расы
                    assert len(human_race.features) == 1
                    feature = human_race.features[0]
                    assert feature.name == "Мастерство"
                    assert feature.description == "Дополнительное мастерство"

                finally:
                    # Очистка
                    Path(races_file.name).unlink()
                    Path(languages_file.name).unlink()


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Интеграционные тесты производительности."""

    def test_large_dataset_loading(self) -> None:
        """Тест загрузки больших наборов данных."""
        # Создаем большой набор данных
        large_races_data: dict[str, Any] = {"races": {}}
        large_languages_data: dict[str, Any] = {
            "language_metadata": {"types": {}, "difficulties": {}},
            "languages": {}
        }

        # Генерируем много рас
        for i in range(100):
            race_id = f"race_{i}"
            large_races_data["races"][race_id] = {
                "name": f"Раса {i}",
                "description": f"Описание расы {i}",
                "ability_bonuses": {"strength": i % 3, "dexterity": i % 2},
                "size": "medium",
                "speed": 30,
                "languages": [f"lang_{i % 10}"],
                "features": [
                    {
                        "name": f"Черта {i}",
                        "description": f"Описание черты {i}",
                        "mechanics": {"type": "test", "value": i}
                    }
                ],
                "subraces": {}
            }

        # Генерируем много языков
        for i in range(20):
            lang_id = f"lang_{i}"
            large_languages_data["languages"][lang_id] = {
                "code": lang_id,
                "type": "standard",
                "difficulty": "easy",
                "localization_keys": {},
                "mechanics": {"learnable_by_all": i % 5 == 0},
                "fallback_data": {"name": f"Language {i}"}
            }

        # Создаем временные файлы
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as races_file:
            yaml.dump(large_races_data, races_file)
            races_file.flush()

            with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as languages_file:
                yaml.dump(large_languages_data, languages_file)
                languages_file.flush()

                try:
                    import time

                    # Замеряем время загрузки рас
                    start_time = time.time()
                    race_loader = RaceLoader(Path(races_file.name))
                    races = race_loader.load_races()
                    races_time = time.time() - start_time

                    # Замеряем время загрузки языков
                    start_time = time.time()
                    language_service = LanguageService(Path(languages_file.name))
                    languages = language_service.get_all_languages()
                    languages_time = time.time() - start_time

                    # Проверяем результаты
                    assert len(races) == 100
                    assert len(languages) == 20

                    # Проверяем производительность (должно быть достаточно быстро)
                    assert races_time < 1.0, f"Loading races took too long: {races_time}s"
                    assert languages_time < 0.5, f"Loading languages took too long: {languages_time}s"

                    # Проверяем работу с большими данными
                    for _race_id, race in races.items():
                        assert race.name.startswith("Раса ")
                        assert len(race.features) == 1

                    for _lang_id, language in languages.items():
                        assert language.code.startswith("lang_")

                finally:
                    # Очистка
                    Path(races_file.name).unlink()
                    Path(languages_file.name).unlink()


@pytest.mark.integration
@pytest.mark.regression
class TestRegressionIntegration:
    """Регрессионные интеграционные тесты."""

    def test_yaml_loading_consistency(self) -> None:
        """Тест консистентности загрузки YAML."""
        test_data = {
            "races": {
                "test_race": {
                    "name": "Тестовая раса",
                    "description": "Тестовое описание",
                    "ability_bonuses": {"strength": 2},
                    "size": "medium",
                    "speed": 30,
                    "languages": ["common"],
                    "features": [],
                    "subraces": {}
                }
            }
        }

        # Создаем временный файл
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()

            try:
                # Загружаем данные несколько раз
                loader1 = RaceLoader(Path(f.name))
                loader2 = RaceLoader(Path(f.name))

                races1 = loader1.load_races()
                races2 = loader2.load_races()

                # Проверяем консистентность
                assert len(races1) == len(races2) == 1

                race1 = races1["test_race"]
                race2 = races2["test_race"]

                assert race1.name == race2.name
                assert race1.description == race2.description
                assert race1.ability_bonuses == race2.ability_bonuses
                assert race1.size == race2.size
                assert race1.speed == race2.speed
                assert race1.languages == race2.languages

            finally:
                Path(f.name).unlink()

    def test_language_service_state_isolation(self) -> None:
        """Тест изоляции состояния LanguageService."""
        test_data1 = {
            "language_metadata": {"types": {}, "difficulties": {}},
            "languages": {
                "lang1": {
                    "code": "lang1",
                    "type": "standard",
                    "difficulty": "easy",
                    "localization_keys": {},
                    "mechanics": {},
                    "fallback_data": {"name": "Language 1"}
                }
            }
        }

        test_data2 = {
            "language_metadata": {"types": {}, "difficulties": {}},
            "languages": {
                "lang2": {
                    "code": "lang2",
                    "type": "exotic",
                    "difficulty": "hard",
                    "localization_keys": {},
                    "mechanics": {},
                    "fallback_data": {"name": "Language 2"}
                }
            }
        }

        # Создаем временные файлы
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f1:
            yaml.dump(test_data1, f1)
            f1.flush()

            with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f2:
                yaml.dump(test_data2, f2)
                f2.flush()

                try:
                    # Создаем два экземпляра сервиса
                    service1 = LanguageService(Path(f1.name))
                    service2 = LanguageService(Path(f2.name))

                    # Проверяем изоляцию
                    languages1 = service1.get_all_languages()
                    languages2 = service2.get_all_languages()

                    assert len(languages1) == 1
                    assert len(languages2) == 1
                    assert "lang1" in languages1
                    assert "lang2" in languages2
                    assert "lang2" not in languages1
                    assert "lang1" not in languages2

                finally:
                    Path(f1.name).unlink()
                    Path(f2.name).unlink()
