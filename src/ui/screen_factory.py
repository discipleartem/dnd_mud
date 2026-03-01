"""Фабрика для создания экранов."""

from abc import ABC, abstractmethod

from interfaces.user_interface import UserInterface
from ui.screens import BaseScreen, MainMenuScreen


class ScreenFactory(ABC):
    """Абстрактная фабрика для создания экранов."""

    @abstractmethod
    def create_main_menu(self, ui: UserInterface) -> BaseScreen:
        """Создать главное меню."""
        return MainMenuScreen(ui)


class DefaultScreenFactory(ScreenFactory):
    """Фабрика экранов по умолчанию."""

    def create_main_menu(self, ui: UserInterface) -> BaseScreen:
        """Создать главное меню."""
        return MainMenuScreen(ui)
