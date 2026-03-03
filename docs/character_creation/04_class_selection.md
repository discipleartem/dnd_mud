# Подзадача 4: Выбор класса

## Цель
Выбор класса персонажа с учетом характеристик

## Требования
- Загрузка данных о классах из YAML файла
- Проверка требований к характеристикам
- Отображение доступных классов
- Выбор уровня (начальный уровень 1)
- Применение классовых особенностей
- Установка hit dice и HP

## Критерии выполнения
- Проверка соответствия характеристик
- Корректная загрузка данных классов
- Применение классовых бонусов
- Расчет начального здоровья

## Техническая реализация

### Компоненты
- **ClassDataLoader** - загрузка из YAML
- **ClassSelector** - интерфейс выбора
- **ClassFeatureApplier** - применение особенностей

### Структура данных YAML
```yaml
classes:
  fighter:
    name: "Воин"
    description: "..."
    hit_dice: "d10"
    primary_ability: "strength"
    saving_throws: ["strength", "constitution"]
    armor_proficiencies: ["all_armor", "shields"]
    weapon_proficiencies: ["simple", "martial"]
    features:
      - name: "Fighting Style"
        level: 1
      - name: "Second Wind"
        level: 1
```

### Расчет здоровья (HP)
```python
def calculate_hit_points(level: int, hit_dice: str, con_mod: int) -> int:
    """Расчет очков здоровья"""
    dice_max = int(hit_dice[1:])  # d10 -> 10
    hp = dice_max + con_mod  # Первый уровень
    if level > 1:
        hp += (level - 1) * (dice_max // 2 + 1 + con_mod)
    return hp
```

### Алгоритм
1. Загрузка данных из classes.yaml
2. Проверка требований к характеристикам
3. Отображение доступных классов
4. Выбор класса пользователем
5. Применение классовых особенностей
6. Расчет HP и других параметров
7. Сохранение данных класса

### Интеграция с архитектурой
```python
class ClassSelectionService:
    def __init__(self, class_loader: ClassDataLoader, abilities: AbilityScores):
        self.class_loader = class_loader
        self.abilities = abilities
    
    async def select_class(self) -> ClassData:
        # Реализация выбора класса
        pass
```

### Тестирование
- Тесты загрузки YAML данных классов
- Тесты проверки требований к характеристикам
- Тесты расчета HP
- Тесты применения классовых особенностей
