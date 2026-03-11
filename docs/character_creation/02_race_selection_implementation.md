# Реализация системы выбора расы

## Обзор

Система выбора расы для D&D MUD полностью реализована согласно требованиям. Система позволяет универсально создавать и выбирать любые расы на основе YAML файла с данными о расах.

## Архитектура

### Сущности (Entities)
- **RaceFeature** - особенности расы с механикой
- **Race** - основная раса D&D 5e
- **Subrace** - подраса с возможным наследованием бонусов
- **Character** - расширен для поддержки расовых данных

### Интерфейсы (Interfaces)
- **RaceDataLoader** - загрузка данных о расах
- **RaceRepository** - работа с данными рас

### Сервисы (Services)
- **YamlRaceDataLoader** - загрузка YAML данных
- **RaceSelectionService** - оркестрация выбора расы
- **RaceBonusApplierService** - применение расовых бонусов

### Адаптеры (Adapters)
- **YamlRaceRepository** - репозиторий на основе YAML
- **RaceSelectionAdapter** - консольный интерфейс выбора

## Примененные паттерны

1. **Entity** - Race, Subrace, RaceFeature
2. **Repository** - RaceRepository, YamlRaceRepository
3. **Service Layer** - RaceSelectionService, RaceBonusApplierService
4. **Adapter** - RaceSelectionAdapter
5. **Strategy** - YamlRaceDataLoader
6. **Template Method** - алгоритмы выбора и загрузки
7. **Value Object** - RaceFeature
8. **Dependency Injection** - внедрение зависимостей в сервисы

## Примененные принципы

1. **Single Responsibility** - каждый класс имеет одну зону ответственности
2. **Open/Closed** - система открыта для расширения новыми расами
3. **Liskov Substitution** - подрасы могут заменять базовые расы
4. **Interface Segregation** - узкоспециализированные интерфейсы
5. **Dependency Inversion** - зависимость от абстракций
6. **Validation First** - валидация данных при создании
7. **Explicit > Implicit** - явное определение всех полей
8. **Immutable Operations** - методы создают новые объекты

## Функциональность

### Загрузка данных
- Парсинг YAML файлов с расами
- Валидация структуры данных
- Обработка ошибок загрузки
- Поддержка подрас и особенностей

### Выбор расы
- Отображение доступных рас
- Выбор базовой расы или подрасы
- Валидация выбора пользователя
- Применение расы к персонажу

### Расовые бонусы
- Применение бонусов к характеристикам
- Поддержка наследования бонусов подрас
- Расчет максимальных значений характеристик
- Валидация финальных значений

### Консольный интерфейс
- Интерактивное меню выбора
- Подробная информация о расах
- Обработка пользовательского ввода
- Сообщения об ошибках

## Структура YAML

```yaml
races:
  race_id:
    name: "Название расы"
    description: "Описание расы"
    ability_bonuses:
      strength: 1
      dexterity: 1
    size: "medium"
    speed: 30
    languages: ["common", "racial"]
    allow_base_race_choice: true
    features:
      - name: "Особенность"
        description: "Описание особенности"
        mechanics:
          type: "bonus"
          value: 1
    subraces:
      subrace_id:
        name: "Название подрасы"
        description: "Описание подрасы"
        ability_bonuses:
          intelligence: 1
        inherit_base_abilities: true
        features: []
```

## Тестирование

### Unit тесты
- **test_race_data_loader_service.py** - 14 тестов
- **test_yaml_race_repository.py** - 17 тестов
- **test_race_selection_service.py** - 22 теста
- **test_race_bonus_applier_service.py** - 18 тестов
- **test_race_selection_adapter.py** - 16 тестов

### Интеграционные тесты
- **test_race_selection_integration.py** - 14 тестов

Всего: **101 тест** с полным покрытием функциональности.

## Использование

### Базовое использование
```python
from src.repositories.yaml_race_repository import YamlRaceRepository
from src.services.race_data_loader_service import YamlRaceDataLoader
from src.services.race_selection_service import RaceSelectionService

# Создание сервисов
loader = YamlRaceDataLoader()
repo = YamlRaceRepository("data/races.yaml", loader)
selection_service = RaceSelectionService(repo)

# Выбор расы
character = Character(name="Персонаж")
updated_character = selection_service.apply_race_to_character(
    character, "human", "base:Человек"
)
```

### Консольный интерфейс
```python
from src.console.race_selection_adapter import RaceSelectionAdapter

adapter = RaceSelectionAdapter(selection_service, bonus_applier)
character_with_race = adapter.select_race_for_character(character)
```

## Расширение системы

### Добавление новой расы
1. Добавить расу в YAML файл
2. Следовать структуре данных
3. Перезапустить приложение

### Добавление нового источника данных
1. Реализовать RaceDataLoader
2. Реализовать RaceRepository
3. Использовать через Dependency Injection

## Качество кода

- **Type hints** - полное использование аннотаций типов
- **Docstrings** - документация на русском языке
- **Logging** - детальное логирование операций
- **Error handling** - явная обработка всех ошибок
- **PEP 8** - соответствие стандартам кода

## Интеграция с персонажем

Система интегрирована с сущностью Character:
- `race_id` - ID выбранной расы
- `subrace_id` - ID выбранной подрасы
- `ability_scores` - характеристики с расовыми бонусами
- `with_race()` - метод для установки расы
- `with_ability_scores()` - метод для установки характеристик

## Следующие шаги

1. Интеграция с основным процессом создания персонажа
2. Добавление генерации характеристик
3. Создание адаптера для выбора характеристик
4. Тестирование полного процесса создания персонажа
