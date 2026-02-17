"""
Модуль обработки пользовательского ввода D&D MUD.
"""

from __future__ import annotations


class InputHandler:
    """Класс для обработки пользовательского ввода."""

    def __init__(self) -> None:
        """Инициализация обработчика ввода."""
        pass

    def get_menu_choice(self, max_options: int) -> int:
        """Получает выбор пункта меню от пользователя."""
        max_attempts = 10
        attempts = 0

        try:
            while attempts < max_attempts:
                attempts += 1
                user_input = input(f"Введите номер (1-{max_options}): ").strip()

                if not user_input:
                    continue

                if user_input.isdigit():
                    choice = int(user_input)
                    if 1 <= choice <= max_options:
                        return choice
                    else:
                        print(f"Пожалуйста, введите число от 1 до {max_options}")
                else:
                    print("Пожалуйста, введите число")

            # Если превысили количество попыток, возвращаем последний пункт
            return max_options

        except (EOFError, KeyboardInterrupt):
            return max_options  # Возвращаем последний пункт (обычно "Выход")

    def get_text_input(self, prompt: str = "> ") -> str:
        """Получает текстовый ввод от пользователя."""
        try:
            return input(prompt)
        except (EOFError, KeyboardInterrupt):
            return ""

    def get_string(
        self, prompt: str, default: str = "", allow_empty: bool = True
    ) -> str:
        """Получает строку от пользователя."""
        max_attempts = 10
        attempts = 0

        while attempts < max_attempts:
            attempts += 1
            try:
                if default:
                    full_prompt = f"{prompt} [{default}]"
                else:
                    full_prompt = f"{prompt}"

                user_input = input(full_prompt).strip()

                if not user_input and default:
                    return default

                if not user_input and not allow_empty:
                    print("Поле не может быть пустым")
                    continue

                return user_input

            except (EOFError, KeyboardInterrupt):
                return default
            except Exception:
                # Перехватываем неожиданные исключения и возвращаем значение по умолчанию
                return default

        # Если превысили количество попыток, возвращаем значение по умолчанию
        return default

    def get_int(
        self,
        prompt: str,
        min_value: int = None,
        max_value: int = None,
        default: int = None,
    ) -> int:
        """Получает целое число от пользователя."""
        max_attempts = 10
        attempts = 0

        while attempts < max_attempts:
            attempts += 1
            try:
                if default is not None:
                    full_prompt = f"{prompt} [{default}]"
                else:
                    full_prompt = f"{prompt}"

                user_input = input(full_prompt).strip()

                if not user_input and default is not None:
                    return default

                if not user_input:
                    print("Введите число")
                    continue

                value = int(user_input)

                if min_value is not None and value < min_value:
                    print(f"Значение должно быть не менее {min_value}")
                    continue

                if max_value is not None and max_value > 0 and value > max_value:
                    print(f"Значение должно быть не более {max_value}")
                    continue

                return value

            except ValueError:
                print("Пожалуйста, введите корректное число")
            except (EOFError, KeyboardInterrupt):
                return default if default is not None else min_value or 0
            except Exception:
                # Перехватываем неожиданные исключения и возвращаем значение по умолчанию
                return default if default is not None else min_value or 0

        # Если превысили количество попыток, возвращаем значение по умолчанию
        return default if default is not None else min_value or 0

    def wait_for_enter(self, prompt: str = "Нажмите Enter для продолжения...") -> None:
        """Ожидает нажатия Enter."""
        try:
            input(prompt)
        except (EOFError, KeyboardInterrupt):
            pass


# Глобальный экземпляр обработчика ввода
input_handler = InputHandler()
