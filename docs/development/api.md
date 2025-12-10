## API документация

### Основные классы и методы

#### StateManager

```python
class StateManager:
    """Управление состояниями игры (Singleton)"""
    
    def set_state(self, state: GameState, data: Optional[Dict[str, Any]] = None) -> None:
        """Установка нового состояния"""
    
    def get_state(self) -> GameState:
        """Получение текущего состояния"""
    
    def get_previous_state(self) -> Optional[GameState]:
        """Получение предыдущего состояния"""
    
    def can_continue(self) -> bool:
        """Проверка наличия активной игры"""
    
    def save_snapshot(self) -> GameSnapshot:
        """Сохранение снимка состояния"""
    
    def load_snapshot(self, snapshot: GameSnapshot) -> None:
        """Загрузка снимка состояния"""
```

#### WindowManager

```python
class WindowManager:
    """Управление окном терминала (Singleton)"""
    
    def get_terminal_size(self) -> TerminalSize:
        """Получение размера терминала"""
    
    def check_minimum_size(self) -> Tuple[bool, str]:
        """Проверка минимального размера терминала"""
    
    def wrap_text(self, text: str, width: Optional[int] = None) -> List[str]:
        """Перенос текста по ширине"""
```

#### LocalizationManager

```python
class LocalizationManager:
    """Менеджер локализации (Singleton)"""
    
    def set_language(self, language: str) -> None:
        """Установка языка интерфейса"""
    
    def get_language(self) -> str:
        """Получение текущего языка"""
    
    def get(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """Получение перевода по ключу"""
    
    def load_mod_localization(self, mod_id: str, mod_path: Path) -> None:
        """Загрузка локализации мода"""
    
    def load_adventure_localization(self, adventure_id: str, adventure_path: Path) -> None:
        """Загрузка локализации приключения"""
```

#### MenuBase

```python
class MenuBase(ABC):
    """Базовый класс для всех меню"""
    
    def add_item(self, label: str, action: Callable[[], Any],
                 enabled: bool = True, description: Optional[str] = None) -> None:
        """Добавление пункта меню"""
    
    def render(self) -> None:
        """Отрисовка меню"""
    
    def handle_input(self, user_input: str) -> Any:
        """Обработка ввода пользователя"""
    
    def run(self) -> None:
        """Запуск меню"""
```

#### MainMenu

```python
class MainMenu(MenuBase):
    """Главное меню игры"""
    
    def build_menu(self) -> None:
        """Построение пунктов главного меню"""
```

#### GameState

```python
class GameState(Enum):
    """Состояния игры"""
    MAIN_MENU = "main_menu"
    CHARACTER_CREATION = "character_creation"
    ADVENTURE = "adventure"
    COMBAT = "combat"
    INVENTORY = "inventory"
    REST = "rest"
    SETTINGS = "settings"
    LOAD_GAME = "load_game"
    EXIT = "exit"
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

### cx_Freeze конфигурация

Конфигурация находится в `pyproject.toml` и `setup.py`. Для создания исполняемого файла:

```bash
# Установить dev-зависимости
pip install -e ".[dev]"

# Создать сборку
python setup.py build

# Исполняемые файлы будут в build/exe.*/
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