"""Утилиты для пользовательского интерфейса.

Содержит общие функции и паттерны для UI.
Следует DRY принципу - Don't Repeat Yourself.
"""


def display_menu(title: str, options: list[str], prompt: str) -> None:
    """Отобразить меню с опциями.

    Args:
        title: Заголовок меню
        options: Список опций
        prompt: Приглашение к вводу
    """
    print(f"\n{title}")
    print("=" * 40)

    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    print(f"\n{prompt}")


def display_section(title: str, content: list[str]) -> None:
    """Отобразить секцию с содержимым.

    Args:
        title: Заголовок секции
        content: Содержимое секции
    """
    print(f"\n{title}")
    print("-" * 40)

    for line in content:
        print(f"  {line}")


def display_error(message: str) -> None:
    """Отобразить сообщение об ошибке.

    Args:
        message: Текст ошибки
    """
    print(f"❌ {message}")


def display_success(message: str) -> None:
    """Отобразить сообщение об успехе.

    Args:
        message: Текст сообщения
    """
    print(f"✅ {message}")


def display_warning(message: str) -> None:
    """Отобразить предупреждение.

    Args:
        message: Текст предупреждения
    """
    print(f"⚠️ {message}")


def display_info(message: str) -> None:
    """Отобразить информационное сообщение.

    Args:
        message: Текст сообщения
    """
    print(f"ℹ️ {message}")


def get_numeric_choice(
    max_option: int, prompt: str = "Выберите вариант", allow_zero: bool = False
) -> int:
    """Получить числовой выбор от пользователя.

    Args:
        max_option: Максимальный номер варианта
        prompt: Приглашение к вводу
        allow_zero: Разрешить выбор 0

    Returns:
        Номер выбранного варианта

    Raises:
        ValueError: При неверном вводе
    """
    while True:
        try:
            choice = input(f"{prompt}: ").strip()
            choice_num = int(choice)

            min_allowed = 0 if allow_zero else 1
            if min_allowed <= choice_num <= max_option:
                return choice_num
            else:
                display_error(
                    f"Введите число от {min_allowed} до {max_option}"
                )
        except ValueError:
            display_error("Введите корректное число")


def confirm_action(message: str) -> bool:
    """Запросить подтверждение действия.

    Args:
        message: Сообщение для подтверждения

    Returns:
        True если пользователь подтвердил
    """
    while True:
        choice = input(f"{message} (да/нет): ").strip().lower()
        if choice in ["да", "д", "yes", "y"]:
            return True
        elif choice in ["нет", "н", "no", "n"]:
            return False
        else:
            display_error("Введите 'да' или 'нет'")


def format_list(items: list[str], separator: str = ", ") -> str:
    """Отформатировать список в строку.

    Args:
        items: Список элементов
        separator: Разделитель

    Returns:
        Отформатированная строка
    """
    return separator.join(items)


def truncate_text(text: str, max_length: int = 50) -> str:
    """Обрезать текст до указанной длины.

    Args:
        text: Текст для обрезки
        max_length: Максимальная длина

    Returns:
        Обрезанный текст
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
