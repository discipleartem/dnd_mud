# 📖 Техническая документация Window Manager

## 🎯 Обзор

Window Manager - это Singleton компонент для управления терминалом, отвечающий за измерение размера окна и обеспечение корректного переноса текста для избежания скролинга и растягивания интерфейса.

## 🏗️ Архитектура

### Паттерны проектирования
- **Singleton** - глобальный экземпляр для всего приложения
- **SRP** (Single Responsibility Principle) - отвечает только за управление окном
- **Dataclass** - для структуры `TerminalSize`

### Основные компоненты

```python
@dataclass
class TerminalSize:
    """Размер терминала."""
    width: int
    height: int
    
    def is_valid(self, min_width: int = 80, min_height: int = 24) -> bool:
        """Проверка минимального размера."""
        return self.width >= min_width and self.height >= min_height

class WindowManager:
    """Singleton класс для управления окном терминала."""
```

## 🔧 Функциональность

### 1. Определение размера терминала

**Кроссплатформенная поддержка:**
- **Linux/Unix**: `fcntl.ioctl()` через `termios.TIOCGWINSZ`
- **Windows**: `ctypes.windll.kernel32.GetConsoleScreenBufferInfo()`
- **Fallback**: `shutil.get_terminal_size()` (работает в cx_Freeze)
- **Резерв**: минимальные значения 80x24

```python
def get_terminal_size(self) -> TerminalSize:
    """Получение размера терминала."""
    try:
        # Основной метод через shutil
        size = shutil.get_terminal_size(fallback=(self.MIN_WIDTH, self.MIN_HEIGHT))
        self._current_size = TerminalSize(width=size.columns, height=size.lines)
    except Exception:
        # Платформоспецифичные методы
        # Windows/Linux реализации
```

### 2. Проверка минимального размера

```python
def check_minimum_size(self) -> Tuple[bool, str]:
    """Проверка минимального размера терминала."""
    size = self.get_terminal_size()
    
    if not size.is_valid(self.MIN_WIDTH, self.MIN_HEIGHT):
        message = (
            f"Размер терминала {size.width}x{size.height} слишком мал.\n"
            f"Минимальный размер: {self.MIN_WIDTH}x{self.MIN_HEIGHT}.\n"
            f"Пожалуйста, увеличьте окно терминала."
        )
        return False, message
    
    return True, ""
```

### 3. Умный перенос текста

**Алгоритм переноса:**
1. Разбиение текста на параграфы по `\n`
2. Обработка каждого параграфа отдельно
3. Разбиение длинных слов на части
4. Сохранение отступов и пустых строк
5. Учёт рамок и границ интерфейса

```python
def wrap_text(self, text: str, width: Optional[int] = None,
              indent: int = 0) -> List[str]:
    """Автоматический перенос текста по ширине."""
    if width is None:
        size = self.get_terminal_size()
        width = size.width - indent - 2  # -2 для рамок
    
    # Разбиваем по существующим переносам строк
    paragraphs = text.split('\n')
    wrapped_lines = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            wrapped_lines.append('')
            continue
        
        # Разбиваем на слова и обрабатываем перенос
        words = paragraph.split()
        current_line = ' ' * indent
        
        for word in words:
            # Обработка очень длинных слов
            if len(word) > width:
                if current_line.strip():
                    wrapped_lines.append(current_line)
                    current_line = ' ' * indent
                
                # Разбиваем длинное слово
                for i in range(0, len(word), width - indent):
                    wrapped_lines.append(' ' * indent + word[i:i + width - indent])
                continue
            
            # Проверяем, поместится ли слово
            test_line = current_line + (' ' if current_line.strip() else '') + word
            
            if len(test_line) <= width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)
                current_line = ' ' * indent + word
        
        # Добавляем последнюю строку параграфа
        if current_line.strip():
            wrapped_lines.append(current_line)
    
    return wrapped_lines
```

### 4. Вспомогательные функции

```python
def clear_screen(self) -> None:
    """Очистка экрана терминала."""
    os.system('cls' if sys.platform == 'win32' else 'clear')

def center_text(self, text: str, width: Optional[int] = None) -> str:
    """Центрирование текста."""
    if width is None:
        size = self.get_terminal_size()
        width = size.width
    
    text_length = len(text)
    if text_length >= width:
        return text
    
    padding = (width - text_length) // 2
    return ' ' * padding + text

def get_content_width(self, border: int = 2) -> int:
    """Получение ширины для контента (с учётом рамок)."""
    size = self.get_terminal_size()
    return max(size.width - border * 2, 40)  # минимум 40 символов

def get_content_height(self, border: int = 2) -> int:
    """Получение высоты для контента (с учётом рамок)."""
    size = self.get_terminal_size()
    return max(size.height - border * 2, 20)  # минимум 20 строк
```

## 🔗 Интеграция с UI компонентами

### 1. Интеграция в main.py

```python
def check_environment() -> bool:
    """Проверка окружения перед запуском игры."""
    console = Console()
    
    # Проверка размера терминала
    is_valid, message = window_manager.check_minimum_size()
    if not is_valid:
        console.print(Panel(
            message,
            title="Ошибка размера терминала",
            border_style="red"
        ))
        return False
    
    return True
```

### 2. Интеграция в MenuBase

```python
def render(self) -> None:
    """Отрисовка меню."""
    # Получение размера терминала
    size = window_manager.get_terminal_size()
    
    # Проверка минимального размера
    if not size.is_valid():
        self.console.print(f"[red]Размер терминала {size.width}x{size.height} слишком мал[/red]")
        self.console.print(f"[yellow]Минимальный размер: {window_manager.MIN_WIDTH}x{window_manager.MIN_HEIGHT}[/yellow]")
        return
    
    # Очистка экрана и отрисовка компонентов
    self.console.clear()
    self._render_title()
    self._render_items()
    self._render_hint()

def _render_title(self) -> None:
    """Отрисовка заголовка меню."""
    size = window_manager.get_terminal_size()
    content_width = window_manager.get_content_width(border=4)
    
    # Адаптивный заголовок - перенос длинных заголовков
    title_lines = window_manager.wrap_text(self.title, width=content_width)
    
    if len(title_lines) == 1:
        # Короткий заголовок - центрируем
        title_text = Text(title_lines[0], style="bold cyan", justify="center")
    else:
        # Длинный заголовок - выравниваем по левому краю с переносом
        title_text = Text()
        for line in title_lines:
            title_text.append(line + "\n", style="bold cyan")
```

### 3. Интеграция в MainMenu

```python
def _render_title(self) -> None:
    """Красивая отрисовка заголовка игры."""
    # Проверка размера терминала для ASCII-арт
    size = window_manager.get_terminal_size()
    art_lines = title_art.strip().split('\n')
    max_line_length = max(len(line) for line in art_lines)
    
    # Если терминал слишком узкий для ASCII-арт, показываем упрощенную версию
    if max_line_length > size.width:
        # Упрощенный заголовок для узких терминалов
        simple_title = "DnD MUD Game\nDungeons & Dragons 5 Edition"
        title_lines = window_manager.wrap_text(simple_title, width=size.width - 4)
        
        title_text = Text()
        for line in title_lines:
            title_text.append(line + "\n", style="bold bright_cyan")
    else:
        # Полный ASCII-арт для нормальных терминалов
        title_text = Text(title_art)
        title_text.stylize("bold bright_cyan")
    
    self.console.print(Align.center(title_text))
```

## 🧪 Тестирование

### Базовые тесты

```python
def test_singleton():
    """Тест Singleton паттерна."""
    wm1 = WindowManager()
    wm2 = WindowManager()
    assert wm1 is wm2

def test_get_terminal_size():
    """Тест определения размера терминала."""
    wm = WindowManager()
    size = wm.get_terminal_size()
    assert size.width >= 80
    assert size.height >= 24

def test_wrap_text():
    """Тест переноса текста."""
    wm = WindowManager()
    text = "This is a very long text that needs to be wrapped"
    lines = wm.wrap_text(text, width=20)
    assert all(len(line) <= 20 for line in lines)
```

### Тестирование граничных случаев

1. **Очень длинные слова** - корректное разбиение на части
2. **Пустые параграфы** - сохранение структуры текста
3. **Отступы** - правильная обработка indent параметра
4. **Минимальная ширина** - fallback значения
5. **Разные платформы** - кроссплатформенная работа

## 📊 Производительность

### Оптимизации
- **Кэширование размера** - сохранение текущего размера в `_current_size`
- **Lazy evaluation** - определение размера только при необходимости
- **Fallback цепочка** - от быстрых методов к медленным

### Память
- **Минимальное использование** - только необходимые данные
- **Очистка строк** - эффективная работа с текстом

## 🔧 Конфигурация

### Константы
```python
MIN_WIDTH = 80    # Минимальная ширина терминала
MIN_HEIGHT = 24   # Минимальная высота терминала
```

### Настройки
- Минимальные размеры можно изменить через константы класса
- Fallback значения настраиваются в методах
- Ширина рамок параметризуется в методах контента

## 🚀 Использование

### Базовое использование
```python
from src.core.window_manager import window_manager

# Получение размера
size = window_manager.get_terminal_size()
print(f"Размер: {size.width}x{size.height}")

# Проверка размера
is_valid, message = window_manager.check_minimum_size()
if not is_valid:
    print(f"Ошибка: {message}")

# Перенос текста
lines = window_manager.wrap_text(long_text, width=40)
for line in lines:
    print(line)
```

### В UI компонентах
```python
class MyMenu(MenuBase):
    def _render_content(self):
        size = window_manager.get_terminal_size()
        content_width = window_manager.get_content_width(border=4)
        
        # Адаптивный контент
        wrapped_text = window_manager.wrap_text(
            self.content, 
            width=content_width
        )
        # ... отрисовка
```

## 🔮 Будущие улучшения

### Планируемые функции
1. **Реальное время** - отслеживание изменения размера терминала
2. **Callbacks** - уведомления при изменении размера
3. **Анимации** - плавные переходы при изменении размера
4. **Темы** - адаптация цветовых схем под размер
5. **Мульти-монитор** - поддержка нескольких дисплеев

### Оптимизации
1. **Асинхронное определение** - неблокирующая проверка размера
2. **Кэширование** - более умное кэширование результатов
3. **Прогнозирование** - предсказание размера при запуске

## 📝 История изменений

### v0.1.0-alpha
- ✅ Базовая реализация Window Manager
- ✅ Кроссплатформенная поддержка
- ✅ Алгоритм переноса текста
- ✅ Интеграция с UI компонентами
- ✅ Проверка минимального размера
- ✅ Адаптивные заголовки

### Планируемые версии
- v0.2.0: Реальное время и callbacks
- v0.3.0: Анимации и темы
- v1.0.0: Полная функциональность

---

**Window Manager** обеспечивает корректную работу интерфейса в терминалах любого размера, предотвращая скролинг и растягивание элементов UI.
