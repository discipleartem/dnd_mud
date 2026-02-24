#!/usr/bin/env python3
"""Тесты для UI сервисов."""

from unittest.mock import Mock, patch

import pytest

from src.services.language_service import Language, LanguageMechanics
from src.ui.entities.race import Feature
from src.ui.services.language_display_service import (
    LanguageDisplayService,
    _safe_str,
)
from src.ui.services.race_display_service import (
    RaceDisplayService,
    _get_feature_emoji,
)


class TestSafeStr:
    """Тесты для функции _safe_str."""

    def test_safe_str_with_string(self) -> None:
        """Тест _safe_str со строкой."""
        result = _safe_str("test string")
        assert result == "test string"

    def test_safe_str_with_non_string(self) -> None:
        """Тест _safe_str с не-строкой."""
        result = _safe_str(123)
        assert result == "123"
        
        result = _safe_str(45.67)
        assert result == "45.67"
        
        result = _safe_str(True)
        assert result == "True"
        
        result = _safe_str(None)
        assert result == "None"
        
        result = _safe_str(["list", "item"])
        assert result == "['list', 'item']"

    def test_safe_str_with_unicode(self) -> None:
        """Тест _safe_str с юникод символами."""
        result = _safe_str("Тест на русском")
        assert result == "Тест на русском"
        
        result = _safe_str("Test with émojis 🎲")
        assert result == "Test with émojis 🎲"


class TestLanguageDisplayService:
    """Тесты для LanguageDisplayService."""

    def create_test_language(self, **overrides) -> Language:
        """Создать тестовый язык с переопределениями."""
        defaults = {
            "code": "test_lang",
            "type": "standard",
            "difficulty": "medium",
            "localization_keys": {},
            "mechanics": LanguageMechanics(),
            "fallback_data": {}
        }
        defaults.update(overrides)
        return Language(**defaults)

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_name_with_localization(self, mock_t) -> None:
        """Тест получения названия с локализацией."""
        mock_t.return_value = "Тестовый язык"
        
        language = self.create_test_language(
            localization_keys={"name": "language.test.name"}
        )
        
        result = LanguageDisplayService.get_language_name(language)
        
        assert result == "Тестовый язык"
        mock_t.assert_called_once_with("language.test.name")

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_name_with_fallback(self, mock_t) -> None:
        """Тест получения названия с fallback."""
        language = self.create_test_language(
            localization_keys={},
            fallback_data={"name": "Fallback Name"}
        )
        
        result = LanguageDisplayService.get_language_name(language)
        
        assert result == "Fallback Name"
        mock_t.assert_not_called()

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_name_with_code(self, mock_t) -> None:
        """Тест получения названия с кодом языка."""
        language = self.create_test_language(
            localization_keys={},
            fallback_data={}
        )
        
        result = LanguageDisplayService.get_language_name(language)
        
        assert result == "test_lang"
        mock_t.assert_not_called()

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_name_with_non_string_result(self, mock_t) -> None:
        """Тест получения названия с не-строковым результатом."""
        mock_t.return_value = 123  # Не-строковый результат
        
        language = self.create_test_language(
            localization_keys={"name": "language.test.name"}
        )
        
        result = LanguageDisplayService.get_language_name(language)
        
        assert result == "123"
        mock_t.assert_called_once_with("language.test.name")

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_description_with_localization(self, mock_t) -> None:
        """Тест получения описания с локализацией."""
        mock_t.return_value = "Описание тестового языка"
        
        language = self.create_test_language(
            localization_keys={"description": "language.test.description"}
        )
        
        result = LanguageDisplayService.get_language_description(language)
        
        assert result == "Описание тестового языка"
        mock_t.assert_called_once_with("language.test.description")

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_description_with_fallback(self, mock_t) -> None:
        """Тест получения описания с fallback."""
        language = self.create_test_language(
            localization_keys={},
            fallback_data={"description": "Fallback Description"}
        )
        
        result = LanguageDisplayService.get_language_description(language)
        
        assert result == "Fallback Description"
        mock_t.assert_not_called()

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_description_empty(self, mock_t) -> None:
        """Тест получения пустого описания."""
        language = self.create_test_language(
            localization_keys={},
            fallback_data={}
        )
        
        result = LanguageDisplayService.get_language_description(language)
        
        assert result == ""
        mock_t.assert_not_called()

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_speakers_with_localization(self, mock_t) -> None:
        """Тест получения носителей с локализацией."""
        mock_t.return_value = "Эльфы, люди"
        
        language = self.create_test_language(
            localization_keys={"speakers": "language.test.speakers"}
        )
        
        result = LanguageDisplayService.get_language_speakers(language)
        
        assert result == "Эльфы, люди"
        mock_t.assert_called_once_with("language.test.speakers")

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_speakers_with_fallback(self, mock_t) -> None:
        """Тест получения носителей с fallback."""
        language = self.create_test_language(
            localization_keys={},
            fallback_data={"speakers": "Fallback Speakers"}
        )
        
        result = LanguageDisplayService.get_language_speakers(language)
        
        assert result == "Fallback Speakers"
        mock_t.assert_not_called()

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_speakers_empty(self, mock_t) -> None:
        """Тест получения пустых носителей."""
        language = self.create_test_language(
            localization_keys={},
            fallback_data={}
        )
        
        result = LanguageDisplayService.get_language_speakers(language)
        
        assert result == ""
        mock_t.assert_not_called()

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_type_name(self, mock_t) -> None:
        """Тест получения названия типа языка."""
        mock_t.return_value = "Стандартный"
        
        language = self.create_test_language(type="standard")
        
        result = LanguageDisplayService.get_language_type_name(language)
        
        assert result == "Стандартный"
        mock_t.assert_called_once_with("language.types.standard")

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_type_name_non_string(self, mock_t) -> None:
        """Тест получения названия типа с не-строковым результатом."""
        mock_t.return_value = {"type": "standard"}  # Не-строковый результат
        
        language = self.create_test_language(type="standard")
        
        result = LanguageDisplayService.get_language_type_name(language)
        
        assert result == "{'type': 'standard'}"
        mock_t.assert_called_once_with("language.types.standard")

    @patch('src.ui.services.language_display_service.t')
    def test_get_language_difficulty_name(self, mock_t) -> None:
        """Тест получения названия сложности языка."""
        mock_t.return_value = "Средняя"
        
        language = self.create_test_language(difficulty="medium")
        
        result = LanguageDisplayService.get_language_difficulty_name(language)
        
        assert result == "Средняя"
        mock_t.assert_called_once_with("language.difficulties.medium")

    def test_language_display_service_integration(self) -> None:
        """Тест интеграции всех методов LanguageDisplayService."""
        language = self.create_test_language(
            code="common",
            type="standard",
            difficulty="easy",
            localization_keys={
                "name": "language.common.name",
                "description": "language.common.description",
                "speakers": "language.common.speakers"
            },
            fallback_data={
                "name": "Common",
                "description": "Universal language",
                "speakers": "All races"
            }
        )
        
        with patch('src.ui.services.language_display_service.t') as mock_t:
            mock_t.side_effect = lambda key: {
                "language.common.name": "Общий",
                "language.common.description": "Универсальный язык",
                "language.common.speakers": "Все расы",
                "language.types.standard": "Стандартный",
                "language.difficulties.easy": "Легкая"
            }.get(key, key)
            
            name = LanguageDisplayService.get_language_name(language)
            description = LanguageDisplayService.get_language_description(language)
            speakers = LanguageDisplayService.get_language_speakers(language)
            type_name = LanguageDisplayService.get_language_type_name(language)
            difficulty_name = LanguageDisplayService.get_language_difficulty_name(language)
            
            assert name == "Общий"
            assert description == "Универсальный язык"
            assert speakers == "Все расы"
            assert type_name == "Стандартный"
            assert difficulty_name == "Легкая"


class TestGetFeatureEmoji:
    """Тесты для функции _get_feature_emoji."""

    def test_get_feature_emoji_known_features(self) -> None:
        """Тест получения эмодзи для известных черт."""
        test_cases = [
            ("темное зрение", "🌙"),
            ("Темное зрение", "🌙"),  # Разный регистр
            ("ТЕМНОЕ ЗРЕНИЕ", "🌙"),  # Все заглавные
            ("светочувствительность", "☀️"),
            ("устойчивость к магии", "🛡️"),
            ("мастерство", "⚔️"),
            ("ловкость", "🏃"),
            ("маскировка", "🥷"),
        ]
        
        for feature_name, expected_emoji in test_cases:
            result = _get_feature_emoji(feature_name)
            assert result == expected_emoji, f"Failed for '{feature_name}'"

    def test_get_feature_emoji_unknown_feature(self) -> None:
        """Тест получения эмодзи для неизвестной черты."""
        unknown_features = [
            "неизвестная черта",
            "random feature",
            "special ability",
            "",
            "123",
            "!@#$%",
        ]
        
        for feature_name in unknown_features:
            result = _get_feature_emoji(feature_name)
            assert result == "⚡", f"Failed for '{feature_name}'"

    def test_get_feature_emoji_case_insensitive(self) -> None:
        """Тест регистронезависимости."""
        base_feature = "темное зрение"
        variants = [
            "темное зрение",
            "Темное зрение",
            "ТЕМНОЕ ЗРЕНИЕ",
            "теМнОе ЗрЕниЕ",
        ]
        
        for variant in variants:
            result = _get_feature_emoji(variant)
            assert result == "🌙", f"Failed for variant '{variant}'"

    def test_get_feature_emoji_partial_match(self) -> None:
        """Тест частичного совпадения (должен возвращать эмодзи по умолчанию)."""
        partial_matches = [
            "темное",  # Частичное совпадение
            "зрение",  # Частичное совпадение
            "темное зрение дополнительно",  # Содержит известную черту
        ]
        
        for feature_name in partial_matches:
            result = _get_feature_emoji(feature_name)
            assert result == "⚡", f"Should return default emoji for '{feature_name}'"


class TestRaceDisplayService:
    """Тесты для RaceDisplayService."""

    def create_test_feature(self, name: str, description: str, mechanics: dict | None = None) -> Feature:
        """Создать тестовую черту."""
        if mechanics is None:
            mechanics = {"type": "test"}
        return Feature(name=name, description=description, mechanics=mechanics)

    @patch('src.ui.services.race_display_service.t')
    @patch('builtins.print')
    def test_display_features_with_emoji(self, mock_print, mock_t) -> None:
        """Тест отображения черт с эмодзи."""
        mock_t.return_value = "Черты:"
        
        features = [
            self.create_test_feature("Темное зрение", "Вы можете видеть в темноте"),
            self.create_test_feature("Мастерство", "Вы получаете дополнительное мастерство"),
            self.create_test_feature("Неизвестная черта", "Описание неизвестной черты"),
        ]
        
        RaceDisplayService.display_features_with_emoji(features)
        
        # Проверяем вызовы print
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Проверяем заголовок
        assert any("Черты:" in call for call in print_calls)
        
        # Проверяем черты с эмодзи
        assert any("🌙 Темное зрение" in call for call in print_calls)
        assert any("⚔️ Мастерство" in call for call in print_calls)
        assert any("⚡ Неизвестная черта" in call for call in print_calls)
        
        # Проверяем описания
        assert any("Вы можете видеть в темноте" in call for call in print_calls)
        assert any("Вы получаете дополнительное мастерство" in call for call in print_calls)
        assert any("Описание неизвестной черты" in call for call in print_calls)

    @patch('src.ui.services.race_display_service.t')
    @patch('builtins.print')
    def test_display_features_with_emoji_custom_indent(self, mock_print, mock_t) -> None:
        """Тест отображения черт с кастомным отступом."""
        mock_t.return_value = "Черты:"
        
        features = [
            self.create_test_feature("Темное зрение", "Описание")
        ]
        
        RaceDisplayService.display_features_with_emoji(features, indent="  ")
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Проверяем, что используется кастомный отступ
        assert any("  Черты:" in call for call in print_calls)
        assert any("     🌙 Темное зрение" in call for call in print_calls)
        assert any("       Описание" in call for call in print_calls)

    @patch('src.ui.services.race_display_service.t')
    @patch('builtins.print')
    def test_display_features_empty_list(self, mock_print, mock_t) -> None:
        """Тест отображения пустого списка черт."""
        mock_t.return_value = "Черты:"
        
        RaceDisplayService.display_features_with_emoji([])
        
        # Должен быть вызван только заголовок
        assert mock_print.call_count == 1
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Черты:" in call for call in print_calls)

    @patch('src.ui.services.race_display_service.t')
    @patch('builtins.print')
    def test_display_abilities_description(self, mock_print, mock_t) -> None:
        """Тест отображения описания способностей."""
        mock_t.return_value = "Бонусы к характеристикам:"
        
        description = "+2 к Ловкости, +1 к Интеллекту"
        
        RaceDisplayService.display_abilities_description(description)
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Проверяем, что описание выведено
        assert any("Бонусы к характеристикам: +2 к Ловкости, +1 к Интеллекту" in call for call in print_calls)

    @patch('src.ui.services.race_display_service.t')
    @patch('builtins.print')
    def test_display_abilities_description_custom_indent(self, mock_print, mock_t) -> None:
        """Тест отображения описания способностей с кастомным отступом."""
        mock_t.return_value = "Бонусы:"
        
        description = "+1 ко всем характеристикам"
        
        RaceDisplayService.display_abilities_description(description, indent="  ")
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Проверяем, что используется кастомный отступ
        assert any("  Бонусы: +1 ко всем характеристикам" in call for call in print_calls)

    @patch('src.ui.services.race_display_service.t')
    @patch('builtins.print')
    def test_display_abilities_description_empty(self, mock_print, mock_t) -> None:
        """Тест отображения пустого описания способностей."""
        # Пустое описание не должно выводиться
        RaceDisplayService.display_abilities_description("")
        
        mock_print.assert_not_called()
        mock_t.assert_not_called()
        
        # None тоже не должен выводиться
        RaceDisplayService.display_abilities_description("")
        
        # Количество вызовов не должно измениться
        assert mock_print.call_count == 0

    @patch('src.ui.services.race_display_service.t')
    @patch('builtins.print')
    def test_display_abilities_description_whitespace_only(self, mock_print, mock_t) -> None:
        """Тест отображения описания с только пробельными символами."""
        # Строка с пробелами должна считаться непустой
        description = "   "
        
        mock_t.return_value = "Бонусы:"
        
        RaceDisplayService.display_abilities_description(description)
        
        mock_print.assert_called_once()
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Бонусы:   " in call for call in print_calls)

    @patch('src.ui.services.race_display_service.t')
    @patch('builtins.print')
    def test_race_display_service_integration(self, mock_print, mock_t) -> None:
        """Тест интеграции всех методов RaceDisplayService."""
        mock_t.side_effect = lambda key: {
            "new_game.details_section.features_label": "Черты:",
            "new_game.details_section.abilities_label": "Бонусы:",
        }.get(key, key)
        
        features = [
            self.create_test_feature("Темное зрение", "Видеть в темноте"),
            self.create_test_feature("Ловкость", "Бонус к ловкости"),
        ]
        abilities = "+2 к Ловкости"
        
        # Отображаем черты
        RaceDisplayService.display_features_with_emoji(features, indent="  ")
        
        # Отображаем способности
        RaceDisplayService.display_abilities_description(abilities, indent="  ")
        
        print_calls = [str(call) for call in mock_print.call_args_list]
        
        # Проверяем, что все было выведено
        assert any("  Черты:" in call for call in print_calls)
        assert any("🌙 Темное зрение" in call for call in print_calls)
        assert any("🏃 Ловкость" in call for call in print_calls)
        assert any("Видеть в темноте" in call for call in print_calls)
        assert any("Бонус к ловкости" in call for call in print_calls)
        assert any("  Бонусы: +2 к Ловкости" in call for call in print_calls)
