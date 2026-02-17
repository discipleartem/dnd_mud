# Паттерны Проектирования в DnD MUD

## Обзор

В проекте DnD MUD используются различные паттерны проектирования для создания чистой, масштабируемой и поддерживаемой архитектуры. Паттерны применяются в соответствии с принципами Чистой Архитектуры и SOLID.

## Порождающие паттерны (Creational Patterns)

### Factory Pattern (Фабрика)

**Назначение:** Создание объектов без указания их конкретных классов.

**Где используется:**
- Создание персонажей разных рас и классов
- Генерация кубиков различных типов
- Создание предметов и монстров

**Пример в коде:**

```python
# src/domain/entities/race_factory.py
class RaceFactory:
    """Фабрика для создания рас из YAML конфигурации."""
    
    _races_cache: Dict[str, Race] = {}
    
    @classmethod
    def create_race(cls, race_key: str, subrace_key: Optional[str] = None) -> Race:
        """Создает объект расы по ключу."""
        cache_key = f"{race_key}_{subrace_key}" if subrace_key else race_key
        
        if cache_key in cls._races_cache:
            return cls._races_cache[cache_key]
        
        # Загрузка данных из YAML
        races_data = cls._load_races_data()
        race_data = races_data[race_key]
        
        # Создание объекта Race
        race = Race(
            name=race_key,
            bonuses=race_data.get('bonuses', {}),
            description=race_data.get('description', '')
        )
        
        # Кеширование
        cls._races_cache[cache_key] = race
        return race

# Использование
elf = RaceFactory.create_race('elf', 'high_elf')
human = RaceFactory.create_race('human')
```

**Преимущества:**
- Скрытие сложности создания объектов
- Единая точка создания объектов одного типа
- Легкое добавление новых типов рас
- Кеширование для производительности

### Abstract Factory Pattern (Абстрактная фабрика)

**Назначение:** Предоставление интерфейса для создания семейств связанных объектов.

**Где используется:**
- Создание полного набора данных для персонажа (раса + класс + характеристики)

**Пример в коде:**

```python
# src/domain/services/character_generation.py
class CharacterBuilderFactory:
    """Абстрактная фабрика для создания персонажей."""
    
    @staticmethod
    def create_builder(build_type: str) -> 'CharacterBuilder':
        """Создает билдер для указанного типа."""
        if build_type == "standard":
            return StandardCharacterBuilder()
        elif build_type == "point_buy":
            return PointBuyCharacterBuilder()
        else:
            raise ValueError(f"Неизвестный тип билдера: {build_type}")

class StandardCharacterBuilder(CharacterBuilder):
    """Билдер для стандартного создания персонажа."""
    
    def build_character(self, request: CreateCharacterRequest) -> Character:
        # Создаем расу
        race = RaceFactory.create_race(request.race, request.subrace)
        
        # Создаем класс
        character_class = ClassFactory.create_class(request.character_class)
        
        # Генерируем характеристики
        attributes = AttributeGenerator.generate_standard_array()
        
        return Character(
            name=request.name,
            race=race,
            character_class=character_class,
            **attributes
        )
```

### Builder Pattern (Строитель)

**Назначение:** Построение сложных объектов пошагово.

**Где используется:**
- Создание персонажей с множеством параметров
- Генерация сложных сценариев бросков кубиков

**Пример в коде:**

```python
# src/domain/services/character_generation.py
class CharacterBuilder(ABC):
    """Абстрактный билдер персонажа."""
    
    @abstractmethod
    def set_basic_info(self, name: str, race: str, character_class: str) -> 'CharacterBuilder':
        pass
    
    @abstractmethod
    def set_attributes(self, method: GenerationMethod) -> 'CharacterBuilder':
        pass
    
    @abstractmethod
    def build(self) -> Character:
        pass

class StandardCharacterBuilder(CharacterBuilder):
    """Конкретная реализация билдера."""
    
    def __init__(self):
        self.name = ""
        self.race = None
        self.character_class = None
        self.attributes = {}
    
    def set_basic_info(self, name: str, race: str, character_class: str) -> 'CharacterBuilder':
        self.name = name
        self.race = RaceFactory.create_race(race)
        self.character_class = ClassFactory.create_class(character_class)
        return self
    
    def set_attributes(self, method: GenerationMethod) -> 'CharacterBuilder':
        generator = AttributeGenerator()
        self.attributes = generator.generate(method)
        return self
    
    def build(self) -> Character:
        return Character(
            name=self.name,
            race=self.race,
            character_class=self.character_class,
            **self.attributes
        )

# Использование
character = (StandardCharacterBuilder()
    .set_basic_info("Aragorn", "human", "fighter")
    .set_attributes(GenerationMethod.STANDARD_ARRAY)
    .build())
```

## Структурные паттерны (Structural Patterns)

### Adapter Pattern (Адаптер)

**Назначение:** Преобразование интерфейса одного класса в интерфейс другого.

**Где используется:**
- Адаптация существующей системы локализации к новому интерфейсу
- Интеграция с различными форматами сохранения данных

**Пример в коде:**

```python
# src/adapters/gateways/localization_adapter.py
class LocalizationAdapter(LocalizationInterface):
    """Адаптер для существующей системы локализации."""
    
    def __init__(self, legacy_loader):
        """Инициализирует адаптер с существующим loader."""
        self._loader = legacy_loader
    
    def get_text(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """Получает локализованный текст по ключу."""
        try:
            # Пробуем получить через существующий loader
            if hasattr(self._loader, 'get_text'):
                return self._loader.get_text(key, **kwargs)
            elif hasattr(self._loader, 'get_attribute_name'):
                # Для совместимости со старыми методами
                if 'attribute' in key:
                    return self._loader.get_attribute_name(key.split('.')[-1])
                else:
                    return default or key
            else:
                return default or key
        except:
            return default or key

# Использование в Domain слое
from src.domain.interfaces.localization import get_text

class Attribute:
    @property
    def localized_name(self) -> str:
        """Возвращает локализованное название."""
        return get_text(f"attribute_name.{self.name}")
```

### Facade Pattern (Фасад)

**Назначение:** Предоставление простого интерфейса к сложной подсистеме.

**Где используется:**
- Упрощение процесса создания персонажа
- Единый интерфейс к системе бросков кубиков

**Пример в коде:**

```python
# src/domain/value_objects/dice.py
class DiceRoll:
    """Фасад для системы бросков кубиков."""
    
    @staticmethod
    def roll_damage(dice_type: str, count: int = 1, modifier: int = 0) -> int:
        """Простой интерфейс для броска урона."""
        results = DiceRoll.roll_multiple(dice_type, count, modifier)
        return sum(result.total for result in results)
    
    @staticmethod
    def roll_with_advantage(dice_type: str = 'd20', modifier: int = 0) -> DiceResult:
        """Бросок с преимуществом."""
        dice = Dice(dice_type)
        return dice.roll_with_modifier(RollModifierType.ADVANTAGE, modifier)
    
    @staticmethod
    def roll_with_disadvantage(dice_type: str = 'd20', modifier: int = 0) -> DiceResult:
        """Бросок с помехой."""
        dice = Dice(dice_type)
        return dice.roll_with_modifier(RollModifierType.DISADVANTAGE, modifier)

# Использование
damage = DiceRoll.roll_damage("d6", 2, 3)  # 2d6+3 урона
attack = DiceRoll.roll_with_advantage("d20", 5)  # Атака с преимуществом +5
```

## Поведенческие паттерны (Behavioral Patterns)

### Strategy Pattern (Стратегия)

**Назначение:** Определение семейства алгоритмов и их инкапсуляция.

**Где используется:**
- Различные методы бросков кубиков (обычный, с преимуществом, с помехой)
- Алгоритмы генерации характеристик персонажа

**Пример в коде:**

```python
# src/domain/value_objects/dice.py
class RollModifierType(Enum):
    """Типы модификаторов бросков."""
    NORMAL = "normal"
    ADVANTAGE = "disadvantage"
    DISADVANTAGE = "disadvantage"
    TRIPLE_ADVANTAGE = "triple_advantage"

class Dice:
    def roll_with_modifier(self, modifier_type: RollModifierType, modifier: int = 0) -> DiceResult:
        """Выполняет бросок с модификатором."""
        if not self._config:
            raise ValueError(f"Неизвестный тип кубика: {self.dice_type}")
        
        # Выбор стратегии броска
        modifier_config = RollModifierConfig._load_config(modifier_type.value)
        rolls = [random.randint(1, self._config.sides) for _ in range(modifier_config.rolls)]
        
        # Применение стратегии
        if modifier_config.type == "best_of":
            value = max(rolls)  # Advantage
        elif modifier_config.type == "worst_of":
            value = min(rolls)  # Disadvantage
        else:
            value = rolls[0]  # Normal
        
        return DiceResult(
            value=value,
            dice_type=self.dice_type,
            rolls=rolls,
            modifier_type=modifier_type,
            modifier=modifier
        )

# Конфигурация стратегий
class RollModifierConfig:
    _config_cache = {
        "normal": {"rolls": 1, "type": "normal"},
        "advantage": {"rolls": 2, "type": "best_of"},
        "disadvantage": {"rolls": 2, "type": "worst_of"},
        "triple_advantage": {"rolls": 3, "type": "best_of"}
    }
```

### Command Pattern (Команда)

**Назначение:** Инкапсуляция запроса как объекта.

**Где используется:**
- Система меню и команд пользователя
- Отмена/повтор действий в редакторе персонажа

**Пример в коде:**

```python
# src/infrastructure/ui/commands.py
class Command(ABC):
    """Абстрактная команда."""
    
    @abstractmethod
    def execute(self) -> None:
        pass
    
    @abstractmethod
    def undo(self) -> None:
        pass

class CreateCharacterCommand(Command):
    """Команда создания персонажа."""
    
    def __init__(self, character_data: dict, character_repo: CharacterRepository):
        self.character_data = character_data
        self.character_repo = character_repo
        self.created_character = None
    
    def execute(self) -> Character:
        """Создает персонажа."""
        character = CharacterFactory.create(**self.character_data)
        self.created_character = self.character_repo.save(character)
        return self.created_character
    
    def undo(self) -> None:
        """Отменяет создание персонажа."""
        if self.created_character:
            self.character_repo.delete(self.created_character.name)

class MenuController:
    """Контроллер меню, использующий команды."""
    
    def __init__(self):
        self.command_history: List[Command] = []
    
    def handle_create_character(self, character_data: dict) -> Character:
        """Обрабатывает создание персонажа."""
        command = CreateCharacterCommand(character_data, self.character_repo)
        character = command.execute()
        self.command_history.append(command)
        return character
    
    def undo_last_action(self) -> bool:
        """Отменяет последнее действие."""
        if not self.command_history:
            return False
        
        last_command = self.command_history.pop()
        last_command.undo()
        return True
```

### Observer Pattern (Наблюдатель)

**Назначение:** Определение зависимости один-ко-многим между объектами.

**Где используется:**
- Уведомления об изменении характеристик персонажа
- Обновление UI при изменении данных

**Пример в коде:**

```python
# src/domain/events.py
class Event(ABC):
    """Абстрактное событие."""
    pass

class AttributeChangedEvent(Event):
    """Событие изменения характеристики."""
    
    def __init__(self, character_name: str, attribute_name: str, old_value: int, new_value: int):
        self.character_name = character_name
        self.attribute_name = attribute_name
        self.old_value = old_value
        self.new_value = new_value

class Observer(ABC):
    """Абстрактный наблюдатель."""
    
    @abstractmethod
    def handle_event(self, event: Event) -> None:
        pass

class Character:
    """Персонаж с поддержкой событий."""
    
    def __init__(self, name: str):
        self.name = name
        self._observers: List[Observer] = []
    
    def add_observer(self, observer: Observer) -> None:
        """Добавляет наблюдателя."""
        self._observers.append(observer)
    
    def remove_observer(self, observer: Observer) -> None:
        """Удаляет наблюдателя."""
        self._observers.remove(observer)
    
    def _notify_observers(self, event: Event) -> None:
        """Уведомляет всех наблюдателей."""
        for observer in self._observers:
            observer.handle_event(event)
    
    def set_strength(self, value: int) -> None:
        """Устанавливает силу с уведомлением."""
        old_value = self.strength.value
        self.strength.value = value
        
        # Уведомляем наблюдателей
        event = AttributeChangedEvent(self.name, "strength", old_value, value)
        self._notify_observers(event)

class CharacterUI(Observer):
    """UI для персонажа, реагирующий на изменения."""
    
    def handle_event(self, event: Event) -> None:
        """Обрабатывает события персонажа."""
        if isinstance(event, AttributeChangedEvent):
            print(f"{event.attribute_name} изменено с {event.old_value} на {event.new_value}")
            self.update_display()
```

## Архитектурные паттерны

### Repository Pattern (Репозиторий)

**Назначение:** Абстрагирование доступа к данным.

**Где используется:**
- Сохранение и загрузка персонажей
- Доступ к конфигурациям игры

**Пример в коде:**

```python
# src/domain/repositories/character_repository.py
class CharacterRepository(ABC):
    """Интерфейс репозитория персонажей."""
    
    @abstractmethod
    def save(self, character: Character) -> Character:
        """Сохраняет персонажа."""
        pass
    
    @abstractmethod
    def load(self, name: str) -> Optional[Character]:
        """Загружает персонажа по имени."""
        pass
    
    @abstractmethod
    def list_characters(self) -> List[str]:
        """Возвращает список имен всех персонажей."""
        pass
    
    @abstractmethod
    def delete(self, name: str) -> bool:
        """Удаляет персонажа."""
        pass

# src/adapters/repositories/character_repository.py
class YamlCharacterRepository(CharacterRepository):
    """Реализация репозитория с использованием YAML файлов."""
    
    def __init__(self, save_directory: str = "data/saves"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
    
    def save(self, character: Character) -> Character:
        """Сохраняет персонажа в YAML файл."""
        save_data = CharacterSaveData.from_character(character)
        file_path = self.save_directory / f"{character.name}.yaml"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(save_data.to_dict(), f, default_flow_style=False, allow_unicode=True)
        
        return character
    
    def load(self, name: str) -> Optional[Character]:
        """Загружает персонажа из YAML файла."""
        file_path = self.save_directory / f"{name}.yaml"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            save_data = CharacterSaveData.from_dict(data)
            return save_data.to_character()
```

### Dependency Injection Pattern (Внедрение зависимостей)

**Назначение:** Внедрение зависимостей извне вместо создания внутри класса.

**Где используется:**
- Use Cases получают репозитории через конструктор
- UI контроллеры получают Use Cases

**Пример в коде:**

```python
# src/application/use_cases/create_character.py
class CreateCharacterUseCase:
    """Use case для создания персонажа."""
    
    def __init__(self, 
                 character_repo: CharacterRepository,
                 localization_service: LocalizationInterface):
        self.character_repo = character_repo
        self.localization = localization_service
    
    def execute(self, request: CreateCharacterRequest) -> Character:
        """Создает нового персонажа."""
        # Валидация
        if not request.name or len(request.name.strip()) == 0:
            raise ValueError(self.localization.get_text("error.empty_name"))
        
        # Создание через доменные сервисы
        character = CharacterFactory.create(
            name=request.name,
            race=request.race,
            character_class=request.character_class
        )
        
        # Сохранение через репозиторий
        return self.character_repo.save(character)

# src/infrastructure/ui/menus/character_creation.py
class CharacterCreationController:
    """Контроллер создания персонажа."""
    
    def __init__(self, 
                 input_handler: InputHandler,
                 renderer: Renderer,
                 create_character_use_case: CreateCharacterUseCase):
        self.input_handler = input_handler
        self.renderer = renderer
        self.create_character_use_case = create_character_use_case
    
    def create_character(self) -> Optional[Character]:
        """Создает персонажа через UI."""
        # Сбор данных от пользователя
        request = self._collect_user_input()
        
        # Выполнение use case
        try:
            return self.create_character_use_case.execute(request)
        except ValueError as e:
            self.renderer.show_error(str(e))
            return None
```

## Рекомендации по использованию паттернов

### Когда использовать Factory:
- Когда есть сложная логика создания объектов
- Когда нужно скрыть конкретные классы от клиента
- Когда объекты создаются на основе конфигурации

### Когда использовать Strategy:
- Когда есть несколько алгоритмов для решения одной задачи
- Когда нужно переключать алгоритмы во время выполнения
- Когда алгоритмы могут быть добавлены в будущем

### Когда использовать Repository:
- Когда нужна абстракция над хранением данных
- Когда может потребоваться смена способа хранения
- Когда нужно тестировать бизнес-логику отдельно от хранения

### Когда использовать Observer:
- Когда нужно уведомлять множество объектов об изменениях
- Когда объекты не должны знать друг о друге напрямую
- Когда нужна слабая связанность между компонентами

Эти паттерны помогают создавать гибкую, расширяемую и поддерживаемую архитектуру в проекте DnD MUD.
