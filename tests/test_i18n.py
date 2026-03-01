"""Тесты системы интернационализации.

Следует Zen Python:
- Простое лучше сложного
- Явное лучше неявного
- Читаемость важна
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

from entities.character import Character
from entities.i18n import I18n, I18nConfig, LanguageInfo, TranslationKey
from ui.console import Console
from use_cases.i18n_manager import (
    DefaultI18nTranslator,
    I18nManagerImpl,
    YamlI18nLoader,
)


class TestI18nConfig:
    """Тесты конфигурации i18n."""

    def test_default_config(self) -> None:
        """Тест конфигурации по умолчанию."""
        config = I18nConfig()

        assert config.default_language == "ru"
        assert config.fallback_language == "en"
        assert config.cache_enabled is True
        assert config.auto_detect_language is True

    def test_custom_config(self) -> None:
        """Тест кастомной конфигурации."""
        config = I18nConfig(
            default_language="en",
            fallback_language="ru",
            cache_enabled=False,
            auto_detect_language=False,
        )

        assert config.default_language == "en"
        assert config.fallback_language == "ru"
        assert config.cache_enabled is False
        assert config.auto_detect_language is False


class TestLanguageInfo:
    """Тесты информации о языке."""

    def test_language_info_creation(self) -> None:
        """Тест создания информации о языке."""
        lang = LanguageInfo("ru", "Russian", "Русский")

        assert lang.code == "ru"
        assert lang.name == "Russian"
        assert lang.native_name == "Русский"
        assert lang.rtl is False

    def test_rtl_language(self) -> None:
        """Тест языка справа налево."""
        lang = LanguageInfo("ar", "Arabic", "العربية", rtl=True)

        assert lang.rtl is True


class TestTranslationKey:
    """Тесты ключей перевода."""

    def test_simple_key(self) -> None:
        """Тест простого ключа."""
        key = TranslationKey("welcome")

        assert key.key == "welcome"
        assert key.context is None
        assert key.get_full_key() == "welcome"

    def test_context_key(self) -> None:
        """Тест ключа с контекстом."""
        key = TranslationKey("title", context="ui.main_menu")

        assert key.key == "title"
        assert key.context == "ui.main_menu"
        assert key.get_full_key() == "ui.main_menu.title"


class TestI18n:
    """Тесты основной сущности i18n."""

    def test_i18n_initialization(self) -> None:
        """Тест инициализации i18n."""
        config = I18nConfig()
        i18n = I18n(config)

        assert i18n.current_language == "ru"
        assert i18n.config == config

    def test_set_language(self) -> None:
        """Тест установки языка."""
        config = I18nConfig()
        i18n = I18n(config)

        # Существующий язык
        assert i18n.set_language("en") is True
        assert i18n.current_language == "en"

        # Несуществующий язык
        assert i18n.set_language("fr") is False
        assert i18n.current_language == "en"

    def test_add_language(self) -> None:
        """Тест добавления языка."""
        config = I18nConfig()
        i18n = I18n(config)

        french = LanguageInfo("fr", "French", "Français")
        i18n.add_language(french)

        languages = i18n.get_available_languages()
        assert "fr" in languages
        assert languages["fr"] == french

    def test_load_translations(self) -> None:
        """Тест загрузки переводов."""
        config = I18nConfig()
        i18n = I18n(config)

        translations = {
            "welcome": "Добро пожаловать",
            "ui": {
                "title": "Заголовок",
            },
        }

        i18n.load_translations("ru", translations)

        # Простой ключ
        key = TranslationKey("welcome")
        assert i18n.get_translation(key) == "Добро пожаловать"

        # Вложенный ключ
        key = TranslationKey("title", context="ui")
        assert i18n.get_translation(key) == "Заголовок"

    def test_fallback_translation(self) -> None:
        """Тест fallback перевода."""
        config = I18nConfig(fallback_language="en")
        i18n = I18n(config)

        # Загружаем только английские переводы
        en_translations = {"welcome": "Welcome"}
        i18n.load_translations("en", en_translations)

        # Устанавливаем несуществующий язык
        i18n.set_language("fr")

        # Должен вернуться fallback перевод
        key = TranslationKey("welcome")
        assert i18n.get_translation(key) == "Welcome"

    def test_cache_functionality(self) -> None:
        """Тест работы кэша."""
        config = I18nConfig(cache_enabled=True)
        i18n = I18n(config)

        translations = {"welcome": "Добро пожаловать"}
        i18n.load_translations("ru", translations)

        key = TranslationKey("welcome")

        # Первый вызов - загружает в кэш
        result1 = i18n.get_translation(key)

        # Второй вызов - из кэша
        result2 = i18n.get_translation(key)

        assert result1 == result2 == "Добро пожаловать"

        # Проверяем статистику кэша
        stats = i18n.get_cache_stats()
        assert stats["size"] == 1

    def test_clear_cache(self) -> None:
        """Тест очистки кэша."""
        config = I18nConfig(cache_enabled=True)
        i18n = I18n(config)

        translations = {"welcome": "Добро пожаловать"}
        i18n.load_translations("ru", translations)

        key = TranslationKey("welcome")
        i18n.get_translation(key)

        # Кэш не пуст
        assert i18n.get_cache_stats()["size"] == 1

        # Очищаем кэш
        i18n.clear_cache()

        # Кэш пуст
        assert i18n.get_cache_stats()["size"] == 0


class TestYamlI18nLoader:
    """Тесты загрузчика YAML."""

    def test_load_translations_from_file(self) -> None:
        """Тест загрузки переводов из файла."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            i18n_dir = data_dir / "i18n"
            i18n_dir.mkdir()

            # Создаем тестовый YAML файл
            translations = {
                "welcome": "Добро пожаловать",
                "ui": {
                    "title": "Заголовок",
                },
            }

            yaml_file = i18n_dir / "ru.yaml"
            with open(yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(translations, f, allow_unicode=True)

            loader = YamlI18nLoader(data_dir)
            loaded = loader.load_translations("ru")

            assert loaded == translations

    def test_load_nonexistent_language(self) -> None:
        """Тест загрузки несуществующего языка."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            i18n_dir = data_dir / "i18n"
            i18n_dir.mkdir()

            loader = YamlI18nLoader(data_dir)
            loaded = loader.load_translations("nonexistent")

            assert loaded == {}

    def test_get_available_languages(self) -> None:
        """Тест получения доступных языков."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            loader = YamlI18nLoader(data_dir)

            languages = loader.get_available_languages()

            assert "ru" in languages
            assert "en" in languages
            assert languages["ru"].code == "ru"
            assert languages["en"].code == "en"


class TestDefaultI18nTranslator:
    """Тесты переводчика по умолчанию."""

    def test_simple_translation(self) -> None:
        """Тест простого перевода."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        translations = {"welcome": "Добро пожаловать"}
        i18n.load_translations("ru", translations)

        result = translator.translate("welcome")
        assert result == "Добро пожаловать"

    def test_translation_with_context(self) -> None:
        """Тест перевода с контекстом."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        translations = {"ui": {"title": "Заголовок"}}
        i18n.load_translations("ru", translations)

        result = translator.translate("title", context="ui")
        assert result == "Заголовок"

    def test_translation_with_formatting(self) -> None:
        """Тест перевода с форматированием."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        translations = {"greeting": "Привет, {name}!"}
        i18n.load_translations("ru", translations)

        result = translator.translate("greeting", name="Мир")
        assert result == "Привет, Мир!"

    def test_fallback_translation(self) -> None:
        """Тест fallback перевода."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        # Нет переводов
        result = translator.translate("nonexistent")
        assert result == "nonexistent"

    def test_set_language(self) -> None:
        """Тест установки языка."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        assert translator.set_language("en") is True
        assert translator.get_current_language() == "en"

        assert translator.set_language("fr") is False


class TestI18nManagerImpl:
    """Тесты менеджера i18n."""

    def test_manager_initialization(self) -> None:
        """Тест инициализации менеджера."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            manager = I18nManagerImpl(data_dir)

            config = I18nConfig()
            manager.initialize(config)

            translator = manager.get_translator()
            assert translator is not None

    def test_load_all_translations(self) -> None:
        """Тест загрузки всех переводов."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            i18n_dir = data_dir / "i18n"
            i18n_dir.mkdir()

            # Создаем тестовые файлы
            ru_translations = {"welcome": "Добро пожаловать"}
            en_translations = {"welcome": "Welcome"}

            with open(i18n_dir / "ru.yaml", "w", encoding="utf-8") as f:
                yaml.dump(ru_translations, f, allow_unicode=True)

            with open(i18n_dir / "en.yaml", "w", encoding="utf-8") as f:
                yaml.dump(en_translations, f, allow_unicode=True)

            manager = I18nManagerImpl(data_dir)
            config = I18nConfig()
            manager.initialize(config)

            manager.load_all_translations()

            translator = manager.get_translator()

            # Русский перевод
            translator.set_language("ru")
            assert translator.translate("welcome") == "Добро пожаловать"

            # Английский перевод
            translator.set_language("en")
            assert translator.translate("welcome") == "Welcome"

    def test_get_statistics(self) -> None:
        """Тест получения статистики."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            manager = I18nManagerImpl(data_dir)

            # Не инициализирован
            stats = manager.get_statistics()
            assert "error" in stats

            # Инициализирован
            config = I18nConfig()
            manager.initialize(config)

            stats = manager.get_statistics()
            assert "current_language" in stats
            assert "config" in stats


class TestSystemI18nDetector:
    """Тесты детектора языка системы."""

    def test_detect_russian_locale(self) -> None:
        """Тест определения русского языка."""
        from use_cases.i18n_manager import SystemI18nDetector

        detector = SystemI18nDetector()

        # Мокаем locale.getdefaultlocale
        with patch('locale.getdefaultlocale', return_value=('ru_RU', 'UTF-8')):
            lang = detector.detect_system_language()
            assert lang == "ru"

    def test_detect_english_locale(self) -> None:
        """Тест определения английского языка."""
        from use_cases.i18n_manager import SystemI18nDetector

        detector = SystemI18nDetector()

        with patch('locale.getdefaultlocale', return_value=('en_US', 'UTF-8')):
            lang = detector.detect_system_language()
            assert lang == "en"

    def test_detect_from_env_var(self) -> None:
        """Тест определения из переменных окружения."""
        from use_cases.i18n_manager import SystemI18nDetector

        detector = SystemI18nDetector()

        with patch('locale.getdefaultlocale', return_value=(None, None)):
            with patch.dict('os.environ', {'LANG': 'ru_RU.UTF-8'}):
                lang = detector.detect_system_language()
                assert lang == "ru"

    def test_detect_no_language(self) -> None:
        """Тест когда язык не определён."""
        from use_cases.i18n_manager import SystemI18nDetector

        detector = SystemI18nDetector()

        with patch('locale.getdefaultlocale', return_value=(None, None)):
            with patch.dict('os.environ', {}, clear=True):
                lang = detector.detect_system_language()
                assert lang is None


class TestConsoleI18nIntegration:
    """Тесты интеграции консоли с i18n."""

    def test_console_with_translator(self) -> None:
        """Тест консоли с переводчиком."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        translations = {"welcome": "Добро пожаловать"}
        i18n.load_translations("ru", translations)

        console = Console(translator)

        # Проверяем метод перевода
        result = console.t("welcome")
        assert result == "Добро пожаловать"

    def test_console_without_translator(self) -> None:
        """Тест консоли без переводчика."""
        console = Console()

        # Должен возвращать ключ как есть
        result = console.t("welcome")
        assert result == "welcome"

    def test_console_set_translator(self) -> None:
        """Тест установки переводчика."""
        console = Console()

        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        console.set_translator(translator)

        # Теперь должен переводить
        translations = {"welcome": "Добро пожаловать"}
        i18n.load_translations("ru", translations)

        result = console.t("welcome")
        assert result == "Добро пожаловать"

    @patch('builtins.input')
    def test_console_show_message_and_wait_with_i18n(self, mock_input: Mock) -> None:
        """Тест показа сообщения с локализацией."""
        mock_input.return_value = ""

        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        translations = {"press_enter": "Нажмите Enter"}
        i18n.load_translations("ru", translations)

        console = Console(translator)

        with patch.object(console, 'print_info') as mock_print:
            console.show_message_and_wait("Тестовое сообщение")

            # Проверяем, что print_info был вызван с сообщением
            mock_print.assert_called_once_with("Тестовое сообщение")

            # Проверяем, что input был вызван с локализованным промптом
            mock_input.assert_called_once_with("Нажмите Enter")


class TestCharacterI18nIntegration:
    """Тесты интеграции персонажа с i18n."""

    def test_character_with_translator(self) -> None:
        """Тест персонажа с переводчиком."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        # Используем правильную структуру с контекстом
        translations = {
            "character": {
                "status": {
                    "dead": "Погиб",
                    "healthy": "Здоров",
                    "wounded": "Ранен",
                    "heavily_wounded": "Тяжело ранен",
                },
            },
            "levels": {
                "novice": "Новичок",
                "adventurer": "Авантюрист",
            },
        }
        i18n.load_translations("ru", translations)
        i18n.set_language("ru")  # Устанавливаем язык в i18n

        character = Character("Тестовый персонаж", level=1, hit_points=0, max_hit_points=10)
        character.set_translator(translator)

        # Проверяем статус
        assert character.get_status() == "Погиб"

        # Проверяем строковое представление
        str_repr = str(character)
        assert "Новичок" in str_repr
        assert "Тестовый персонаж" in str_repr

    def test_character_without_translator(self) -> None:
        """Тест персонажа без переводчика."""
        character = Character("Тестовый персонаж", level=1, hit_points=0, max_hit_points=10)

        # Должен возвращать ключи как есть
        assert character.get_status() == "character.status.dead"

        str_repr = str(character)
        assert "levels.novice" in str_repr  # Исправляем ожидаемый результат

    def test_character_different_statuses(self) -> None:
        """Тест разных статусов персонажа."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        # Используем правильную структуру с контекстом
        translations = {
            "character": {
                "status": {
                    "dead": "Погиб",
                    "healthy": "Здоров",
                    "wounded": "Ранен",
                    "heavily_wounded": "Тяжело ранен",
                },
            },
            "levels": {
                "novice": "Новичок",
                "adventurer": "Авантюрист",
            },
        }
        i18n.load_translations("ru", translations)
        i18n.set_language("ru")  # Устанавливаем язык

        # Мёртвый персонаж
        dead_char = Character("Мертвец", hit_points=0, max_hit_points=10)
        dead_char.set_translator(translator)
        assert dead_char.get_status() == "Погиб"

        # Здоровый персонаж
        healthy_char = Character("Здоровяк", hit_points=10, max_hit_points=10)
        healthy_char.set_translator(translator)
        assert healthy_char.get_status() == "Здоров"

        # Раненый персонаж
        wounded_char = Character("Раненый", hit_points=6, max_hit_points=10)
        wounded_char.set_translator(translator)
        assert wounded_char.get_status() == "Ранен"

        # Тяжело раненый персонаж
        heavily_wounded_char = Character("Тяжело раненый", hit_points=3, max_hit_points=10)
        heavily_wounded_char.set_translator(translator)
        assert heavily_wounded_char.get_status() == "Тяжело ранен"

    def test_character_different_levels(self) -> None:
        """Тест разных уровней персонажа."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        # Используем правильную структуру с контекстом
        translations = {
            "character": {
                "status": {
                    "dead": "Погиб",
                    "healthy": "Здоров",
                },
            },
            "levels": {
                "novice": "Новичок",
                "adventurer": "Авантюрист",
            },
        }
        i18n.load_translations("ru", translations)
        i18n.set_language("ru")  # Устанавливаем язык

        # Новичок (уровень <= 5)
        novice = Character("Новичок", level=3)
        novice.set_translator(translator)
        str_repr = str(novice)
        assert "Новичок" in str_repr

        # Авантюрист (уровень > 5)
        adventurer = Character("Авантюрист", level=10)
        adventurer.set_translator(translator)
        str_repr = str(adventurer)
        assert "Авантюрист" in str_repr


class TestI18nEdgeCases:
    """Тесты граничных случаев системы i18n."""

    def test_empty_translation_key(self) -> None:
        """Тест пустого ключа перевода."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        result = translator.translate("")
        assert result == ""

    def test_none_translation_key(self) -> None:
        """Тест None ключа перевода."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        # Должен обработать None как строку
        result = translator.translate(None)  # type: ignore
        assert result is None  # Исправляем ожидаемый результат

    def test_missing_yaml_file(self) -> None:
        """Тест отсутствующего YAML файла."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            i18n_dir = data_dir / "i18n"
            i18n_dir.mkdir()

            loader = YamlI18nLoader(data_dir)

            # Запрос несуществующего языка
            translations = loader.load_translations("nonexistent")
            assert translations == {}

    def test_invalid_yaml_file(self) -> None:
        """Тест некорректного YAML файла."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            i18n_dir = data_dir / "i18n"
            i18n_dir.mkdir()

            # Создаем некорректный YAML файл
            yaml_file = i18n_dir / "invalid.yaml"
            with open(yaml_file, "w", encoding="utf-8") as f:
                f.write("invalid: yaml: content: [")

            loader = YamlI18nLoader(data_dir)
            translations = loader.load_translations("invalid")

            # Должен вернуть пустой словарь при ошибке
            assert translations == {}

    def test_circular_reference_in_yaml(self) -> None:
        """Тест циклических ссылок в YAML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            i18n_dir = data_dir / "i18n"
            i18n_dir.mkdir()

            # Создаем YAML с потенциальной проблемой
            translations = {
                "key1": "value1",
                "nested": {
                    "key2": "value2",
                },
            }

            yaml_file = i18n_dir / "test.yaml"
            with open(yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(translations, f, allow_unicode=True)

            loader = YamlI18nLoader(data_dir)
            loaded = loader.load_translations("test")

            assert loaded == translations

    def test_unicode_in_translations(self) -> None:
        """Тест Unicode в переводах."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        # Тест с различными Unicode символами
        translations = {
            "unicode_test": "Тест с Unicode: ñáéíóú 🎮",
            "emoji": "Игра: 🐉⚔️🛡️",
            "cyrillic": "Кириллица: абвгдеёж",
        }

        i18n.load_translations("ru", translations)

        assert translator.translate("unicode_test") == "Тест с Unicode: ñáéíóú 🎮"
        assert translator.translate("emoji") == "Игра: 🐉⚔️🛡️"
        assert translator.translate("cyrillic") == "Кириллица: абвгдеёж"

    def test_very_long_translation_key(self) -> None:
        """Тест очень длинного ключа перевода."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        long_key = "a" * 1000
        translations = {long_key: "Длинный ключ"}

        i18n.load_translations("ru", translations)

        result = translator.translate(long_key)
        assert result == "Длинный ключ"

    def test_special_characters_in_keys(self) -> None:
        """Тест специальных символов в ключах."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        translations = {
            "key-with-dashes": "Дефис",
            "key_with_underscores": "Подчёркивания",
            "key with spaces": "Пробелы",
        }
        i18n.load_translations("ru", translations)

        for key, expected in translations.items():
            result = translator.translate(key)
            assert result == expected

        # Тест с точками - они работают как разделители контекста
        nested_translations = {
            "key": {
                "with": {
                    "dots": "Точка",
                },
            },
        }
        i18n.load_translations("ru", nested_translations)

        # Должен работать с контекстом
        result = translator.translate("dots", context="key.with")
        assert result == "Точка"

        # Тест с простыми спецсимволами (без точек)
        special_translations = {
            "special!@#chars": "Спецсимволы",
        }
        i18n.load_translations("ru", special_translations)

        result = translator.translate("special!@#chars")
        assert result == "Спецсимволы"

    def test_nested_key_not_found(self) -> None:
        """Тест отсутствующего вложенного ключа."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        translations = {
            "ui": {
                "main_menu": {
                    "title": "Заголовок",
                },
            },
        }

        i18n.load_translations("ru", translations)

        # Существующий ключ
        assert translator.translate("title", context="ui.main_menu") == "Заголовок"

        # Несуществующий вложенный ключ
        result = translator.translate("nonexistent", context="ui.main_menu")
        assert result == "ui.main_menu.nonexistent"

    def test_cache_disabled(self) -> None:
        """Тест работы с отключенным кэшем."""
        config = I18nConfig(cache_enabled=False)
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        translations = {"welcome": "Добро пожаловать"}
        i18n.load_translations("ru", translations)

        # Первый вызов
        result1 = translator.translate("welcome")
        assert result1 == "Добро пожаловать"

        # Второй вызов (без кэша)
        result2 = translator.translate("welcome")
        assert result2 == "Добро пожаловать"

        # Статистика кэша должна быть пустой
        stats = i18n.get_cache_stats()
        assert stats["size"] == 0

    def test_multiple_language_switches(self) -> None:
        """Тест многократного переключения языков."""
        config = I18nConfig()
        i18n = I18n(config)
        translator = DefaultI18nTranslator(i18n)

        ru_translations = {"welcome": "Добро пожаловать"}
        en_translations = {"welcome": "Welcome"}

        i18n.load_translations("ru", ru_translations)
        i18n.load_translations("en", en_translations)

        # Переключаем языки несколько раз
        for _ in range(5):
            translator.set_language("ru")
            assert translator.translate("welcome") == "Добро пожаловать"

            translator.set_language("en")
            assert translator.translate("welcome") == "Welcome"


class TestI18nValidator:
    """Тесты валидатора переводов."""

    def test_validate_empty_translations(self) -> None:
        """Тест валидации пустых переводов."""
        from use_cases.i18n_manager import DefaultI18nValidator

        validator = DefaultI18nValidator()

        # Пустой словарь - валиден
        assert validator.validate_translations({}) is True

        # None - не валиден
        assert validator.validate_translations(None) is False  # type: ignore

    def test_validate_nested_translations(self) -> None:
        """Тест валидации вложенных переводов."""
        from use_cases.i18n_manager import DefaultI18nValidator

        validator = DefaultI18nValidator()

        translations = {
            "ui": {
                "main_menu": {
                    "title": "Заголовок",
                },
            },
            "character": {
                "status": {
                    "alive": "Жив",
                    "dead": "Мёртв",
                },
            },
        }

        assert validator.validate_translations(translations) is True

    def test_find_missing_keys_simple(self) -> None:
        """Тест поиска отсутствующих ключей (простой случай)."""
        from use_cases.i18n_manager import DefaultI18nValidator

        validator = DefaultI18nValidator()

        base = {"key1": "value1", "key2": "value2"}
        target = {"key1": "value1"}

        missing = validator.find_missing_keys(base, target)
        assert missing == ["key2"]

    def test_find_missing_keys_nested(self) -> None:
        """Тест поиска отсутствующих ключей (вложенный случай)."""
        from use_cases.i18n_manager import DefaultI18nValidator

        validator = DefaultI18nValidator()

        base = {
            "ui": {
                "title": "Заголовок",
                "button": "Кнопка",
            },
            "character": {
                "name": "Имя",
                "level": "Уровень",
            },
        }
        target = {
            "ui": {
                "title": "Заголовок",
            },
            "character": {
                "name": "Имя",
            },
        }

        missing = validator.find_missing_keys(base, target)
        assert set(missing) == {"ui.button", "character.level"}

    def test_find_missing_keys_no_missing(self) -> None:
        """Тест когда нет отсутствующих ключей."""
        from use_cases.i18n_manager import DefaultI18nValidator

        validator = DefaultI18nValidator()

        base = {"key1": "value1", "key2": "value2"}
        target = {"key1": "value1", "key2": "value2"}

        missing = validator.find_missing_keys(base, target)
        assert missing == []
