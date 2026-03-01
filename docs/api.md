# API Reference

## Обзор

D&D Text MUD предоставляет простой API для взаимодействия с основными компонентами игры. **После рефакторинга API стал проще и следует принципам KISS/YAGNI.**

**📋 Текущий статус:** MVP этап - приветственное окно, главное меню, навигация.

## Основные модули (упрощенные после рефакторинга)

### Core Module

#### Game

```python
from core.game import Game

class Game:
    """Главный класс игры (KISS - максимально простой)."""
    
    def __init__(self, ui: UserInterface) -> None:
        """Инициализация игры."""
        
    def run(self) -> None:
        """Запустить игровой цикл."""
```

#### Config

```python
from core.config import Config

class Config:
    """Класс конфигурации игры (KISS - максимально простой)."""
    
    def __init__(self) -> None:
        """Инициализация конфигурации."""
        
    def get(self, key: str, default: Any = None) -> Any:
        """Получить настройку."""
        
    def set(self, key: str, value: Any) -> None:
        """Установить настройку."""
        
    def load(self) -> None:
        """Загрузить конфигурацию."""
        
    def save(self) -> None:
        """Сохранить конфигурацию."""
```

### Entities Module

#### Character

```python
from entities.character import Character

class Character:
    """Бизнес-сущность персонажа D&D (KISS - просто)."""
    
    def __init__(self, name: str, level: int = 1, 
                 hit_points: int = 10, max_hit_points: int = 10):
        """Создание персонажа."""
        
    def modify_hp(self, amount: int) -> None:
        """Изменить HP (универсальный метод)."""
        
    def take_damage(self, damage: int) -> None:
        """Получить урон."""
        
    def heal(self, amount: int) -> None:
        """Восстановить здоровье."""
        
    def level_up(self) -> None:
        """Повысить уровень."""
        
    def is_alive(self) -> bool:
        """Проверить, жив ли персонаж."""
        
    def get_status(self) -> str:
        """Получить статус персонажа."""
```

#### GameSession

```python
from entities.game_session import GameSession

class GameSession:
    """Бизнес-сущность сессии игры (KISS - просто)."""
    
    def __init__(self, player: Character, session_name: str = "Новая игра"):
        """Создание сессии."""
        
    def advance_turn(self) -> None:
        """Продвинуть на один ход."""
        
    def get_session_info(self) -> str:
        """Получить информацию о сессии."""
        
    def is_new_game(self) -> bool:
        """Проверить, новая ли это игра."""
```
