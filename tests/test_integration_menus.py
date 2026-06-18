"""Интеграционные тесты для модулей игры."""

import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для импорта main.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_localization():
    """Тест локализации: загрузка строк и получение по ключу."""
    from core.localization import get_string, load_strings

    # Загружаем английский
    strings_en = load_strings("en")
    assert get_string(strings_en, "menu.new_game") == "New Game"
    assert get_string(strings_en, "menu.exit") == "Exit"

    # Загружаем русский
    strings_ru = load_strings("ru")
    assert get_string(strings_ru, "menu.new_game") == "Новая игра"
    assert get_string(strings_ru, "settings.caption") == "НАСТРОЙКИ"

    print("✓ Локализация: все ключи загружены")


def test_settings():
    """Тест сохранения и загрузки настроек."""
    from core.settings import load_settings, save_settings

    # Сохраняем тестовые настройки
    save_settings("en", hardcore=True)

    loaded = load_settings()
    assert loaded["language"] == "en"
    assert loaded["hardcore"] is True

    # Проверяем дефолтные
    save_settings("ru", hardcore=False)

    loaded = load_settings()
    assert loaded["language"] == "ru"
    assert loaded["hardcore"] is False

    print("✓ Настройки: сохранение/загрузка OK")


def test_main_imports():
    """Тест, что main.py можно импортировать без ошибок."""
    import main

    assert main.VERSION == "0.1.0"
    assert callable(main.main)

    print(f"✓ main.py: импорты OK (версия {main.VERSION})")


if __name__ == "__main__":
    tests = [
        test_localization,
        test_settings,
        test_main_imports,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()  # type: ignore[no-untyped-call]
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
            failed += 1

    total = passed + failed
    print()
    print("=" * 50)
    print(f"  Результат: {passed}/{total} тестов пройдено")
    print("=" * 50)

    if failed > 0:
        exit(1)
