# Участие в разработке

## Как внести вклад в проект

Мы рады любому вкладу в развитие D&D Text MUD! Вот руководство по тому, как вы можете помочь.

## Начало работы

### 1. Форк репозитория

1. Перейдите на [GitHub репозиторий](https://github.com/discipleartem/dnd_mud)
2. Нажмите кнопку "Fork" в правом верхнем углу
3. Клонируйте ваш форк локально:

```bash
git clone https://github.com/YOUR_USERNAME/dnd_mud.git
cd dnd_mud
```

### 2. Настройка окружения

```bash
# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -e ".[dev]"

# Настройка pre-commit hooks
pre-commit install
```

### 3. Создание ветки

```bash
# Создание новой ветки для вашей задачи
git checkout -b feature/amazing-feature

# Или для исправления ошибки
git checkout -b fix/bug-description
```

## Типы вкладов

### 🐛 Исправление ошибок

1. Проверьте [Issues](https://github.com/discipleartem/dnd_mud/issues) на наличие похожих проблем
2. Если нет, создайте новый Issue с описанием ошибки
3. Создайте ветку для исправления
4. Напишите тесты, воспроизводящие ошибку
5. Исправьте ошибку
6. Убедитесь, что все тесты проходят

### ✨ Новые функции

1. Проверьте [Issues](https://github.com/discipleartem/dnd_mud/issues) на наличие запросов на функции
2. Если нет, создайте новый Issue с описанием функции
3. Обсудите реализацию с командой
4. Создайте ветку для разработки
5. Реализуйте функцию с тестами
6. Обновите документацию

### 📚 Документация

1. Улучшение существующей документации
2. Добавление примеров использования
3. Перевод документации на другие языки
4. Создание туториалов и гайдов

### 🎨 Контент

1. Новые расы, классы, предыстории
2. Новые приключения и квесты
3. Предметы и заклинания
4. Локализация на новые языки

## Стандарты кода

### Стиль кода

Мы используем следующие инструменты для поддержания качества кода:

- **Black** для форматирования кода
- **Ruff** для проверки стиля и линтинга
- **MyPy** для проверки типов
- **Pytest** для тестирования

### Форматирование

```bash
# Форматирование кода
black src tests

# Проверка стиля
ruff check src tests

# Исправление стиля
ruff check --fix src tests
```

### Типизация

```python
# Всегда используйте type hints
from typing import List, Dict, Optional, Union

def calculate_damage(
    attacker: Character,
    target: Character,
    weapon: Weapon,
    modifier: Optional[int] = None
) -> int:
    """Расчет урона с полной типизацией"""
    base_damage = weapon.damage.roll()
    strength_bonus = attacker.get_ability_modifier("strength")
    
    total_damage = base_damage + strength_bonus
    if modifier:
        total_damage += modifier
        
    return max(0, total_damage)
```

### Документация

```python
class Character:
    """Класс персонажа D&D.
    
    Attributes:
        name: Имя персонажа
        race: Раса персонажа
        character_class: Класс персонажа
        level: Текущий уровень
        
    Example:
        >>> character = Character("Арагорн", human, fighter, soldier)
        >>> character.level
        1
    """
    
    def get_ability_score(self, ability: str) -> int:
        """Получение значения характеристики.
        
        Args:
            ability: Название характеристики (strength, dexterity, etc.)
            
        Returns:
            Значение характеристики от 1 до 20
            
        Raises:
            ValueError: Если характеристика неизвестна
            
        Example:
            >>> character.get_ability_score("strength")
            16
        """
```

## Тестирование

### Написание тестов

```python
import pytest
from dnd_mud.character.character import Character
from dnd_mud.data.models import Race, Class, Background

class TestCharacter:
    """Тесты класса персонажа"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.race = Race(name="Человек", ...)
        self.character_class = Class(name="Воин", ...)
        self.background = Background(name="Солдат", ...)
        self.character = Character("Тест", self.race, self.character_class, self.background)
    
    def test_character_creation(self):
        """Тест создания персонажа"""
        assert self.character.name == "Тест"
        assert self.character.level == 1
        assert self.character.is_alive() == True
    
    def test_ability_score_calculation(self):
        """Тест расчета характеристик"""
        self.character.set_ability_score("strength", 16)
        assert self.character.get_ability_score("strength") == 16
        assert self.character.get_ability_modifier("strength") == 3
    
    def test_level_up(self):
        """Тест повышения уровня"""
        initial_level = self.character.level
        self.character.add_experience(300)  # Достаточно для 2 уровня
        assert self.character.level == initial_level + 1
```

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=dnd_mud --cov-report=html

# Конкретный тест
pytest tests/test_character.py::TestCharacter::test_character_creation

# Тесты с метками
pytest -m "unit"  # Только unit тесты
pytest -m "integration"  # Только integration тесты
pytest -m "not slow"  # Все тесты кроме медленных
```

### Покрытие кода

Мы стремимся к покрытию кода не менее 80%. Проверьте покрытие перед отправкой PR:

```bash
pytest --cov=dnd_mud --cov-fail-under=80
```

## Процесс Pull Request

### 1. Подготовка

```bash
# Убедитесь, что код актуален
git checkout main
git pull upstream main

# Переключитесь на вашу ветку
git checkout feature/amazing-feature

# Обновите ветку
git rebase main
```

### 2. Проверка качества

```bash
# Запустите все проверки
black src tests
ruff check src tests
mypy src
pytest --cov=dnd_mud
```

### 3. Коммиты

Используйте осмысленные сообщения коммитов:

```
feat: добавление системы заклинаний
fix: исправление расчета урона
docs: обновление документации API
test: добавление тестов для персонажа
refactor: оптимизация загрузки данных
```

### 4. Создание Pull Request

1. Отправьте ветку в ваш форк:
```bash
git push origin feature/amazing-feature
```

2. Создайте Pull Request на GitHub
3. Заполните шаблон PR
4. Дождитесь ревью

### 5. Ревью и изменения

- Отвечайте на комментарии ревьюеров
- Вносите необходимые изменения
- Обновляйте PR по необходимости

## Структура проекта

### Директории

```
src/dnd_mud/
├── core/           # Ядро игры
├── ui/             # Пользовательский интерфейс
├── data/           # Управление данными
├── character/      # Система персонажей
├── combat/         # Боевая система
├── adventure/      # Приключения
├── mods/           # Система модов
├── save/           # Система сохранения
└── i18n/           # Локализация

tests/
├── unit/           # Unit тесты
├── integration/    # Integration тесты
└── e2e/            # End-to-end тесты

docs/               # Документация
data/               # Игровые данные (YAML)
locale/             # Локализация
Mods/               # Моды пользователей
```

### Именование

- **Файлы**: `snake_case.py`
- **Классы**: `PascalCase`
- **Функции/переменные**: `snake_case`
- **Константы**: `UPPER_SNAKE_CASE`
- **Приватные**: `_leading_underscore`

## Релизы

### Версионирование

Мы используем [Semantic Versioning](https://semver.org/):

- **MAJOR**: Обратно несовместимые изменения
- **MINOR**: Новые функции с обратной совместимостью
- **PATCH**: Исправления ошибок

### Процесс релиза

1. Обновление версии в `pyproject.toml`
2. Создание changelog
3. Создание тега на GitHub
4. Публикация на PyPI (если применимо)

## Сообщество

### Каналы связи

- **GitHub Issues**: Сообщения об ошибках и запросы функций
- **GitHub Discussions**: Обсуждения и вопросы
- **Discord**: (если есть) Общение в реальном времени

### Кодекс поведения

Мы придерживаемся [Python Code of Conduct](https://www.python.org/psf/conduct/):

- Будьте уважительны и доброжелательны
- Помогайте новичкам
- Следуйте конструктивной критике
- Уважайте различия во мнениях

## Распространенные задачи

### Добавление новой расы

1. Добавьте данные в `data/races.yaml`
2. Напишите тесты в `tests/test_races.py`
3. Обновите документацию
4. Проверьте валидацию данных

### Добавление нового класса

1. Добавьте данные в `data/classes.yaml`
2. Реализуйте механику в `src/dnd_mud/character/class_.py`
3. Напишите тесты
4. Обновите документацию

### Исправление ошибки

1. Воспроизведите ошибку в тесте
2. Найдите и исправьте причину
3. Убедитесь, что тест проходит
4. Проверьте, что ничего не сломалось

### Улучшение документации

1. Найдите устаревшую информацию
2. Обновите документацию
3. Проверьте ссылки и примеры
4. Убедитесь, что формат правильный

## Полезные ресурсы

### Документация

- [Python Documentation](https://docs.python.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Typer Documentation](https://typer.tiangolo.com/)

### Инструменты

- [Black](https://black.readthedocs.io/) - Форматирование кода
- [Ruff](https://github.com/charliermarsh/ruff) - Линтер
- [MyPy](https://mypy.readthedocs.io/) - Проверка типов
- [Pytest](https://docs.pytest.org/) - Тестирование

### D&D ресурсы

- [D&D 5e SRD](https://dnd.wizards.com/resources/systems-reference-document)
- [Open5e](https://open5e.com/)
- [D&D Beyond](https://www.dndbeyond.com/)

## Благодарности

Спасибо всем, кто вносит вклад в проект! Ваша помощь делает D&D Text MUD лучше.

### Особая благодарность

- Всем контрибьюторам, создавшим Issues и Pull Requests
- Тестировщикам, находящим ошибки
- Переводчикам, адаптирующим игру на другие языки
- Разработчикам модов, расширяющим функциональность

---

**Если у вас есть вопросы, не стесняйтесь спрашивать в GitHub Issues или Discussions!**
