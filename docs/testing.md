# Тестирование в D&D Text MUD

## 📋 Обзор

Документация описывает подход к тестированию проекта D&D Text MUD. Мы используем только **unit** и **integration** тесты с фокусом на простоту и минимально необходимый функционал.

## 🎯 Принципы тестирования

### Основные правила

- **Простота** — тесты должны быть понятными и лёгкими для чтения
- **Минимализм** — тестируем только необходимый функционал, без излишеств
- **Надёжность** — тесты должны быть стабильными и детерминированными
- **Быстрота** — unit тесты выполняются быстро, integration — медленнее
- **Изоляция** — unit тесты не зависят от внешних систем

### Типы тестов

#### Unit тесты
- **Цель:** Проверка отдельных функций и классов
- **Скорость:** Быстрые (< 0.1с)
- **Зависимости:** Моки, стабы
- **Пример:** Проверка расчёта урона, валидация данных

#### Integration тесты
- **Цель:** Проверка взаимодействия компонентов
- **Скорость:** Медленные (> 1с)
- **Зависимости:** Реальные компоненты, тестовая БД
- **Пример:** Проверка сохранения персонажа, загрузки модов

## 🏗️ Структура тестов

```
tests/
├── unit/                    # Unit тесты
│   ├── test_character.py      # Тесты системы персонажей
│   ├── test_combat.py        # Тесты боевой системы
│   ├── test_data.py          # Тесты управления данными
│   └── test_ui.py            # Тесты UI компонентов
├── integration/             # Integration тесты
│   ├── test_character_flow.py # Полный цикл создания персонажа
│   ├── test_combat_flow.py   # Полный бой
│   └── test_modding.py      # Загрузка модов
├── fixtures/               # Тестовые данные
│   ├── characters.yaml       # Тестовые персонажи
│   ├── items.yaml           # Тестовые предметы
│   └── spells.yaml         # Тестовые заклинания
└── conftest.py            # Общие фикстуры pytest
```

## 📝 Написание тестов

### Unit тесты

**Структура:**
```python
import pytest
from unittest.mock import Mock, patch

class TestCharacter:
    """Тесты класса Character."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.character = Character(name="Тестовый персонаж")
    
    def test_character_creation(self):
        """Тест создания персонажа."""
        assert self.character.name == "Тестовый персонаж"
        assert self.character.level == 1
        assert self.character.hp > 0
    
    def test_character_take_damage(self):
        """Тест получения урона."""
        initial_hp = self.character.hp
        damage = 10
        
        self.character.take_damage(damage)
        
        assert self.character.hp == initial_hp - damage
    
    @patch('dnd_mud.character.dice.roll')
    def test_character_attack_with_mock(self, mock_roll):
        """Тест атаки с моком."""
        mock_roll.return_value = 20
        
        damage = self.character.attack()
        
        mock_roll.assert_called_once()
        assert damage > 0
```

**Правила unit тестов:**
- Используем моки для внешних зависимостей
- Тестируем один сценарий на тест
- Проверяем результат и состояние
- Используем описательные имена тестов

### Integration тесты

**Структура:**
```python
import pytest
from dnd_mud.character import Character
from dnd_mud.data import DataLoader

class TestCharacterFlow:
    """Тесты полного цикла работы с персонажем."""
    
    def test_complete_character_creation(self):
        """Тест полного создания персонажа."""
        # Создание персонажа
        character = Character.create_new(
            name="Тестовый герой",
            race="human",
            class_name="warrior"
        )
        
        # Проверка базовых свойств
        assert character.name == "Тестовый герой"
        assert character.race.name == "human"
        assert character.class_.name == "warrior"
        
        # Проверка сохранения
        saved_data = character.save_to_dict()
        assert saved_data["name"] == "Тестовый герой"
        
        # Проверка загрузки
        loaded_character = Character.load_from_dict(saved_data)
        assert loaded_character.name == character.name
        assert loaded_character.race.name == character.race.name
```

**Правила integration тестов:**
- Используем реальные компоненты
- Тестируем полный пользовательский сценарий
- Проверяем взаимодействие между модулями
- Используем тестовые данные из fixtures

## 🔧 Фикстуры и утилиты

### conftest.py

```python
import pytest
import yaml
from pathlib import Path

@pytest.fixture
def sample_character_data():
    """Фикстура с тестовыми данными персонажа."""
    return {
        "name": "Тестовый персонаж",
        "race": "human",
        "class": "warrior",
        "level": 1,
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 15,
            "intelligence": 12,
            "wisdom": 13,
            "charisma": 10
        }
    }

@pytest.fixture
def temp_yaml_file(tmp_path, sample_character_data):
    """Фикстура для временного YAML файла."""
    yaml_file = tmp_path / "test_character.yaml"
    with open(yaml_file, 'w') as f:
        yaml.dump(sample_character_data, f)
    return yaml_file

@pytest.fixture
def mock_dice():
    """Мок для кубиков."""
    with patch('dnd_mud.core.dice.Dice') as mock_dice:
        mock_dice.return_value.roll.return_value = 10
        yield mock_dice
```

### Тестовые утилиты

```python
# tests/utils.py
from typing import Any, Dict

def assert_character_equivalence(char1: Any, char2: Any) -> None:
    """Проверяет эквивалентность персонажей."""
    assert char1.name == char2.name
    assert char1.race.name == char2.race.name
    assert char1.class_.name == char2.class_.name
    assert char1.level == char2.level

def create_test_character(**kwargs) -> Any:
    """Создаёт тестового персонажа с параметрами."""
    defaults = {
        "name": "Тестовый персонаж",
        "race": "human",
        "class_name": "warrior"
    }
    defaults.update(kwargs)
    return Character.create_new(**defaults)
```

## 🏃‍♂️ Запуск тестов

### Команды

```bash
# Все тесты
pytest

# Только unit тесты
pytest -m unit

# Только integration тесты
pytest -m integration

# Быстрые тесты (без медленных)
pytest -m "not slow"

# С покрытием кода
pytest --cov=dnd_mud --cov-report=html

# Детальный вывод
pytest -v

# Остановиться при первой ошибке
pytest -x
```

### Маркеры

Из `pyproject.toml`:
- `@pytest.mark.unit` — unit тесты
- `@pytest.mark.integration` — integration тесты  
- `@pytest.mark.slow` — медленные тесты

## 📊 Покрытие кода

### Цели

- **Общее покрытие:** > 80%
- **Unit тесты:** > 90%
- **Integration тесты:** > 70%

### Отчёты

```bash
# HTML отчёт
pytest --cov=dnd_mud --cov-report=html

# Терминальный отчёт
pytest --cov=dnd_mud --cov-report=term-missing

# Файл отчёта
pytest --cov=dnd_mud --cov-report=xml
```

## 🚨 Лучшие практики

### Unit тесты

1. **Изоляция** — не зависеть от БД, сети, файловой системы
2. **Моки** — использовать для внешних зависимостей
3. **Быстрота** — каждый тест < 0.1 секунды
4. **Один сценарий** — один тест = одна проверка
5. **Читаемость** — понятные имена и структура

### Integration тесты

1. **Реальные данные** — использовать тестовую БД, файлы
2. **Полные сценарии** — проверять пользовательские пути
3. **Очистка** — удалять временные данные после тестов
4. **Стабильность** — избегать случайных значений
5. **Документация** — описывать тестируемый сценарий

### Общие правила

1. **Имена тестов** — `test_что_делает_когда_условие`
2. **Arrange-Act-Assert** — подготовка, действие, проверка
3. **Константы** — выносить повторяющиеся значения
4. **FIXTURES** — использовать для повторяющейся настройки
5. **Ошибки** — тестировать и успешные, и ошибочные сценарии

## 🔍 Примеры тестов

### Unit тест для расчёта урона

```python
def test_calculate_damage_critical_hit(self):
    """Тест расчёта урона при критическом попадании."""
    character = Character(strength=16)
    weapon = Weapon(dice="1d8", bonus=3)
    
    # Мокируем бросок кубика
    with patch('dnd_mud.core.dice.Dice.roll') as mock_roll:
        mock_roll.return_value = 8  # Максимальное значение для 1d8
        
        damage = character.calculate_damage(weapon, critical=True)
        
        # Критический удар = двойной урон + бонус
        expected_damage = (8 + 3) * 2
        assert damage == expected_damage
```

### Integration тест для сохранения персонажа

```python
def test_save_and_load_character_flow(self, tmp_path):
    """Тест полного цикла сохранения и загрузки персонажа."""
    # Создаём персонажа
    character = create_test_character(name="Тестовый герой")
    
    # Сохраняем в файл
    save_file = tmp_path / "character.json"
    character.save_to_file(save_file)
    
    # Проверяем существование файла
    assert save_file.exists()
    
    # Загружаем из файла
    loaded_character = Character.load_from_file(save_file)
    
    # Проверяем эквивалентность
    assert_character_equivalence(character, loaded_character)
```

## 📝 Чек-лист для тестов

### Перед коммитом

- [ ] Все unit тесты проходят
- [ ] Все integration тесты проходят  
- [ ] Покрытие кода не ниже 80%
- [ ] Нет warnings в pytest
- [ ] Тесты изолированы (не зависят друг от друга)
- [ ] Используются правильные маркеры
- [ ] Имена тестов описательные

### При добавлении нового функционала

- [ ] Написан unit тест для основной логики
- [ ] Написан integration тест для полного сценария
- [ ] Добавлены тестовые данные в fixtures
- [ ] Обновлена документация
- [ ] Проверено покрытие кода

---

**Помните:** Хорошие тесты — это инвестиция в стабильность проекта. Лучше написать простой тест, чем не написать вообще.
