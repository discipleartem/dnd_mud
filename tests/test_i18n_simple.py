"""Простые тесты для локализации - только необходимое."""

from pathlib import Path
from use_cases.i18n_manager import I18nManagerImpl, I18nConfig


def test_i18n_basic():
    """Базовый тест локализации."""
    # Создаем менеджер
    manager = I18nManagerImpl(Path("data"))
    config = I18nConfig(default_language="ru", auto_detect_language=False)
    manager.initialize(config)
    manager.load_all_translations()
    manager._i18n.set_language("ru")
    
    # Получаем переводчик
    translator = manager.get_translator()
    
    # Тестируем UI перевод
    ui_result = translator.translate("ui.main_menu.title")
    assert ui_result == "D&D Text MUD", f"UI перевод неверный: {ui_result}"
    
    # Тестируем модульный перевод
    race_result = translator.translate("races.human.name")
    assert race_result == "Человек", f"Перевод расы неверный: {race_result}"
    
    # Тестируем отсутствующий ключ
    missing_result = translator.translate("nonexistent.key")
    assert missing_result == "nonexistent.key", f"Обработка отсутствующего ключа неверная: {missing_result}"
    
    print("✅ Все базовые тесты локализации пройдены")


if __name__ == "__main__":
    test_i18n_basic()
    print("🎉 Тестирование локализации завершено успешно!")
