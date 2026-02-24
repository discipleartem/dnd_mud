#!/usr/bin/env python3
"""Тесты для модуля language_service."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import pytest
import yaml

from src.services.language_service import (
    Language,
    LanguageMechanics,
    LanguageService,
    get_language_service,
)


class TestLanguageMechanics:
    """Тесты для класса LanguageMechanics."""

    def test_language_mechanics_init(self) -> None:
        """Тест инициализации LanguageMechanics."""
        mechanics = LanguageMechanics(
            script="Common",
            is_default=True,
            learnable_by_all=False,
            learnable_by=["human", "elf"],
            race_bonus=["dwarf"],
            learnable_by_special=["wizard"],
            magic_language=True,
            secret_language=False,
            evil_alignment=False,
            good_alignment=True,
            lawful_evil_alignment=False,
        )
        
        assert mechanics.script == "Common"
        assert mechanics.is_default is True
        assert mechanics.learnable_by_all is False
        assert mechanics.learnable_by == ["human", "elf"]
        assert mechanics.race_bonus == ["dwarf"]
        assert mechanics.learnable_by_special == ["wizard"]
        assert mechanics.magic_language is True
        assert mechanics.secret_language is False
        assert mechanics.evil_alignment is False
        assert mechanics.good_alignment is True
        assert mechanics.lawful_evil_alignment is False

    def test_language_mechanics_default_values(self) -> None:
        """Тест значений по умолчанию для LanguageMechanics."""
        mechanics = LanguageMechanics()
        
        assert mechanics.script == ""
        assert mechanics.is_default is False
        assert mechanics.learnable_by_all is False
        assert mechanics.learnable_by == []
        assert mechanics.race_bonus == []
        assert mechanics.learnable_by_special == []
        assert mechanics.magic_language is False
        assert mechanics.secret_language is False
        assert mechanics.evil_alignment is False
        assert mechanics.good_alignment is False
        assert mechanics.lawful_evil_alignment is False


class TestLanguage:
    """Тесты для класса Language."""

    def test_language_init(self) -> None:
        """Тест инициализации Language."""
        mechanics = LanguageMechanics(
            learnable_by_all=True,
            learnable_by=["human"],
            learnable_by_special=["wizard"]
        )
        
        language = Language(
            code="common",
            type="standard",
            difficulty="easy",
            localization_keys={"name": "language.common.name"},
            mechanics=mechanics,
            fallback_data={"name": "Common"},
        )
        
        assert language.code == "common"
        assert language.type == "standard"
        assert language.difficulty == "easy"
        assert language.localization_keys == {"name": "language.common.name"}
        assert language.mechanics == mechanics
        assert language.fallback_data == {"name": "Common"}

    def test_language_is_available_for_race(self) -> None:
        """Тест проверки доступности языка для расы."""
        # Язык доступный всем
        mechanics_all = LanguageMechanics(learnable_by_all=True)
        lang_all = Language("common", "standard", "easy", mechanics=mechanics_all)
        assert lang_all.is_available_for_race("human") is True
        assert lang_all.is_available_for_race("elf") is True
        assert lang_all.is_available_for_race("unknown") is True
        
        # Язык доступный конкретным расам
        mechanics_specific = LanguageMechanics(
            learnable_by=["human", "elf"],
            race_bonus=["dwarf"]
        )
        lang_specific = Language("elvish", "standard", "medium", mechanics=mechanics_specific)
        assert lang_specific.is_available_for_race("human") is True
        assert lang_specific.is_available_for_race("elf") is True
        assert lang_specific.is_available_for_race("dwarf") is True
        assert lang_specific.is_available_for_race("orc") is False
        
        # Язык недоступный никому
        mechanics_none = LanguageMechanics()
        lang_none = Language("secret", "secret", "hard", mechanics=mechanics_none)
        assert lang_none.is_available_for_race("human") is False
        assert lang_none.is_available_for_race("elf") is False

    def test_language_is_available_for_class(self) -> None:
        """Тест проверки доступности языка для класса."""
        mechanics = LanguageMechanics(learnable_by_special=["wizard", "cleric"])
        language = Language("draconic", "magic", "hard", mechanics=mechanics)
        
        assert language.is_available_for_class("wizard") is True
        assert language.is_available_for_class("cleric") is True
        assert language.is_available_for_class("fighter") is False
        assert language.is_available_for_class("rogue") is False


class TestLanguageService:
    """Тесты для класса LanguageService."""

    def create_test_language_data(self) -> dict[str, Any]:
        """Создать тестовые данные языков."""
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
                    "mechanics": {
                        "is_default": True,
                        "learnable_by_all": True
                    },
                    "fallback_data": {"name": "Common"}
                },
                "elvish": {
                    "code": "elvish",
                    "type": "standard",
                    "difficulty": "medium",
                    "localization_keys": {"name": "language.elvish.name"},
                    "mechanics": {
                        "learnable_by": ["elf", "half_elf"],
                        "race_bonus": ["human"]
                    },
                    "fallback_data": {"name": "Elvish"}
                },
                "draconic": {
                    "code": "draconic",
                    "type": "exotic",
                    "difficulty": "hard",
                    "localization_keys": {"name": "language.draconic.name"},
                    "mechanics": {
                        "magic_language": True,
                        "learnable_by_special": ["wizard", "sorcerer"]
                    },
                    "fallback_data": {"name": "Draconic"}
                },
                "thieves_cant": {
                    "code": "thieves_cant",
                    "type": "secret",
                    "difficulty": "hard",
                    "localization_keys": {"name": "language.thieves_cant.name"},
                    "mechanics": {
                        "secret_language": True,
                        "learnable_by_special": ["rogue"]
                    },
                    "fallback_data": {"name": "Thieves' Cant"}
                }
            }
        }

    def test_language_service_init_with_custom_path(self) -> None:
        """Тест инициализации с кастомным путем."""
        test_data = self.create_test_language_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            assert service.data_path == Path(f.name)
            assert len(service._languages) == 4
            assert "common" in service._languages
            assert "elvish" in service._languages
            assert "draconic" in service._languages
            assert "thieves_cant" in service._languages
            
            # Очистка
            Path(f.name).unlink()

    def test_language_service_load_error(self) -> None:
        """Тест обработки ошибок загрузки."""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()
            
            with pytest.raises(RuntimeError, match="Ошибка загрузки данных языков"):
                LanguageService(Path(f.name))
            
            # Очистка
            Path(f.name).unlink()

    def test_get_all_languages(self) -> None:
        """Тест получения всех языков."""
        test_data = self.create_test_language_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            languages = service.get_all_languages()
            
            assert len(languages) == 4
            assert "common" in languages
            assert "elvish" in languages
            assert "draconic" in languages
            assert "thieves_cant" in languages
            
            # Проверяем, что возвращается копия
            languages["test"] = "test"
            assert "test" not in service._languages
            
            # Очистка
            Path(f.name).unlink()

    def test_get_language_by_code(self) -> None:
        """Тест получения языка по коду."""
        test_data = self.create_test_language_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            # Существующий язык
            common = service.get_language_by_code("common")
            assert common is not None
            assert common.code == "common"
            assert common.type == "standard"
            assert common.difficulty == "easy"
            
            # Несуществующий язык
            unknown = service.get_language_by_code("unknown")
            assert unknown is None
            
            # Очистка
            Path(f.name).unlink()

    def test_get_languages_by_type(self) -> None:
        """Тест получения языков по типу."""
        test_data = self.create_test_language_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            standard_langs = service.get_languages_by_type("standard")
            exotic_langs = service.get_languages_by_type("exotic")
            secret_langs = service.get_languages_by_type("secret")
            unknown_langs = service.get_languages_by_type("unknown")
            
            assert len(standard_langs) == 2
            assert len(exotic_langs) == 1
            assert len(secret_langs) == 1
            assert len(unknown_langs) == 0
            
            assert all(lang.type == "standard" for lang in standard_langs)
            assert all(lang.type == "exotic" for lang in exotic_langs)
            assert all(lang.type == "secret" for lang in secret_langs)
            
            # Очистка
            Path(f.name).unlink()

    def test_get_languages_by_difficulty(self) -> None:
        """Тест получения языков по сложности."""
        test_data = self.create_test_language_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            easy_langs = service.get_languages_by_difficulty("easy")
            medium_langs = service.get_languages_by_difficulty("medium")
            hard_langs = service.get_languages_by_difficulty("hard")
            unknown_langs = service.get_languages_by_difficulty("unknown")
            
            assert len(easy_langs) == 1
            assert len(medium_langs) == 1
            assert len(hard_langs) == 2
            assert len(unknown_langs) == 0
            
            assert all(lang.difficulty == "easy" for lang in easy_langs)
            assert all(lang.difficulty == "medium" for lang in medium_langs)
            assert all(lang.difficulty == "hard" for lang in hard_langs)
            
            # Очистка
            Path(f.name).unlink()

    def test_get_available_languages_for_race(self) -> None:
        """Тест получения доступных языков для расы."""
        test_data = self.create_test_language_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            # Для человека (доступен common и elvish)
            human_langs = service.get_available_languages_for_race("human")
            assert len(human_langs) == 2
            human_codes = [lang.code for lang in human_langs]
            assert "common" in human_codes
            assert "elvish" in human_codes
            
            # Для эльфа (доступен common и elvish)
            elf_langs = service.get_available_languages_for_race("elf")
            assert len(elf_langs) == 2
            elf_codes = [lang.code for lang in elf_langs]
            assert "common" in elf_codes
            assert "elvish" in elf_codes
            
            # для дварфа (доступен только elvish через race_bonus)
            dwarf_langs = service.get_available_languages_for_race("dwarf")
            assert len(dwarf_langs) == 1
            assert dwarf_langs[0].code == "elvish"
            
            # Для неизвестной расы (доступен только common, т.к. learnable_by_all=True)
            unknown_langs = service.get_available_languages_for_race("unknown")
            assert len(unknown_langs) == 1
            assert unknown_langs[0].code == "common"
            
            # Очистка
            Path(f.name).unlink()

    def test_get_default_language(self) -> None:
        """Тест получения языка по умолчанию."""
        test_data = self.create_test_language_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            default_lang = service.get_default_language()
            assert default_lang is not None
            assert default_lang.code == "common"
            assert default_lang.mechanics.is_default is True
            
            # Очистка
            Path(f.name).unlink()

    def test_get_default_language_none(self) -> None:
        """Тест получения языка по умолчанию когда его нет."""
        test_data = self.create_test_language_data()
        # Убираем флаг is_default
        test_data["languages"]["common"]["mechanics"]["is_default"] = False
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            default_lang = service.get_default_language()
            assert default_lang is None
            
            # Очистка
            Path(f.name).unlink()

    def test_get_language_names_list(self) -> None:
        """Тест получения списка названий языков."""
        test_data = self.create_test_language_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            names = service.get_language_names_list()
            assert len(names) == 4
            assert "common" in names
            assert "elvish" in names
            assert "draconic" in names
            assert "thieves_cant" in names
            
            # Очистка
            Path(f.name).unlink()

    def test_format_languages_list(self) -> None:
        """Тест форматирования списка языков."""
        test_data = self.create_test_language_data()
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            # Непустой список
            languages = [
                service.get_language_by_code("common"),
                service.get_language_by_code("elvish"),
            ]
            formatted = service.format_languages_list(languages)
            assert "common (easy)" in formatted
            assert "elvish (medium)" in formatted
            assert ", " in formatted
            
            # Пустой список
            empty_formatted = service.format_languages_list([])
            assert empty_formatted == "Нет доступных языков"
            
            # Очистка
            Path(f.name).unlink()

    def test_get_language_service_singleton(self) -> None:
        """Тест синглтона get_language_service."""
        # Сброс синглтона
        import src.services.language_service
        src.services.language_service._language_service = None
        
        service1 = get_language_service()
        service2 = get_language_service()
        
        assert service1 is service2
        assert isinstance(service1, LanguageService)


class TestLanguageServiceIntegration:
    """Интеграционные тесты для LanguageService."""

    def test_full_workflow(self) -> None:
        """Тест полного рабочего процесса."""
        test_data = {
            "language_metadata": {
                "types": {"standard": "Standard", "exotic": "Exotic"},
                "difficulties": {"easy": "Easy", "hard": "Hard"}
            },
            "languages": {
                "common": {
                    "code": "common",
                    "type": "standard",
                    "difficulty": "easy",
                    "mechanics": {"is_default": True, "learnable_by_all": True}
                },
                " draconic": {
                    "code": "draconic",
                    "type": "exotic",
                    "difficulty": "hard",
                    "mechanics": {"magic_language": True, "learnable_by_special": ["wizard"]}
                }
            }
        }
        
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_data, f)
            f.flush()
            
            service = LanguageService(Path(f.name))
            
            # Получаем все языки
            all_langs = service.get_all_languages()
            assert len(all_langs) == 2
            
            # Фильтруем по типу
            standard_langs = service.get_languages_by_type("standard")
            assert len(standard_langs) == 1
            
            # Фильтруем по сложности
            hard_langs = service.get_languages_by_difficulty("hard")
            assert len(hard_langs) == 1
            
            # Проверяем доступность для класса
            draconic = service.get_language_by_code("draconic")
            assert draconic is not None
            assert draconic.is_available_for_class("wizard") is True
            assert draconic.is_available_for_class("fighter") is False
            
            # Форматируем список
            formatted = service.format_languages_list(hard_langs)
            assert "draconic (hard)" in formatted
            
            # Очистка
            Path(f.name).unlink()
