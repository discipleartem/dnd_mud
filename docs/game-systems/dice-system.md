# Система бросков кубиков D&D MUD

## Обзор

Система бросков кубиков реализует Core механику D&D для генерации случайных значений с поддержкой всех основных правил игры.

## Архитектура

### Применяемые паттерны

- **Factory (Фабрика)** — `DiceRoll` создает различные типы бросков
- **Strategy (Стратегия)** — разные модификаторы бросков (advantage/disadvantage)
- **Value Object (Объект-значение)** — `DiceResult` как неизменяемый результат броска
- **Repository (Хранилище)** — конфигурация кубиков из YAML

### Применяемые принципы

- **Single Responsibility** — каждый класс отвечает за одну вещь
- **Open/Closed** — легко добавлять новые типы кубиков и модификаторы
- **Dependency Inversion** — зависимость от абстракций, а не реализаций

## Основные классы

### DiceConfig

Конфигурация типа кубика из YAML:

```python
@dataclass(frozen=True)
class DiceConfig:
    sides: int           # Количество граней
    name: str           # Название (d20, d6 и т.д.)
    description: str    # Описание
```

### DiceResult

Результат броска (Value Object):

```python
@dataclass
class DiceResult:
    value: int                    # Значение на кубике
    dice_type: str               # Тип кубика
    rolls: List[int]             # Все броски (для advantage/disadvantage)
    modifier_type: RollModifierType
    special_result: SpecialResultType
    modifier: int                # Модификатор к броску
    
    @property
    def total(self) -> int:       # Итоговое значение с модификатором
    @property
    def is_critical(self) -> bool # Проверка на критический результат
```

### Dice

Основной класс кубика:

```python
dice = Dice("d20")
result = dice.roll(modifier=5)  # Обычный бросок
result = dice.roll_with_modifier(RollModifierType.ADVANTAGE, modifier=3)
```

### DiceRoll

Фабрика для удобного создания бросков:

```python
# Простые броски
result = DiceRoll.roll("d20", 5)
result = DiceRoll.roll_with_advantage("d20", 3)
result = DiceRoll.roll_with_disadvantage("d20", 2)

# Множественные броски
results = DiceRoll.roll_multiple("d6", 3, 1)  # 3d6+1

# Пул кубиков
results = DiceRoll.roll_dice_pool(["d6", "d8", "d4"])
```

## Удобные функции

Для частых операций есть готовые функции:

```python
from src.core.mechanics.dice import roll_d20, roll_d20_advantage, roll_damage

# Атака
attack_roll = roll_d20(5)  # d20+5
attack_roll = roll_d20_advantage(3)  # d20+3 с преимуществом

# Урон
damage = roll_damage("d6", 2, 4)  # 2d6+4
damage = roll_damage("d8", 1)  # 1d8
```

## Модификаторы бросков

### Advantage (Преимущество)

Бросаем два кубика, берем лучший результат:

```python
result = roll_d20_advantage(2)
# rolls: [5, 18], value: 18, total: 20
```

### Disadvantage (Помеха)

Бросаем два кубика, берем худший результат:

```python
result = roll_d20_disadvantage(2)
# rolls: [5, 18], value: 5, total: 7
```

### Triple Advantage/Disadvantage

Тройные версии модификаторов:

```python
dice = Dice("d20")
result = dice.roll_with_modifier(RollModifierType.TRIPLE_ADVANTAGE)
result = dice.roll_with_modifier(RollModifierType.TRIPLE_DISADVANTAGE)
```

## Критические результаты

Для d20 автоматически определяются критические результаты:

- **20** — критический успех (`critical_success`)
- **1** — критический провал (`critical_failure`)

**Примечание:** Конкретные эффекты критических результатов (удвоенный урон, автоматические успехи/провалы) определяются в игровых системах (боевая система, система испытаний), а не в core механике кубиков.

```python
result = roll_d20()
if result.is_critical_success:
    print("Критический успех! Удвоенный урон!")
elif result.is_critical_failure:
    print("Критический провал! Автоматический промах!")
```

## Валидация

Система включает валидацию параметров:

```python
from src.core.mechanics.dice import DiceValidator

# Проверка типа кубика
DiceValidator.validate_dice_type("d20")  # True
DiceValidator.validate_dice_type("d7")   # False

# Проверка модификатора
DiceValidator.validate_modifier(5)      # True
DiceValidator.validate_modifier(2000)   # False

# Проверка количества кубиков
DiceValidator.validate_dice_count(3)     # True
DiceValidator.validate_dice_count(0)     # False
```

## Конфигурация

Типы кубиков и правила настраиваются через YAML:

```yaml
# data/yaml/dice/core_dice.yaml
dice_types:
  d20:
    sides: 20
    name: "d20"
    description: "Двадцатигранный кубик"

roll_modifiers:
  advantage:
    name: "advantage"
    description: "Преимущество - бросаем дважды, берем лучший"
    type: "best_of"
    rolls: 2

validation_rules:
  max_dice_count: 100
  max_sides: 1000
  min_sides: 2
  max_modifier: 1000
  min_modifier: -1000
```

**Примечание:** Информация о стандартных бросках D&D (атаки, испытания, урон) вынесена в отдельные системы и не входит в core механику кубиков.

## Примеры использования

### Сценарий боя

```python
from src.core.mechanics.dice import roll_d20_advantage, roll_damage

# Атака с преимуществом
attack_roll = roll_d20_advantage(5)  # +5 к атаке

if attack_roll.is_critical_success:
    # Критический успех - двойной урон
    damage = roll_damage("d8", 2, 3) * 2
elif attack_roll.is_critical_failure:
    # Критический провал - нулевой урон
    damage = 0
else:
    # Обычный урон
    damage = roll_damage("d8", 1, 3)

print(f"Атака: {attack_roll.total}, Урон: {damage}")
```

### Испытание характеристики

```python
from src.core.mechanics.dice import roll_d20_disadvantage

# Испытание Ловкости с помехой
save_roll = roll_d20_disadvantage(2)  # +2 к Ловкости
dc = 15  # Сложность испытания

success = save_roll.total >= dc

if save_roll.is_critical_success:
    success = True  # Автоматический успех
elif save_roll.is_critical_failure:
    success = False  # Автоматический провал

print(f"Испытание: {save_roll.total} vs DC {dc} - {'Успех' if success else 'Провал'}")
```

### Генерация характеристик

```python
from src.core.mechanics.dice import DiceRoll, roll_damage

# Метод 4d6, отбрасываем наименьший
def roll_attribute():
    dice = Dice("d6")
    rolls = [dice.roll().value for _ in range(4)]
    rolls.sort()
    return sum(rolls[1:])  # Отбрасываем наименьший

# Генерируем 6 характеристик
attributes = [roll_attribute() for _ in range(6)]
print(f"Характеристики: {attributes}")
```

## Расширение системы

### Добавление нового типа кубика

1. Добавить в YAML конфигурацию:

```yaml
dice_types:
  d3:
    sides: 3
    name: "d3"
    description: "Трехгранный кубик"
```

2. Использовать:

```python
result = DiceRoll.roll("d3")
```

### Добавление нового модификатора

1. Добавить в YAML:

```yaml
roll_modifiers:
  elven_accuracy:
    name: "elven_accuracy"
    description: "Эльфийская точность - лучший из трех"
    type: "best_of"
    rolls: 3
```

2. Добавить в Enum:

```python
class RollModifierType(Enum):
    ELVEN_ACCURACY = "elven_accuracy"
    # ...
```

3. Использовать:

```python
result = dice.roll_with_modifier(RollModifierType.ELVEN_ACCURACY)
```

## Тестирование

Система покрыта тестами в `tests/test_dice.py`:

- Базовые броски кубиков
- Модификаторы (advantage/disadvantage)
- Критические результаты
- Валидация параметров
- Фабричные методы
- Интеграционные сценарии

Запуск тестов:

```bash
python -m unittest tests.test_dice -v
```

## Производительность

Система использует кэширование конфигураций для минимизации загрузки YAML файлов. Все операции выполняются за O(1) кроме множественных бросков, которые выполняются за O(n), где n - количество бросков.
