# Подзадача 5: Выбор Предыстории

## Цель
Выбор предыстории персонажа из доступных

## Требования
- Загрузка данных из data/backgrounds.yaml
- Проверка совместимости с классом/расой
- Предоставление навыков от предыстории
- Добавление особенностей и владений
- Установка стартового оборудования

## Критерии выполнения
- Корректная загрузка предысторий
- Применение бонусов к навыкам
- Добавление владений и языков
- Интеграция с классовыми особенностями

## Техническая реализация

### Компоненты
- **BackgroundDataLoader** - загрузка из YAML
- **BackgroundSelector** - интерфейс выбора
- **BackgroundFeatureApplier** - применение бонусов

### Структура данных YAML
```yaml
backgrounds:
  soldier:
    name: "Солдат"
    description: "..."
    skill_proficiencies: ["athletics", "intimidation"]
    tool_proficiencies: ["land_vehicles", "gaming_set"]
    equipment:
      - "chain_mail"
      - "longsword"
      - "dagger"
      - "shield"
    feature:
      name: "Military Rank"
      description: "..."
    languages: []
    personality_traits: ["..."]
    ideals: ["..."]
    bonds: ["..."]
    flaws: ["..."]
```

### Алгоритм
1. Загрузка данных из backgrounds.yaml
2. Фильтрация совместимых предысторий
3. Отображение доступных вариантов
4. Выбор предыстории пользователем
5. Применение бонусов к навыкам
6. Добавление владений и языков
7. Установка стартового оборудования
8. Сохранение данных предыстории

### Интеграция с архитектурой
```python
class BackgroundSelectionService:
    def __init__(self, background_loader: BackgroundDataLoader, 
                 class_data: ClassData, race_data: RaceData):
        self.background_loader = background_loader
        self.class_data = class_data
        self.race_data = race_data
    
    async def select_background(self) -> BackgroundData:
        # Реализация выбора предыстории
        pass
```

### Тестирование
- Тесты загрузки YAML данных предысторий
- Тесты проверки совместимости
- Тесты применения бонусов к навыкам
- Тесты добавления оборудования
