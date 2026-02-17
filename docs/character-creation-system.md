# Система создания персонажей D&D MUD

## Обзор

Система создания персонажей предоставляет полный функционал для генерации, настройки и сохранения персонажей в мире Dungeons & Dragons. Система поддерживает различные методы генерации характеристик, выбор расы и класса, а также сохранение персонажей в различных форматах.

## Архитектура

### Основные компоненты

1. **AttributeGenerator** - генератор характеристик с различными методами
2. **CharacterBuilder** - билдер для пошагового создания персонажа
3. **CharacterFactory** - фабрика для быстрого создания персонажей
4. **CharacterCreationMenu** - UI интерфейс создания персонажа
5. **CharacterManager** - менеджер сохранения и загрузки персонажей

### Применяемые паттерны

- **Factory (Фабрика)** - создание персонажей и характеристик
- **Builder (Строитель)** - пошаговое создание персонажа
- **Strategy (Стратегия)** - разные методы генерации характеристик
- **Repository (Хранилище)** - сохранение и загрузка персонажей
- **Singleton (Одиночка)** - единый менеджер персонажей

## Методы генерации характеристик

### 1. Стандартный набор (Standard Array)
- Значения: 15, 14, 13, 12, 10, 8
- Распределение: случайное
- Преимущества: сбалансированный персонаж

### 2. 4d6 drop lowest
- Метод: 4 кубика d6, отбрасываем наименьший
- Диапазон: 3-18 для каждой характеристики
- Преимущества: возможность получить высокие значения

### 3. Покупка очков (Point Buy)
- Очков: 27
- Диапазон: 8-15
- Стоимость: таблица стоимости D&D 5e
- Преимущества: полный контроль над характеристиками

## Использование

### Создание персонажа через UI

```python
from src.ui.menus.character_creation import CharacterCreationController
from src.ui.input_handler import input_handler
from src.ui.renderer import renderer

controller = CharacterCreationController(input_handler, renderer)
character = controller.create_character()
```

### Программное создание персонажа

```python
from src.core.mechanics.character_generation import CharacterBuilder

# Через билдер
builder = CharacterBuilder()
character = (builder
    .set_name("Арагорн")
    .set_level(5)
    .set_race("human")
    .set_class("fighter")
    .generate_attributes_standard_array()
    .build())

# Через фабрику
from src.core.mechanics.character_generation import CharacterFactory
character = CharacterFactory.create_random_character("Гэндальф", 10)
```

### Сохранение и загрузка

```python
from src.systems.character_manager import CharacterManager

manager = CharacterManager.get_instance()

# Сохранение
success = manager.save_character(character, "json")

# Загрузка
loaded_character = manager.load_character("character.json")

# Список персонажей
characters = manager.list_characters()
```

## Конфигурация

### Характеристики (data/yaml/attributes/core_attributes.yaml)

```yaml
base_attributes:
  strength:
    name: "strength"
    default_value: 10
    min_value: 1
    max_value: 20
    short_name: "STR"

generation_methods:
  standard_array:
    name: "Стандартный набор"
    description: "Стандартный набор (15, 14, 13, 12, 10, 8)"
    values: [15, 14, 13, 12, 10, 8]
```

## Валидация

Система включает валидацию:
- Диапазоны характеристик
- Стоимость очков в point buy
- Уровень персонажа
- Корректность расы и класса

## Тестирование

Запуск тестов:
```bash
python -m pytest tests/test_character_creation.py -v
```

## Расширение системы

### Добавление нового метода генерации

1. Добавить метод в `GenerationMethod` enum
2. Создать класс конфигурации
3. Реализовать метод в `AttributeGenerator`
4. Обновить YAML конфигурацию

### Добавление нового формата сохранения

1. Добавить методы в `CharacterRepository`
2. Обновить `save_character` и `load_character`
3. Добавить тесты

## Интеграция с главным меню

Система полностью интегрирована в главное меню:
- **Новая игра** - запускает создание персонажа
- **Загрузить игру** - показывает список сохраненных персонажей

## Будущие улучшения

1. Мультиязычность интерфейса создания
2. Визуальное представление персонажа
3. Расширенные опции кастомизации
4. Импорт/экспорт персонажей
5. Валидация правил D&D 5e
6. Предпросмотр персонажа перед сохранением
