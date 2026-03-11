"""Простые тесты для D&D MUD.

Следует принципам KISS - без pytest и сложных декораторов.
Простые assert'ы для проверки функциональности.
"""

def test_welcome_service():
    """Тест приветственного сервиса."""
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

    from services.welcome_service import WelcomeService

    service = WelcomeService()
    screen = service.create_welcome_screen()

    assert screen is not None
    assert screen.language.get_code() == "ru"
    assert screen.has_ascii_art() is True
    print("✓ WelcomeService тест пройден")


def test_use_case():
    """Тест сценария использования."""
    from src.welcome_dto import WelcomeScreenRequest
    from src.welcome_use_case import ShowWelcomeScreenUseCase

    use_case = ShowWelcomeScreenUseCase()
    request = WelcomeScreenRequest(language="ru", show_ascii_art=True)

    response = use_case.execute(request)

    assert response.language == "ru"
    assert response.ascii_art is not None
    print("✓ UseCase тест пройден")


def test_entity():
    """Тест сущности."""
    from src.value_objects.ascii_art import AsciiArt
    from src.value_objects.language import Language
    from src.value_objects.welcome_content import WelcomeContent
    from src.welcome_screen import WelcomeScreen

    content = WelcomeContent(
        title="Test Title",
        subtitle="Test Subtitle",
        description="Test Description"
    )

    screen = WelcomeScreen(
        content=content,
        ascii_art=AsciiArt.create_dnd_logo(),
        language=Language.from_string("en"),
        press_enter_text="Press Enter"
    )

    assert screen.content.get_title() == "Test Title"
    assert screen.language.get_code() == "en"
    assert screen.has_ascii_art() is True
    print("✓ Entity тест пройден")


def test_value_objects():
    """Тест Value Objects."""
    from src.value_objects.ascii_art import AsciiArt
    from src.value_objects.language import Language
    from src.value_objects.welcome_content import WelcomeContent

    # Тест ASCII Art
    art = AsciiArt(value="Test ASCII Art")
    assert art.value == "Test ASCII Art"
    assert not art.is_empty()
    assert art.get_line_count() == 1

    # Тест Language
    lang = Language.from_string("ru")
    assert lang.get_code() == "ru"
    assert lang.is_supported()
    assert lang.is_russian()

    # Тест WelcomeContent
    content = WelcomeContent(
        title="Test Title",
        subtitle="Test Subtitle",
        description="Test Description"
    )
    assert content.get_title() == "Test Title"
    assert content.get_subtitle() == "Test Subtitle"
    assert content.get_description() == "Test Description"

    print("✓ Value Objects тест пройден")


def test_adapter():
    """Тест адаптера (без реального отображения)."""
    from src.console.welcome_adapter import WelcomeScreenAdapter
    from src.welcome_dto import WelcomeScreenResponse

    adapter = WelcomeScreenAdapter()
    response = WelcomeScreenResponse(
        title="Test",
        subtitle="Subtitle",
        description="Description",
        ascii_art=None,
        language="en",
        press_enter_text="Press Enter"
    )

    # Просто проверяем, что метод существует
    assert hasattr(adapter, 'display')
    assert hasattr(adapter, 'clear_screen')

    print("✓ Adapter тест пройден")


def test_validation():
    """Тест валидации."""
    from src.value_objects.ascii_art import AsciiArt
    from src.value_objects.language import Language
    from src.value_objects.welcome_content import WelcomeContent

    # Тест невалидных данных
    try:
        AsciiArt(value="")  # Пустой ASCII-арт
        assert False, "Должно быть исключение"
    except ValueError:
        pass  # Ожидаемое поведение

    try:
        Language.from_string("invalid")  # Невалидный язык
        assert False, "Должно быть исключение"
    except ValueError:
        pass  # Ожидаемое поведение

    try:
        WelcomeContent(title="", subtitle="Test", description="Test")  # Пустой заголовок
        assert False, "Должно быть исключение"
    except ValueError:
        pass  # Ожидаемое поведение

    print("✓ Validation тест пройден")


def run_all_tests():
    """Запустить все тесты."""
    print("Запуск тестов...")
    print()

    try:
        test_welcome_service()
        test_use_case()
        test_entity()
        test_value_objects()
        test_adapter()
        test_validation()

        print("\n🎉 Все тесты пройдены успешно!")
        print("Рефакторинг завершен успешно!")

    except Exception as e:
        print(f"\n❌ Тест провален: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
