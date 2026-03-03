# Подзадача 9: Выбор Снаряжения

## Цель
Финализация стартового оборудования персонажа

## Требования
- Базовое снаряжение от класса и предыстории
- Возможность выбора из вариантов
- Расчет стартовых денег (gold)
- Учет веса и переносимости
- Организация инвентаря

## Категории снаряжения
### Оружие (Weapons)
- Простое оружие (Simple)
- Воинское оружие (Martial)
- Дистанционное оружие (Ranged)

### Доспехи (Armor)
- Легкие доспехи (Light)
- Средние доспехи (Medium)
- Тяжелые доспехи (Heavy)
- Щиты (Shields)

### Инструменты (Tools)
- Музыкальные инструменты
- Ремесленные инструменты
- Игровые наборы

### Расходуемые предметы (Consumables)
- Зелья
- Свитки
- Еда и питье

## Критерии выполнения
- Корректное применение стартового комплекта
- Расчет и распределение денег
- Проверка веса оборудования
- Формирование инвентаря

## Техническая реализация

### Компоненты
- **EquipmentManager** - управление снаряжением
- **EquipmentSelector** - интерфейс выбора
- **InventoryCalculator** - расчет веса и стоимости

### Расчет переносимости
```python
def calculate_carry_capacity(strength_score: int) -> int:
    """Расчет переносимости в фунтах"""
    return strength_score * 15

def calculate_encumbrance(weight: float, capacity: int) -> str:
    """Определение степени нагрузки"""
    ratio = weight / capacity
    if ratio <= 1/3:
        return "light"
    elif ratio <= 2/3:
        return "medium"
    else:
        return "heavy"
```

### Структура данных
```python
@dataclass
class Equipment:
    name: str
    name_ru: str
    category: str
    cost: Dict[str, float]  # {"gp": 10.5, "sp": 0}
    weight: float
    description: str
    properties: List[str] = field(default_factory=list)
```

### Алгоритм
1. Загрузка стартового комплекта от класса
2. Добавление оборудования от предыстории
3. Расчет стартовых денег
4. Предложение вариантов выбора (если есть)
5. Интерактивный выбор дополнительного снаряжения
6. Расчет общего веса
7. Проверка переносимости
8. Формирование финального инвентаря
9. Сохранение данных оборудования

### Стартовые комплекты по классам
- **Fighter**: Доспехи, оружие, щит
- **Wizard**: Книга заклинаний, компоненты, кинжал
- **Cleric**: Символ веры, доспехи, оружие
- **Rogue**: Легкие доспехи, оружие, воровские инструменты

### Интеграция с архитектурой
```python
class EquipmentSelectionService:
    def __init__(self, class_data: ClassData, background_data: BackgroundData,
                 abilities: AbilityScores):
        self.class_data = class_data
        self.background_data = background_data
        self.abilities = abilities
    
    async def select_equipment(self) -> Inventory:
        # Реализация выбора снаряжения
        pass
```

### Тестирование
- Тесты загрузки стартовых комплектов
- Тесты расчета веса и переносимости
- Тесты выбора вариантов снаряжения
- Тесты формирования инвентаря
