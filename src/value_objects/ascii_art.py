"""Value Object для ASCII-арта.

Следует KISS и YAGNI - просто и без излишеств.
"""

from dataclasses import dataclass

from src.value_objects.base_validatable import BaseValidatable


@dataclass(frozen=True)
class AsciiArt:
    """Неизменяемый объект ASCII-арта.

    Следует KISS и YAGNI - просто и понятно.
    """

    value: str

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        object.__setattr__(
            self, "value", BaseValidatable.validate_ascii_art(self.value)
        )

    def is_empty(self) -> bool:
        """Проверить, является ли ASCII-арт пустым."""
        return not self.value.strip()

    @classmethod
    def create_dnd_logo(cls) -> "AsciiArt":
        """Создать ASCII-логотип D&D."""
        logo = (
            "██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗███████╗\n"
            "██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║██╔════╝\n"
            "██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║███████╗\n"
            "██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║╚════██║\n"
            "██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║███████║\n"
            "╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝\n"
            "\n"
            "             ██████╗ ██████╗  █████╗  ██████╗  ██████╗ ███╗   ██╗███████╗\n"
            "             ██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔═══██╗████╗  ██║██╔════╝\n"
            "             ██║  ██║██████╔╝███████║██║  ███╗██║   ██║██╔██╗ ██║███████╗\n"
            "             ██║  ██║██╔══██╗██╔══██║██║   ██║██║   ██║██║╚██╗██║╚════██║\n"
            "             ██████╔╝██║  ██║██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║███████║\n"
            "             ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝"
        )
        return cls(value=logo)

    def get_value(self) -> str:
        """Получить значение ASCII-арта."""
        return self.value

    def get_line_count(self) -> int:
        """Получить количество строк в ASCII-арте."""
        return len(self.value.splitlines()) if self.value else 0

    def __str__(self) -> str:
        """Строковое представление."""
        return self.value
