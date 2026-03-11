"""Dependency Injection контейнер.

Следует Clean Architecture - управляет зависимостями приложения.
Создаёт и связывает все компоненты архитектуры.
"""

from typing import Dict, Any, Optional

from src.use_cases.welcome_user import WelcomeUserUseCase
from src.controllers.welcome_controller import WelcomeController
from src.interfaces.services.translation_service_interface import TranslationService
from src.interfaces.services.ascii_art_service import AsciiArtService
from src.frameworks.services.file_translation_service import FileTranslationService
from src.frameworks.services.simple_ascii_art_service import SimpleAsciiArtService
from src.frameworks.services.translation_service_adapter import TranslationServiceAdapter


class DIContainer:
    """Контейнер зависимостей.
    
    Следует Clean Architecture - централизованное управление
    созданием и связыванием компонентов.
    """
    
    def __init__(self) -> None:
        """Инициализация контейнера."""
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._setup_services()
    
    def _setup_services(self) -> None:
        """Настроить сервисы в контейнере."""
        # Framework Layer - конкретные реализации
        self._services["translation_service"] = lambda: TranslationServiceAdapter()
        self._services["ascii_art_service"] = lambda: SimpleAsciiArtService()
        
        # Use Cases - бизнес-логика
        self._services["welcome_use_case"] = self._create_welcome_use_case
        
        # Controllers - адаптеры интерфейсов
        self._services["welcome_controller"] = self._create_welcome_controller
    
    def get(self, service_name: str) -> Any:
        """Получить сервис из контейнера.
        
        Args:
            service_name: Имя сервиса
            
        Returns:
            Экземпляр сервиса
            
        Raises:
            KeyError: Если сервис не найден
        """
        if service_name not in self._services:
            raise KeyError(f"Сервис '{service_name}' не найден в контейнере")
        
        # Для синглтонов возвращаем существующий экземпляр
        if service_name in self._singletons:
            return self._singletons[service_name]
        
        # Создаём новый экземпляр
        service_factory = self._services[service_name]
        
        if callable(service_factory):
            service = service_factory()
        else:
            service = service_factory
        
        # Сохраняем как синглтон
        self._singletons[service_name] = service
        
        return service
    
    def _create_welcome_use_case(self) -> WelcomeUserUseCase:
        """Создать Use Case приветствия.
        
        Returns:
            Use Case приветствия
        """
        translation_service = self.get("translation_service")
        ascii_art_service = self.get("ascii_art_service")
        return WelcomeUserUseCase(translation_service, ascii_art_service)
    
    def _create_welcome_controller(self) -> WelcomeController:
        """Создать контроллер приветствия.
        
        Returns:
            Контроллер приветствия
        """
        welcome_use_case = self.get("welcome_use_case")
        return WelcomeController(welcome_use_case)
    
    def register_singleton(self, service_name: str, instance: Any) -> None:
        """Зарегистрировать синглтон.
        
        Args:
            service_name: Имя сервиса
            instance: Экземпляр сервиса
        """
        self._singletons[service_name] = instance
    
    def register_factory(self, service_name: str, factory: callable) -> None:
        """Зарегистрировать фабрику сервиса.
        
        Args:
            service_name: Имя сервиса
            factory: Фабрика сервиса
        """
        self._services[service_name] = factory
    
    def clear_singletons(self) -> None:
        """Очистить синглтоны.
        
        Полезно для тестирования.
        """
        self._singletons.clear()
    
    def get_service_names(self) -> list:
        """Получить список имён сервисов.
        
        Returns:
            Список имён зарегистрированных сервисов
        """
        return list(self._services.keys())


# Глобальный контейнер для приложения
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Получить глобальный контейнер зависимостей.
    
    Returns:
        Экземпляр DIContainer
    """
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def reset_container() -> None:
    """Сбросить глобальный контейнер.
    
    Полезно для тестирования.
    """
    global _container
    _container = None


class ApplicationServices:
    """Фасад для доступа к основным сервисам приложения.
    
    Следует Clean Architecture - предоставляет удобный интерфейс
    для доступа к сервисам верхнего уровня.
    """
    
    def __init__(self, container: DIContainer = None) -> None:
        """Инициализация фасада.
        
        Args:
            container: Контейнер зависимостей
        """
        self._container = container or get_container()
    
    @property
    def welcome_controller(self) -> WelcomeController:
        """Получить контроллер приветствия.
        
        Returns:
            Контроллер приветствия
        """
        return self._container.get("welcome_controller")
    
    @property
    def translation_service(self) -> TranslationService:
        """Получить сервис переводов.
        
        Returns:
            Сервис переводов
        """
        return self._container.get("translation_service")
    
    @property
    def ascii_art_service(self) -> AsciiArtService:
        """Получить сервис ASCII art.
        
        Returns:
            Сервис ASCII art
        """
        return self._container.get("ascii_art_service")