"""Функции для пользовательского ввода."""


def _display_choices(
    choices: list[str], allow_cancel: bool, cancel_text: str, custom_only: bool
) -> None:
    """Отобразить варианты выбора."""
    if not custom_only:
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")

    if allow_cancel and not custom_only:
        print(f"  0. {cancel_text}")


def _handle_cancel_input(
    user_input: str, allow_cancel: bool, cancel_text: str, custom_only: bool
) -> bool:
    """Обработать ввод отмены.

    Returns:
        True если была отмена
    """
    if allow_cancel and user_input.lower() == cancel_text.lower():
        return True

    if allow_cancel and user_input == "0" and not custom_only:
        return True

    return False


def _handle_numeric_choice(user_input: str, choices: list[str]) -> str | None:
    """Обработать числовой выбор.

    Returns:
        Выбранный вариант или None если невалидный номер
    """
    try:
        choice_num = int(user_input)
        if 1 <= choice_num <= len(choices):
            return choices[choice_num - 1]
    except ValueError:
        pass

    return None


def _handle_custom_input(
    user_input: str,
    choices: list[str],
    allow_custom_input: bool,
    custom_only: bool,
) -> str | None:
    """Обработать произвольный ввод.

    Returns:
        Результат ввода или None
    """
    if custom_only:
        return user_input

    # Проверяем, это выбор из списка или произвольный ввод
    numeric_choice = _handle_numeric_choice(user_input, choices)
    if numeric_choice is not None:
        return numeric_choice

    try:
        int(user_input)  # Проверяем что это не число
    except ValueError:
        return user_input

    return None


def _show_error_message(
    user_input: str,
    choices: list[str],
    allow_cancel: bool,
    allow_custom_input: bool,
    custom_only: bool,
) -> None:
    """Показать сообщение об ошибке."""
    try:
        choice_num = int(user_input)
        if not (1 <= choice_num <= len(choices)):
            print("❌ Неверный номер варианта")
    except ValueError:
        if not allow_custom_input and not custom_only:
            print(f"❌ Введите число от 1 до {len(choices)}")

    if not allow_cancel and not allow_custom_input and not custom_only:
        print("❌ Попробуйте еще раз")


def get_user_choice(
    choices: list[str],
    prompt: str,
    allow_cancel: bool = False,
    cancel_text: str = "отмена",
    allow_custom_input: bool = False,
    custom_prompt: str = "или введите свое значение",
    custom_only: bool = False,
) -> str | int | None:
    """Получить выбор пользователя из списка или произвольный ввод.

    Args:
        choices: Список вариантов выбора
        prompt: Приглашение к вводу
        allow_cancel: Разрешить отмену
        cancel_text: Текст для отмены
        allow_custom_input: Разрешить произвольный ввод
        custom_prompt: Текст для произвольного ввода
        custom_only: Только произвольный ввод

    Returns:
        Выбор пользователя или None при отмене
    """
    while True:
        print(f"\n{prompt}")

        _display_choices(choices, allow_cancel, cancel_text, custom_only)

        if allow_custom_input or custom_only:
            print(f"  {custom_prompt}")

        user_input = input("> ").strip()

        # Проверка отмены
        if _handle_cancel_input(
            user_input, allow_cancel, cancel_text, custom_only
        ):
            return None

        # Произвольный ввод
        if allow_custom_input or custom_only:
            result = _handle_custom_input(
                user_input, choices, allow_custom_input, custom_only
            )
            if result is not None:
                return result

        # Выбор из списка
        result = _handle_numeric_choice(user_input, choices)
        if result is not None:
            return result
        else:
            _show_error_message(
                user_input,
                choices,
                allow_cancel,
                allow_custom_input,
                custom_only,
            )
