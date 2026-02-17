# Принципы Программирования в DnD MUD

## SOLID Principles

### S - Single Responsibility Principle (Принцип единственной ответственности)

> Каждый класс должен иметь только одну причину для изменения.

**Пример в проекте:**

```python
# ✅ Хорошо - каждый класс отвечает за свою задачу
class Dice:                    # Только броски кубиков
    def roll(self) -> DiceResult: pass

class Character:                # Только данные персонажа
    def __init__(self, name: str): pass

class CharacterRepository:       # Только сохранение/загрузка
    def save(self, character: Character): pass

# ❌ Плохо - смешение ответственности
class CharacterManager:
    def roll_dice(self): pass           # Не относится к управлению персонажем
    def save_to_database(self): pass   # Не относится к управлению персонажем
    def calculate_hp(self): pass        # Относится, но должно быть в Character
```

### O - Open/Closed Principle (Принцип открытости/закрытости)

> Программные сущности должны быть открыты для расширения, но закрыты для изменения.

**Пример в проекте:**

```python
# ✅ Хорошо - легко добавить новые типы кубиков
class DiceType(Enum):
    D4 = "d4"
    D6 = "d6"
    D8 = "d8"
    D20 = "d20"
    # Можно добавить D100, D12 и т.д. без изменения кода

class Dice:
    def __init__(self, dice_type: DiceType):
        self.sides = self._get_sides(dice_type)
    
    def _get_sides(self, dice_type: DiceType) -> int:
        mapping = {
            DiceType.D4: 4,
            DiceType.D6: 6,
            DiceType.D8: 8,
            DiceType.D20: 20,
        }
        return mapping[dice_type]
```

### L - Liskov Substitution Principle (Принцип подстановки Барбары Лисков)

> Объекты в программе должны быть заменяемы на экземпляры их подтипов без изменения правильности программы.

**Пример в проекте:**

```python
# ✅ Хорошо - подтипы можно заменять
class CharacterRepository(ABC):
    @abstractmethod
    def save(self, character: Character) -> Character: pass
    
    @abstractmethod
    def load(self, name: str) -> Optional[Character]: pass

class YamlCharacterRepository(CharacterRepository):
    def save(self, character: Character) -> Character:
        # Реализация для YAML
        pass
    
    def load(self, name: str) -> Optional[Character]:
        # Реализация для YAML
        pass

class JsonCharacterRepository(CharacterRepository):
    def save(self, character: Character) -> Character:
        # Реализация для JSON
        pass
    
    def load(self, name: str) -> Optional[Character]:
        # Реализация для JSON
        pass

# Можно использовать любую реализацию
repo: CharacterRepository = YamlCharacterRepository()  # или JsonCharacterRepository()
```

### I - Interface Segregation Principle (Принцип разделения интерфейса)

> Клиенты не должны быть вынуждены зависеть от методов, которые они не используют.

**Пример в проекте:**

```python
# ✅ Хорошо - узкоспециализированные интерфейсы
class CharacterSaver(ABC):
    @abstractmethod
    def save(self, character: Character) -> Character: pass

class CharacterLoader(ABC):
    @abstractmethod
    def load(self, name: str) -> Optional[Character]: pass

class CharacterLister(ABC):
    @abstractmethod
    def list_characters(self) -> List[str]: pass

# ❌ Плохо - один большой интерфейс
class CharacterRepository(ABC):
    @abstractmethod
    def save(self, character: Character) -> Character: pass
    
    @abstractmethod
    def load(self, name: str) -> Optional[Character]: pass
    
    @abstractmethod
    def list_characters(self) -> List[str]: pass
    
    @abstractmethod
    def delete(self, name: str) -> bool: pass
    
    @abstractmethod
    def backup(self) -> str: pass  # Не всегда нужно
```

### D - Dependency Inversion Principle (Принцип инверсии зависимостей)

> Модули верхних уровней не должны зависеть от модулей нижних уровней. Оба должны зависеть от абстракций.

**Пример в проекте:**

```python
# ✅ Хорошо - зависимость от абстракции
class CreateCharacterUseCase:
    def __init__(self, character_repo: CharacterRepository):  # Абстракция
        self.character_repo = character_repo
    
    def execute(self, request: CreateCharacterRequest) -> Character:
        character = CharacterFactory.create(request)
        return self.character_repo.save(character)

# Можно передать любую реализацию
use_case = CreateCharacterUseCase(YamlCharacterRepository())
use_case = CreateCharacterUseCase(JsonCharacterRepository())
use_case = CreateCharacterUseCase(DatabaseCharacterRepository())

# ❌ Плохо - зависимость от конкретной реализации
class CreateCharacterUseCase:
    def __init__(self):
        self.character_repo = YamlCharacterRepository()  # Конкретная реализация
```

## DRY Principle (Don't Repeat Yourself)

> Не повторяйте себя - каждая часть знания должна иметь единственное представление в системе.

**Пример в проекте:**

```python
# ✅ Хорошо - вынесение общей логики
class AttributeCalculator:
    @staticmethod
    def get_modifier(value: int) -> int:
        """Единый метод расчета модификатора."""
        return (value - 10) // 2

class Character:
    def get_strength_modifier(self) -> int:
        return AttributeCalculator.get_modifier(self.strength.value)
    
    def get_dexterity_modifier(self) -> int:
        return AttributeCalculator.get_modifier(self.dexterity.value)

# ❌ Плохо - дублирование логики
class Character:
    def get_strength_modifier(self) -> int:
        return (self.strength.value - 10) // 2
    
    def get_dexterity_modifier(self) -> int:
        return (self.dexterity.value - 10) // 2  # Дублирование!
```

## KISS Principle (Keep It Simple, Stupid)

> Простота лучше сложности.

**Пример в проекте:**

```python
# ✅ Хорошо - просто и понятно
def roll_dice(sides: int) -> int:
    """Бросок кубика с указанным количеством граней."""
    return random.randint(1, sides)

# ❌ Плохо - избыточная сложность
def roll_dice(sides: int, 
              use_quantum_random: bool = False,
              apply_entropy_correction: bool = False,
              simulate_fairness: bool = True) -> int:
    """Слишком сложный бросок кубика."""
    if use_quantum_random:
        # Квантовый генератор случайных чисел
        pass
    if apply_entropy_correction:
        # Коррекция энтропии
        pass
    return random.randint(1, sides)
```

## YAGNI Principle (You Aren't Gonna Need It)

> Не создавайте функциональность до тех пор, пока она действительно не понадобится.

**Пример в проекте:**

```python
# ✅ Хорошо - только то, что нужно сейчас
class Dice:
    def roll(self) -> int:
        return random.randint(1, self.sides)

# ❌ Плохо - избыточная функциональность
class Dice:
    def roll(self) -> int:
        return random.randint(1, self.sides)
    
    def roll_with_quantum_entropy(self) -> int:  # Не нужно сейчас
        pass
    
    def roll_with_fairness_simulation(self) -> int:  # Не нужно сейчас
        pass
    
    def roll_with_custom_distribution(self, distribution) -> int:  # Не нужно сейчас
        pass
```

## Принципы Чистой Архитектуры

### Dependency Rule

> Зависимости могут направляться только внутрь.

```
Infrastructure → Adapters → Application → Domain
```

**Пример в проекте:**

```python
# ✅ Правильно - зависимость от абстракции
class CreateCharacterUseCase:
    def __init__(self, repo: CharacterRepository):  # Интерфейс из Domain
        self.repo = repo

# ❌ Неправильно - зависимость от реализации
class CreateCharacterUseCase:
    def __init__(self):
        self.repo = YamlCharacterRepository()  # Конкретная реализация
```

### Entities Independence

> Сущности Domain слоя не должны зависеть от внешних систем.

```python
# ✅ Правильно - чистая бизнес-логика
class Character:
    def get_ac(self) -> int:
        """Расчет Armor Class по правилам D&D."""
        base_ac = 10 + self.get_dexterity_modifier()
        if self.armor:
            base_ac = max(base_ac, self.armor.ac)
        return base_ac

# ❌ Неправильно - зависимость от YAML
class Character:
    def get_ac(self) -> int:
        # Загрузка правил из YAML - нарушение!
        with open('rules/ac_rules.yaml') as f:
            rules = yaml.load(f)
        return rules['base_ac'] + self.get_dexterity_modifier()
```

## Паттерны проектирования в проекте

### Factory Pattern

```python
class CharacterFactory:
    @staticmethod
    def create(name: str, race_key: str, class_key: str) -> Character:
        race = RaceFactory.create_race(race_key)
        character_class = ClassFactory.create_class(class_key)
        return Character(name=name, race=race, character_class=character_class)
```

### Repository Pattern

```python
class CharacterRepository(ABC):
    @abstractmethod
    def save(self, character: Character) -> Character: pass
    
    @abstractmethod
    def load(self, name: str) -> Optional[Character]: pass
```

### Strategy Pattern

```python
class DiceRollStrategy(ABC):
    @abstractmethod
    def roll(self, dice: Dice) -> DiceResult: pass

class NormalRollStrategy(DiceRollStrategy):
    def roll(self, dice: Dice) -> DiceResult:
        value = random.randint(1, dice.sides)
        return DiceResult(value=value, dice_type=dice.dice_type)

class AdvantageRollStrategy(DiceRollStrategy):
    def roll(self, dice: Dice) -> DiceResult:
        roll1 = random.randint(1, dice.sides)
        roll2 = random.randint(1, dice.sides)
        value = max(roll1, roll2)
        return DiceResult(value=value, rolls=[roll1, roll2])
```

## Рекомендации по коду

### Именование

```python
# ✅ Хорошо - понятные имена
class Character:
    def get_armor_class(self) -> int: pass
    def apply_damage(self, damage: int) -> None: pass

# ❌ Плохо - непонятные имена
class Char:
    def get_ac(self) -> int: pass
    def dmg(self, x: int) -> None: pass
```

### Обработка ошибок

```python
# ✅ Хорошо - конкретные исключения
class InvalidCharacterError(Exception):
    """Ошибка валидации персонажа."""

def create_character(name: str, race: str) -> Character:
    if not name or len(name.strip()) == 0:
        raise InvalidCharacterError("Имя персонажа не может быть пустым")
    # ...

# ❌ Плохо - общие исключения
def create_character(name: str, race: str) -> Character:
    if not name:
        raise Exception("Ошибка")  # Непонятно какая ошибка
```

### Документация

```python
# ✅ Хорошо - подробная документация
def calculate_saving_throw(ability_score: int, proficiency_bonus: int, is_proficient: bool) -> int:
    """Рассчитывает модификатор спасброска.
    
    Args:
        ability_score: Значение характеристики (например, 14 для Strength)
        proficiency_bonus: Бонус мастерства персонажа
        is_proficient: Обладает ли персонаж мастерством в этом спасброске
        
    Returns:
        Модификатор спасброска
        
    Example:
        >>> calculate_saving_throw(14, 2, True)
        6  # (+2 от модификатора +2 от мастерства +2 от proficiency)
    """
    modifier = (ability_score - 10) // 2
    if is_proficient:
        modifier += proficiency_bonus
    return modifier
```

Эти принципы помогают создавать поддерживаемый, тестируемый и масштабируемый код в проекте DnD MUD.
