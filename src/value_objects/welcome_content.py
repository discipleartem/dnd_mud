"""Value Object для контента приветственного экрана.

Следует KISS и YAGNI - просто и без излишеств.
"""

from dataclasses import dataclass

from src.value_objects.base_validatable import BaseValidatable


@dataclass(frozen=True)
class WelcomeContent:
    """Неизменяемый объект контента приветственного экрана.

    Следует KISS и YAGNI - просто и понятно.
    """

    title: str
    subtitle: str
    description: str

    def __post_init__(self) -> None:
        """Валидация после инициализации."""
        object.__setattr__(
            self, "title", BaseValidatable.validate_title(self.title)
        )
        object.__setattr__(
            self, "subtitle", BaseValidatable.validate_subtitle(self.subtitle)
        )
        object.__setattr__(
            self,
            "description",
            BaseValidatable.validate_description(self.description),
        )

    def get_title(self) -> str:
        """Получить заголовок."""
        return self.title

    def get_subtitle(self) -> str:
        """Получить подзаголовок."""
        return self.subtitle

    def get_description(self) -> str:
        """Получить описание."""
        return self.description

    def __str__(self) -> str:
        """Строковое представление."""
        return f"{self.title}\n{self.subtitle}\n{self.description}"
