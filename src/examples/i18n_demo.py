#!/usr/bin/env python3
"""Демо системы интернационализации."""

import sys
from pathlib import Path

# Добавляем src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from use_cases.i18n_manager import I18nManagerImpl, I18nConfig
from entities.character import Character


def main():
    """Основная функция демо."""
    print("🌍 Демо системы локализации D&D Text MUD")
    print("=" * 50)
    
    # Инициализация системы i18n
    print("\n📦 Инициализация системы локализации...")
    manager = I18nManagerImpl(Path("data"))
    config = I18nConfig(default_language="ru", auto_detect_language=False)
    manager.initialize(config)
    manager.load_all_translations()
    
    # Получаем переводчик
    translator = manager.get_translator()
    
    # Демонстрация UI переводов
    print("\n🎨 UI переводы:")
    ui_examples = [
        ("ui.main_menu.title", "Главное меню"),
        ("ui.main_menu.new_game", "Новая игра"),
        ("ui.main_menu.load_game", "Загрузить игру"),
        ("ui.main_menu.settings", "Настройки"),
        ("ui.main_menu.exit", "Выход"),
    ]
    
    for key, description in ui_examples:
        translated = translator.translate(key)
        print(f"  {description}: {translated}")
    
    # Демонстрация игровых данных
    print("\n⚔️ Игровые данные:")
    game_examples = [
        ("races.human.name", "Человек"),
        ("races.elf.name", "Эльф"),
        ("races.dwarf.name", "Дварф"),
        ("classes.fighter.name", "Воин"),
        ("classes.wizard.name", "Волшебник"),
        ("skills.athletics.name", "Атлетика"),
        ("skills.stealth.name", "Скрытность"),
        ("abilities.strength.name", "Сила"),
        ("abilities.intelligence.name", "Интеллект"),
        ("sizes.MEDIUM", "Средний"),
        ("languages.common", "Общий"),
        ("backgrounds.acolyte.name", "Послушник"),
    ]
    
    for key, description in game_examples:
        translated = translator.translate(key)
        print(f"  {description}: {translated}")
    
    # Демонстрация персонажа с локализацией
    print("\n👤 Персонаж с локализацией:")
    character = Character(name="Воин", level=5)
    character.set_translator(translator)
    
    # Устанавливаем разные статусы для демонстрации
    statuses = [
        ("character.status.dead", 0, 50),
        ("character.status.healthy", 45, 50),
        ("character.status.wounded", 25, 50),
        ("character.status.heavily_wounded", 10, 50),
    ]
    
    for status_key, hp, max_hp in statuses:
        character.hit_points = hp
        character.max_hit_points = max_hp
        status = character.get_status()
        print(f"  {status_key} ({hp}/{max_hp} HP): {status}")
    
    # Демонстрация простого UI с локализацией
    print("\n🖥️ Интерфейс с локализацией:")
    
    class DemoUI:
        def __init__(self):
            self._translator = None
        
        def set_translator(self, translator):
            self._translator = translator
        
        def t(self, key, **kwargs):
            if self._translator:
                return self._translator.translate(key, **kwargs)
            return key
    
    ui = DemoUI()
    ui.set_translator(translator)
    
    ui_elements = [
        ("ui.main_menu.title", "Главное меню"),
        ("ui.main_menu.new_game", "Новая игра"),
        ("ui.main_menu.settings", "Настройки"),
    ]
    
    for key, description in ui_elements:
        localized = ui.t(key)
        print(f"  {description}: {localized}")
    
    # Демонстрация без переводчика
    print("\n❌ Без переводчика:")
    ui_no_translator = DemoUI()
    key = "ui.main_menu.title"
    fallback = ui_no_translator.t(key)
    print(f"  {key}: {fallback}")
    
    # Демонстрация переключения языков
    print("\n🔄 Переключение языков:")
    
    # Русский
    manager._i18n.set_language("ru")
    ru_title = translator.translate("ui.main_menu.title")
    print(f"  Русский: {ru_title}")
    
    # Английский
    manager._i18n.set_language("en")
    en_title = translator.translate("ui.main_menu.title")
    print(f"  Английский: {en_title}")
    
    # Статистика системы
    print("\n📊 Статистика системы:")
    stats = manager.get_statistics()
    print(f"  Текущий язык: {stats['current_language']}")
    print(f"  Язык по умолчанию: {stats['config']['default_language']}")
    print(f"  Fallback язык: {stats['config']['fallback_language']}")
    print(f"  Кэш включен: {stats['config']['cache_enabled']}")
    
    print("\n" + "=" * 50)
    print("✅ Демо завершено! Система локализации работает корректно.")
    print("\n💡 Попробуйте изменить язык в системе или добавить новые переводы!")


if __name__ == "__main__":
    main()
