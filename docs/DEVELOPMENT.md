# Руководство по разработке D&D MUD

## 🚀 Начало работы

### Требования

- Python 3.12+
- Git
- Виртуальное окружение (рекомендуется)

### Настройка окружения

```bash
# 1. Клонирование репозитория
git clone <repository-url>
cd dnd_mud

# 2. Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

# 3. Установка зависимостей
pip install -e .

# 4. Установка зависимостей для разработки
pip install -e ".[dev]"

# 5. Настройка pre-commit hooks (опционально)
pre-commit install
```

## 🏗️ Структура проекта

Подробная информация в [ARCHITECTURE.md](ARCHITECTURE.md)

### Ключевые директории

- `src/` - основной исходный код
- `tests/` - тесты
- `data/` - игровые данные (YAML)
- `docs/` - документация
- `localization/` - файлы локализации

## 🧪 Разработка и тестирование

### Запуск приложения

```bash
# Активировать окружение
source .venv/bin/activate

# Запуск
python main.py
# или через скрипт
dnd-mud
```

### Тестирование

```bash
# Запустить все тесты
pytest

# С покрытием кода
pytest --cov=src --cov-report=html

# Конкретный тест
pytest tests/test_race_loader.py

# С выводом
pytest -v

# Только быстрые тесты
pytest -m "not slow"
```

### Качество кода

```bash
# Форматирование
black src/ tests/

# Проверка стиля
flake8 src/ tests/

# Проверка типов
mypy src/

# Все проверки вместе
black src/ tests/ && flake8 src/ tests/ && mypy src/
```

## 📝 Стиль кода

### Python стандарты

Проект следует PEP 8 с дополнительными правилами:

```python
# ✅ Хорошо
from typing import Dict, List, Optional

class Character:
    """Класс персонажа D&D.
    
    Attributes:
        name: Имя персонажа
        race: Раса персонажа
        ability_scores: Характеристики
    """
    
    def __init__(self, name: str, race: Optional[Race] = None) -> None:
        self.name = name
        self.race = race
        self.ability_scores: Optional[AbilityScores] = None
    
    def get_total_ability_score(self, ability: str) -> int:
        """Рассчитать общую характеристику с учетом расовых бонусов.
        
        Args:
            ability: Название характеристики
            
        Returns:
            Общее значение характеристики
        """
        base_score = self.ability_scores.get_base_score(ability)
        racial_bonus = self.race.get_ability_bonus(ability) if self.race else 0
        return base_score + racial_bonus
```

### Правила именования

- **Классы:** `PascalCase` - `Character`, `RaceLoader`
- **Функции/методы:** `snake_case` - `get_race`, `load_from_yaml`
- **Переменные:** `snake_case` - `race_id`, `ability_scores`
- **Константы:** `UPPER_SNAKE_CASE` - `MAX_ABILITY_SCORE`
- **Файлы:** `snake_case.py` - `character.py`, `race_loader.py`

### Docstrings

Используем Google стиль на русском языке:

```python
def generate_ability_scores(race: Race, method: str = "standard") -> AbilityScores:
    """Генерирует характеристики персонажа.
    
    Args:
        race: Раса персонажа для применения бонусов
        method: Метод генерации (standard, point_buy, random)
        
    Returns:
        Объект сгенерированных характеристик
        
    Raises:
        ValueError: Если указан неподдерживаемый метод генерации
        
    Example:
        >>> human = Race.get_race("human")
        >>> scores = generate_ability_scores(human, "standard")
        >>> print(scores.strength)
        15
    """
```

## 🔧 Добавление нового функционала

### 1. Новая раса

```yaml
# data/races.yaml
races:
  dragonborn:
    name: "Драконорожденный"
    description: "Потомок драконов с драконьими силами"
    ability_bonuses:
      strength: 2
      charisma: 1
    ability_bonuses_description: "Сила +2, Харизма +1"
    size: "MEDIUM"
    speed: 30
    age:
      min: 15
      max: 80
    languages: ["common", "draconic"]
    features:
      - name: "Драконье наследие"
        description: "Вы можете дышать оружием"
        mechanics:
          type: "breath_weapon"
          damage_type: "fire"
          damage: "2d10"
```

```yaml
# localization/ru.yaml
character_creation:
  race:
    dragonborn: "Драконорожденный"
```

```python
# tests/test_new_race.py
def test_dragonborn_race():
    dragonborn = Race.get_race("dragonborn")
    assert dragonborn.name == "Драконорожденный"
    assert dragonborn.ability_bonuses == {"strength": 2, "charisma": 1}
    assert "draconic" in dragonborn.languages
```

### 2. Новая характеристика

```python
# src/ui/entities/abilities.py
@dataclass
class AbilityScores:
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    # Новая характеристика
    luck: int = 10  # Удача
    
    def get_modifier(self, ability: str) -> int:
        """Рассчитать модификатор характеристики."""
        score = getattr(self, ability, 10)
        return (score - 10) // 2
```

### 3. Новый метод генерации характеристик

```python
# src/ui/main_menu/ability_generation.py
class DicePoolStrategy(AbilityGenerationStrategy):
    """Стратегия генерации через пул костей."""
    
    def __init__(self, pool_size: int = 24):
        self.pool_size = pool_size
    
    def generate(self) -> Dict[str, int]:
        """Генерация через распределение пула очков."""
        scores = {}
        remaining_pool = self.pool_size
        
        abilities = ["strength", "dexterity", "constitution", 
                    "intelligence", "wisdom", "charisma"]
        
        for ability in abilities[:-1]:
            score = min(15, max(8, remaining_pool // (len(abilities) - len(scores))))
            scores[ability] = score
            remaining_pool -= score
        
        scores[abilities[-1]] = remaining_pool
        return scores

# Добавление в фабрику
def create_strategy(method: str) -> AbilityGenerationStrategy:
    strategies = {
        "standard": StandardArrayStrategy(),
        "point_buy": PointBuyStrategy(),
        "random": RandomGenerationStrategy(),
        "dice_pool": DicePoolStrategy(),  # Новая стратегия
    }
    return strategies.get(method, StandardArrayStrategy())
```

## 🌐 Локализация

### Добавление нового текста

```yaml
# localization/ru.yaml
new_feature:
  title: "Новая функция"
  description: "Описание новой функции"
  confirm: "Вы уверены?"
  success: "Функция успешно выполнена"
  
# localization/en.yaml
new_feature:
  title: "New Feature"
  description: "Description of new feature"
  confirm: "Are you sure?"
  success: "Feature completed successfully"
```

### Использование в коде

```python
from i18n import t

def new_feature():
    print(t('new_feature.title'))
    if input(t('new_feature.confirm')) == 'yes':
        # логика
        print(t('new_feature.success'))
```

## 🧪 Написание тестов

### Unit тесты

```python
# tests/test_character.py
import pytest
from src.ui.entities.character import Character
from src.ui.entities.race import Race

class TestCharacter:
    def test_character_creation(self):
        """Тест создания персонажа."""
        character = Character(name="Тест")
        assert character.name == "Тест"
        assert character.race is None
    
    def test_character_with_race(self):
        """Тест персонажа с расой."""
        human = Race.get_race("human")
        character = Character(name="Тест", race=human)
        assert character.race.name == "Человек"
    
    def test_ability_calculation(self):
        """Тест расчета характеристик."""
        # Arrange
        human = Race.get_race("human")
        character = Character(name="Тест", race=human)
        character.ability_scores = AbilityScores(strength=14)
        
        # Act
        total_strength = character.get_total_ability_score("strength")
        
        # Assert
        assert total_strength == 15  # 14 + 1 (расовый бонус)
```

### Integration тесты

```python
# tests/test_integration.py
def test_full_character_creation():
    """Тест полного процесса создания персонажа."""
    # Выбор расы
    race = Race.get_race("human")
    
    # Генерация характеристик
    scores = generate_ability_scores(race, "standard")
    
    # Создание персонажа
    character = Character(name="Интеграционный тест", race=race)
    character.ability_scores = scores
    
    # Проверки
    assert character.name == "Интеграционный тест"
    assert character.race.name == "Человек"
    assert character.ability_scores is not None
```

## 📦 Сборка и публикация

### Локальная сборка

```bash
# Сборка пакета
python -m build

# Проверка пакета
twine check dist/*
```

### Публикация (для администраторов)

```bash
# Установка инструментов
pip install build twine

# Сборка
python -m build

# Публикация в test PyPI
twine upload --repository testpypi dist/*

# Публикация в PyPI
twine upload dist/*
```

## 🐛 Отладка

### Логирование

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Начало выполнения функции")
    try:
        # логика
        logger.info("Функция выполнена успешно")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise
```

### Отладка в VS Code

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug D&D MUD",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

## 🔄 Git рабочий процесс

### Ветвление

```bash
# Создание новой ветки
git checkout -b feature/new-race

# Внесение изменений
git add .
git commit -m "feat: добавить драконорожденных"

# Push и PR
git push origin feature/new-race
# Создать Pull Request на GitHub
```

### Сообщения коммитов

Используем Conventional Commits:

```
feat: добавить новую функцию
fix: исправить ошибку в генерации характеристик
docs: обновить документацию
style: форматирование кода
refactor: рефакторинг загрузчика рас
test: добавить тесты для персонажа
chore: обновить зависимости
```

## 📋 Чек-лист перед PR

- [ ] Код отформатирован (`black`)
- [ ] Нет ошибок стиля (`flake8`)
- [ ] Типы проверены (`mypy`)
- [ ] Тесты проходят (`pytest`)
- [ ] Покрытие тестами не менее 80%
- [ ] Документация обновлена
- [ ] Локализация добавлена
- [ ] CHANGELOG.md обновлен
- [ ] Сообщение коммита соответствует стандарту

## 🚨 Частые проблемы

### Проблема: ImportError

**Решение:**
```bash
# Убедиться что активировано окружение
source .venv/bin/activate

# Переустановить пакет
pip install -e .
```

### Проблема: Тесты не находят модули

**Решение:**
```bash
# Установить PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Или использовать pytest с правильным путем
pytest --pyargs src
```

### Проблема: Локализация не работает

**Решение:**
1. Проверить наличие ключа в YAML файлах
2. Убедиться что файлы в UTF-8 кодировке
3. Проверить правильность иерархии ключей

## 📚 Полезные ресурсы

- [Python Documentation](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [MyPy Type Checking](https://mypy.readthedocs.io/)

---

**D&D MUD Development** - руководство для эффективной разработки
