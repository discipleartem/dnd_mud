"""Фабрика для внедрения зависимостей.

Реализует паттерн Factory для создания объектов с правильными зависимостями.
"""

from src.use_cases.character_creation import (
    CreateCharacterUseCase, GetRaceChoicesUseCase, GetClassChoicesUseCase
)
from src.ui.character_controller import CharacterController
from src.ui.character_creator import CharacterCreator
from src.frameworks.repositories import (
    YAMLRaceRepository, YAMLClassRepository, InMemoryCharacterRepository
)


class DIContainer:
    """Контейнер внедрения зависимостей."""
    
    def __init__(self) -> None:
        """Инициализировать контейнер."""
        self._race_repository: YAMLRaceRepository | None = None
        self._class_repository: YAMLClassRepository | None = None
        self._character_repository: InMemoryCharacterRepository | None = None
        self._create_character_use_case: CreateCharacterUseCase | None = None
        self._get_race_choices_use_case: GetRaceChoicesUseCase | None = None
        self._get_class_choices_use_case: GetClassChoicesUseCase | None = None
        self._character_controller: CharacterController | None = None
        self._character_creator: CharacterCreator | None = None
    
    @property
    def race_repository(self) -> YAMLRaceRepository:
        """Получить репозиторий рас."""
        if self._race_repository is None:
            self._race_repository = YAMLRaceRepository()
        return self._race_repository
    
    @property
    def class_repository(self) -> YAMLClassRepository:
        """Получить репозиторий классов."""
        if self._class_repository is None:
            self._class_repository = YAMLClassRepository()
        return self._class_repository
    
    @property
    def character_repository(self) -> InMemoryCharacterRepository:
        """Получить репозиторий персонажей."""
        if self._character_repository is None:
            self._character_repository = InMemoryCharacterRepository()
        return self._character_repository
    
    @property
    def create_character_use_case(self) -> CreateCharacterUseCase:
        """Получить Use Case создания персонажа."""
        if self._create_character_use_case is None:
            self._create_character_use_case = CreateCharacterUseCase(
                self.race_repository,
                self.class_repository,
                self.character_repository
            )
        return self._create_character_use_case
    
    @property
    def get_race_choices_use_case(self) -> GetRaceChoicesUseCase:
        """Получить Use Case получения списка рас."""
        if self._get_race_choices_use_case is None:
            self._get_race_choices_use_case = GetRaceChoicesUseCase(
                self.race_repository
            )
        return self._get_race_choices_use_case
    
    @property
    def get_class_choices_use_case(self) -> GetClassChoicesUseCase:
        """Получить Use Case получения списка классов."""
        if self._get_class_choices_use_case is None:
            self._get_class_choices_use_case = GetClassChoicesUseCase(
                self.class_repository
            )
        return self._get_class_choices_use_case
    
    @property
    def character_controller(self) -> CharacterController:
        """Получить контроллер персонажей."""
        if self._character_controller is None:
            self._character_controller = CharacterController(
                self.create_character_use_case,
                self.get_race_choices_use_case,
                self.get_class_choices_use_case
            )
        return self._character_controller
    
    @property
    def character_creator(self) -> CharacterCreator:
        """Получить создатель персонажей."""
        if self._character_creator is None:
            self._character_creator = CharacterCreator(
                self.character_controller
            )
        return self._character_creator


# Глобальный экземпляр контейнера
_container = DIContainer()


def get_character_creator() -> CharacterCreator:
    """Получить создатель персонажей."""
    return _container.character_creator


def get_character_controller() -> CharacterController:
    """Получить контроллер персонажей."""
    return _container.character_controller