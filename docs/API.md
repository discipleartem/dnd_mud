## API документация

### Основные классы и методы

#### Game

```python
class Game:
    def __init__(self) -> None:
        """Инициализация игры"""
    
    def start(self) -> None:
        """Запуск игры"""
    
    def main_loop(self) -> None:
        """Главный игровой цикл"""
    
    def shutdown(self) -> None:
        """Корректное завершение игры"""
```

#### StateManager

```python
class StateManager:
    def set_state(self, state: GameState) -> None:
        """Установка нового состояния"""
    
    def get_state(self) -> GameState:
        """Получение текущего состояния"""
    
    def can_continue(self) -> bool:
        """Проверка наличия активной игры"""
```

#### Character

```python
class Character:
    def __init__(self, name: str, race: str, char_class: str) -> None:
        """Создание персонажа"""
    
    def get_modifier(self, stat: str) -> int:
        """Получение модификатора характеристики"""
    
    def take_damage(self, damage: int) -> None:
        """Получение урона"""
    
    def heal(self, amount: int) -> None:
        """Лечение"""
    
    def level_up(self) -> None:
        """Повышение уровня"""
```

---

## Требования к производительности

### Минимальные требования
- Python 3.13+
- 100 MB свободной RAM
- 50 MB свободного места на диске

### Ограничения
- Размер сохранения: < 1 MB
- Время загрузки игры: < 2 секунды
- FPS отрисовки UI: 30+ (при необходимости анимаций)

---

## Безопасность и надёжность

### Обработка ошибок
- Все операции с файлами обёрнуты в try-except
- Валидация пользовательского ввода
- Graceful degradation при ошибках

### Сохранность данных
- Атомарное сохранение (сначала во временный файл)
- Backup предыдущего сохранения
- Проверка целостности при загрузке

---

## Совместимость

### Платформы
- ✅ Windows 10/11
- ✅ Linux (Ubuntu 20.04+)
- ⚠️ macOS (не тестировалось)

### Терминалы
- ✅ Windows Terminal
- ✅ PowerShell
- ✅ CMD
- ✅ Linux Terminal (gnome-terminal, konsole, etc.)
- ✅ VS Code Terminal

---

## Сборка и развёртывание

### PyInstaller конфигурация

```python
# dnd_mud_game.spec
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/yaml', 'data/yaml'),
    ],
    hiddenimports=['rich', 'yaml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
```

### Команды сборки

```bash
# Linux
pyinstaller --onefile --name dnd-game-linux src/main.py

# Windows
pyinstaller --onefile --name dnd-game-windows.exe src/main.py
```

---

## Тестирование

### Покрытие тестами
- Минимальное покрытие: 80%
- Критические системы: 100%

### Типы тестов
- Unit tests - тестирование отдельных компонентов
- Integration tests - тестирование взаимодействия систем
- E2E tests - тестирование полных сценариев

---

## Changelog

### v0.1.0 (В разработке)
- Инициализация проекта
- Структура проекта
- Базовая документация

---