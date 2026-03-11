# Руководство разработчика

## 🛠️ Разработка D&D Text MUD

Это руководство для разработчиков, работающих над проектом D&D Text MUD.

---

## 🚀 Настройка окружения

### Требования
- **Python 3.12+**
- **Git**
- **Редактор кода** (VS Code, PyCharm, etc.)

### Установка
```bash
# Клонирование
git clone https://github.com/discipleartem/dnd_mud.git
cd dnd_mud

# Виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Разработка с зависимостями
pip install -e ".[dev]"

# Pre-commit хуки
pre-commit install
```

---

## 📁 Структура проекта

```
dnd_mud/
├── src/                    # Исходный код
│   ├── entities/          # Бизнес-сущности
│   ├── use_cases/         # Сценарии использования
│   ├── interfaces/        # Интерфейсы
│   ├── adapters/          # Реализации
│   ├── dtos/              # DTO
│   └── console/           # Консольный UI
├── data/                   # Игровые данные (YAML)
├── tests/                  # Тесты
├── docs/                   # Документация
└── scripts/               # Вспомогательные скрипты
```

---

## 🎯 Принципы разработки

### Clean Architecture
- **Entities** - бизнес-логика без зависимостей
- **Use Cases** - прикладные сценарии
- **Interfaces** - абстракции
- **Adapters** - реализации внешних зависимостей

### Качество кода
- **Type hints** везде
- **Docstrings** (Google style)
- **Tests** для каждого модуля
- **Black** форматирование
- **Ruff** линтинг
- **MyPy** проверка типов

---

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
pytest

# С покрытием
pytest --cov=src --cov-report=html

# Конкретный модуль
pytest tests/test_character_creation.py

# По маркерам
pytest -m unit
pytest -m integration
```

### Структура тестов
```
tests/
├── unit/                   # Юнит-тесты
│   ├── test_entities.py
│   ├── test_services.py
│   └── test_utilities.py
├── integration/            # Интеграционные тесты
│   ├── test_character_creation_flow.py
│   └── test_combat_system.py
└── e2e/                    # End-to-end тесты
    └── test_full_gameplay.py
```

### Написание тестов
```python
import pytest
from src.entities.character import Character

class TestCharacter:
    def test_character_creation(self):
        character = Character(name="Test")
        assert character.name == "Test"
        assert character.level == 1
    
    @pytest.mark.parametrize("level,expected", [
        (1, 100), (2, 200), (3, 400)
    ])
    def test_experience_required(self, level, expected):
        character = Character(level=level)
        assert character.experience_required == expected
```

---

## 📋 Стиль кода

### Black форматирование
```bash
# Форматирование
black src/ tests/

# Проверка
black --check src/ tests/
```

### Ruff линтинг
```bash
# Проверка
ruff check src/ tests/

# Исправление
ruff check --fix src/ tests/
```

### MyPy проверка типов
```bash
# Проверка
mypy src/

# Строгий режим
mypy --strict src/
```

---

## 🔄 CI/CD

### GitHub Actions
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov=src
      - name: Check code quality
        run: |
          black --check src/ tests/
          ruff check src/ tests/
          mypy src/
```

### Pre-commit хуки
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
```

---

## 📦 Сборка и публикация

### PyPI публикация
```bash
# Сборка
python -m build

# Публикация (test)
python -m twine upload --repository testpypi dist/*

# Публикация (production)
python -m twine upload dist/*
```

### Версионирование
```toml
# pyproject.toml
[project]
name = "dnd-text-mud"
version = "0.1.0"
```

---

## 🐛 Отладка

### Логирование
```python
import logging

logger = logging.getLogger(__name__)

class CharacterService:
    def create_character(self, data: CharacterDTO) -> Character:
        logger.info(f"Creating character: {data.name}")
        try:
            character = Character.from_dto(data)
            logger.debug(f"Character created: {character}")
            return character
        except Exception as e:
            logger.error(f"Failed to create character: {e}")
            raise
```

### Отладка в VS Code
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug DND MUD",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        }
    ]
}
```

---

## 📊 Мониторинг

### Метрики
- Покрытие кода
- Время выполнения тестов
- Количество багов
- Производительность

### Инструменты
- **Coverage.py** - покрытие кода
- **pytest-benchmark** - производительность
- **pytest-xdist** - параллельные тесты

---

## 🔧 Инструменты разработчика

### VS Code расширения
- Python
- Pylance
- Black Formatter
- Ruff
- GitLens

### Полезные скрипты
```bash
# scripts/dev.sh
#!/bin/bash
# Полная проверка качества кода
echo "Running black..."
black --check src/ tests/

echo "Running ruff..."
ruff check src/ tests/

echo "Running mypy..."
mypy src/

echo "Running tests..."
pytest --cov=src

echo "All checks completed!"
```

---

## 🤝 Вклад в проект

### Process
1. Fork репозитория
2. Создать feature branch
3. Написать код и тесты
4. Проверить качество кода
5. Создать Pull Request
6. Дождаться ревью

### Guidelines
- Следуйте существующему стилю кода
- Добавляйте тесты для новой функциональности
- Обновляйте документацию
- Используйте понятные сообщения коммитов

### Commit messages
```
feat: add character creation service
fix: resolve race selection bug
docs: update API documentation
test: add combat system tests
refactor: simplify ability calculation
```

---

## 📚 Ресурсы

### Документация
- [Python typing](https://docs.python.org/3/library/typing.html)
- [pytest docs](https://docs.pytest.org/)
- [Black documentation](https://black.readthedocs.io/)
- [Ruff docs](https://beta.ruff.rs/)

### Сообщество
- [Python Discord](https://discord.gg/python)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/python)
- [Reddit r/Python](https://reddit.com/r/python)

---

## 🚨 Частые проблемы

### Import ошибки
```python
# ❌ Неправильно
from character import Character

# ✅ Правильно
from src.entities.character import Character
```

### Type ошибки
```python
# ❌ Неправильно
def process_data(data):
    return data.upper()

# ✅ Правильно
def process_data(data: str) -> str:
    return data.upper()
```

### Test ошибки
```python
# ❌ Неправильно
def test_something():
    # Тест без проверок
    pass

# ✅ Правильно
def test_something():
    result = some_function()
    assert result is not None
```

---

*Счастливой разработки!*