# API Reference

## Обзор

D&D Text MUD предоставляет программный API для расширения функциональности и создания модов.

## Основные модули

### Core Module

#### Game

```python
from dnd_mud.core.game import Game

class Game:
    """Основной класс игры"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Инициализация игры"""
        
    def start(self) -> None:
        """Запуск игрового цикла"""
        
    def load_character(self, save_path: str) -> Character:
        """Загрузка персонажа из сохранения"""
        
    def save_character(self, character: Character, save_path: str) -> None:
        """Сохранение персонажа"""
        
    def get_current_adventure(self) -> Adventure:
        """Получение текущего приключения"""
```

#### Config

```python
from dnd_mud.core.config import Config

class Config:
    """Управление конфигурацией игры"""
    
    def __init__(self, config_path: str):
        """Загрузка конфигурации из YAML файла"""
        
    def get(self, key: str, default=None) -> Any:
        """Получение значения конфигурации"""
        
    def set(self, key: str, value: Any) -> None:
        """Установка значения конфигурации"""
        
    def save(self) -> None:
        """Сохранение конфигурации"""
```

### Data Module

#### DataLoader

```python
from dnd_mud.data.loader import DataLoader

class DataLoader:
    """Загрузчик игровых данных из YAML файлов"""
    
    def load_races(self) -> Dict[str, Race]:
        """Загрузка рас"""
        
    def load_classes(self) -> Dict[str, Class]:
        """Загрузка классов"""
        
    def load_backgrounds(self) -> Dict[str, Background]:
        """Загрузка предысторий"""
        
    def load_skills(self) -> Dict[str, Skill]:
        """Загрузка навыков"""
        
    def load_spells(self) -> Dict[str, Spell]:
        """Загрузка заклинаний"""
        
    def load_items(self) -> Dict[str, Item]:
        """Загрузка предметов"""
```

#### Models

```python
from dnd_mud.data.models import Race, Class, Background

@dataclass
class Race:
    """Модель расы"""
    name: str
    description: str
    size: str
    speed: int
    ability_bonuses: Dict[str, int]
    traits: List[Trait]
    languages: List[str]
    subraces: Optional[Dict[str, "Race"]] = None

@dataclass
class Class:
    """Модель класса"""
    name: str
    description: str
    hit_die: int
    primary_ability: List[str]
    saving_throws: List[str]
    skill_choices: int
    skill_options: List[str]
    equipment: Dict[str, Any]
    features: Dict[str, List[Feature]]
    subclasses: Optional[Dict[str, "Subclass"]] = None
```

### Character Module

#### Character

```python
from dnd_mud.character.character import Character

class Character:
    """Основной класс персонажа"""
    
    def __init__(self, name: str, race: Race, character_class: Class, 
                 background: Background):
        """Создание персонажа"""
        
    def get_ability_score(self, ability: str) -> int:
        """Получение значения характеристики"""
        
    def get_ability_modifier(self, ability: str) -> int:
        """Получение модификатора характеристики"""
        
    def get_skill_bonus(self, skill: str) -> int:
        """Получение бонуса к навыку"""
        
    def get_proficiency_bonus(self) -> int:
        """Получение бонуса мастерства"""
        
    def level_up(self) -> None:
        """Повышение уровня"""
        
    def add_experience(self, xp: int) -> None:
        """Добавление опыта"""
        
    def take_damage(self, damage: int, damage_type: str) -> int:
        """Получение урона"""
        
    def heal(self, amount: int) -> None:
        """Лечение"""
        
    def is_alive(self) -> bool:
        """Проверка жив ли персонаж"""
```

#### Race

```python
from dnd_mud.character.race import Race

class Race:
    """Класс расы персонажа"""
    
    def apply_bonuses(self, character: Character) -> None:
        """Применение расовых бонусов к характеристикам"""
        
    def get_traits(self) -> List[Trait]:
        """Получение расовых черт"""
        
    def get_languages(self) -> List[str]:
        """Получение языков расы"""
```

#### Class

```python
from dnd_mud.character.class_ import Class

class Class:
    """Класс персонажа"""
    
    def get_hit_points(self, level: int, constitution: int) -> int:
        """Расчет хит-поинтов"""
        
    def get_features(self, level: int) -> List[Feature]:
        """Получение способностей класса на уровне"""
        
    def get_spell_slots(self, level: int) -> Dict[int, int]:
        """Получение слотов заклинаний"""
        
    def can_cast_spell(self, spell: Spell, character: Character) -> bool:
        """Проверка возможности колдовать заклинание"""
```

### Combat Module

#### Combat

```python
from dnd_mud.combat.combat import Combat

class Combat:
    """Управление боевым encounters"""
    
    def __init__(self, participants: List[Combatant]):
        """Инициализация боя с участниками"""
        
    def start_combat(self) -> None:
        """Начало боя"""
        
    def roll_initiative(self, combatant: Combatant) -> int:
        """Бросок инициативы"""
        
    def get_turn_order(self) -> List[Combatant]:
        """Получение порядка ходов"""
        
    def execute_turn(self, combatant: Combatant, action: Action) -> None:
        """Выполнение хода"""
        
    def end_combat(self) -> None:
        """Завершение боя"""
        
    def is_combat_active(self) -> bool:
        """Проверка активен ли бой"""
```

#### Action

```python
from dnd_mud.combat.actions import Action

class Action:
    """Боевое действие"""
    
    def __init__(self, name: str, action_type: str, 
                 range_: str, target: str):
        """Создание действия"""
        
    def execute(self, attacker: Combatant, target: Combatant) -> ActionResult:
        """Выполнение действия"""
        
    def calculate_damage(self, attacker: Combatant, target: Combatant) -> int:
        """Расчет урона"""
        
    def roll_attack(self, attacker: Combatant, target: Combatant) -> AttackResult:
        """Бросок атаки"""
```

### Adventure Module

#### Adventure

```python
from dnd_mud.adventure.adventure import Adventure

class Adventure:
    """Приключение"""
    
    def __init__(self, adventure_data: Dict[str, Any]):
        """Создание приключения из данных"""
        
    def start(self, character: Character) -> None:
        """Начало приключения"""
        
    def get_current_scene(self) -> Scene:
        """Получение текущей сцены"""
        
    def transition_to_scene(self, scene_id: str) -> None:
        """Переход к сцене"""
        
    def check_objectives(self) -> List[Objective]:
        """Проверка выполнения целей"""
        
    def is_completed(self) -> bool:
        """Проверка завершения приключения"""
```

#### Dialogue

```python
from dnd_mud.adventure.dialogue import Dialogue

class Dialogue:
    """Система диалогов"""
    
    def __init__(self, dialogue_data: Dict[str, Any]):
        """Создание диалога из данных"""
        
    def get_current_text(self) -> str:
        """Получение текущего текста"""
        
    def get_responses(self) -> List[Response]:
        """Получение вариантов ответа"""
        
    def select_response(self, response_index: int) -> None:
        """Выбор ответа"""
        
    def check_skill_requirement(self, skill: str, dc: int) -> bool:
        """Проверка требования навыка"""
```

### Mods Module

#### ModManager

```python
from dnd_mud.mods.manager import ModManager

class ModManager:
    """Менеджер модов"""
    
    def __init__(self, mods_directory: str = "Mods"):
        """Инициализация менеджера модов"""
        
    def load_mod(self, mod_name: str) -> Mod:
        """Загрузка мода"""
        
    def enable_mod(self, mod_name: str) -> None:
        """Включение мода"""
        
    def disable_mod(self, mod_name: str) -> None:
        """Отключение мода"""
        
    def get_enabled_mods(self) -> List[Mod]:
        """Получение включенных модов"""
        
    def check_conflicts(self, mod_name: str) -> List[str]:
        """Проверка конфликтов мода"""
        
    def resolve_conflicts(self, mod_name: str) -> None:
        """Разрешение конфликтов"""
```

#### Mod

```python
from dnd_mud.mods.mod import Mod

class Mod:
    """Класс мода"""
    
    def __init__(self, mod_info: Dict[str, Any]):
        """Создание мода из информации"""
        
    def get_info(self) -> Dict[str, Any]:
        """Получение информации о моде"""
        
    def load_content(self) -> Dict[str, Any]:
        """Загрузка контента мода"""
        
    def validate(self) -> ValidationResult:
        """Валидация мода"""
        
    def is_compatible(self, game_version: str) -> bool:
        """Проверка совместимости с версией игры"""
```

### Save Module

#### SaveManager

```python
from dnd_mud.save.save_manager import SaveManager

class SaveManager:
    """Менеджер сохранений"""
    
    def __init__(self, saves_directory: str = "saves"):
        """Инициализация менеджера сохранений"""
        
    def create_save(self, character: Character, slot: int) -> str:
        """Создание сохранения"""
        
    def load_save(self, slot: int) -> SaveData:
        """Загрузка сохранения"""
        
    def delete_save(self, slot: int) -> None:
        """Удаление сохранения"""
        
    def list_saves(self) -> List[SaveInfo]:
        """Получение списка сохранений"""
        
    def auto_save(self, character: Character) -> None:
        """Автосохранение"""
```

### I18n Module

#### Translator

```python
from dnd_mud.i18n.translator import Translator

class Translator:
    """Переводчик"""
    
    def __init__(self, locale: str = "ru"):
        """Инициализация переводчика"""
        
    def translate(self, key: str, **kwargs) -> str:
        """Перевод строки"""
        
    def set_locale(self, locale: str) -> None:
        """Установка языка"""
        
    def get_available_locales(self) -> List[str]:
        """Получение доступных языков"""
        
    def add_translation(self, locale: str, key: str, value: str) -> None:
        """Добавление перевода"""
```

## События и хуки

### Event System

```python
from dnd_mud.core.events import Event, EventBus

class Event:
    """Базовый класс события"""
    
    def __init__(self, event_type: str, data: Dict[str, Any]):
        """Создание события"""

class EventBus:
    """Шина событий"""
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Подписка на событие"""
        
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Отписка от события"""
        
    def emit(self, event: Event) -> None:
        """Отправка события"""
```

### Примеры событий

```python
# События персонажа
character_created = Event("character_created", {"character": character})
character_leveled_up = Event("character_leveled_up", {"character": character, "new_level": 5})
character_died = Event("character_died", {"character": character})

# События боя
combat_started = Event("combat_started", {"combat": combat, "participants": participants})
combat_ended = Event("combat_ended", {"combat": combat, "winner": winner})
damage_dealt = Event("damage_dealt", {"attacker": attacker, "target": target, "damage": 10})

# События приключений
adventure_started = Event("adventure_started", {"adventure": adventure, "character": character})
objective_completed = Event("objective_completed", {"objective": objective, "character": character})
adventure_completed = Event("adventure_completed", {"adventure": adventure, "character": character})
```

## Расширения API

### Создание плагинов

```python
from dnd_mud.core.plugin import Plugin

class MyPlugin(Plugin):
    """Пример плагина"""
    
    def __init__(self):
        super().__init__("my_plugin", "1.0.0")
        
    def initialize(self, game: Game) -> None:
        """Инициализация плагина"""
        # Подписка на события
        game.event_bus.subscribe("character_created", self.on_character_created)
        
    def on_character_created(self, event: Event) -> None:
        """Обработчик создания персонажа"""
        character = event.data["character"]
        # Логика плагина
        
    def shutdown(self) -> None:
        """Завершение работы плагина"""
        # Очистка ресурсов
```

### Регистрация плагина

```python
from dnd_mud.core.registry import register_plugin

@register_plugin
class MyPlugin(Plugin):
    """Плагин с автоматической регистрацией"""
    pass
```

## Конфигурация API

### Настройка через конфигурационный файл

```yaml
# config.yaml
api:
  version: "1.0.0"
  plugins:
    enabled: true
    directory: "plugins"
    auto_load: true
  events:
    max_queue_size: 1000
    timeout: 5.0
  mods:
    check_conflicts: true
    auto_resolve: false
    max_load_time: 30.0
```

### Программная настройка

```python
from dnd_mud.core.config import Config

config = Config("config.yaml")

# Настройка API
config.set("api.plugins.enabled", True)
config.set("api.mods.check_conflicts", True)
config.set("api.events.max_queue_size", 1000)

config.save()
```

## Тестирование API

### Unit тесты

```python
import pytest
from dnd_mud.character.character import Character
from dnd_mud.data.models import Race, Class, Background

def test_character_creation():
    """Тест создания персонажа"""
    race = Race(name="Человек", ...)
    character_class = Class(name="Воин", ...)
    background = Background(name="Солдат", ...)
    
    character = Character("Тест", race, character_class, background)
    
    assert character.name == "Тест"
    assert character.race == race
    assert character.level == 1
    assert character.is_alive() == True
```

### Integration тесты

```python
def test_combat_system():
    """Тест боевой системы"""
    character = create_test_character()
    enemy = create_test_enemy()
    
    combat = Combat([character, enemy])
    combat.start_combat()
    
    assert combat.is_combat_active() == True
    
    # Выполнение хода
    action = Action("attack", "melee", "5ft", "single")
    combat.execute_turn(character, action)
    
    assert enemy.current_hp < enemy.max_hp
```

## Примеры использования

### Создание персонажа через API

```python
from dnd_mud.character.character import Character
from dnd_mud.data.loader import DataLoader

# Загрузка данных
loader = DataLoader()
races = loader.load_races()
classes = loader.load_classes()
backgrounds = loader.load_backgrounds()

# Создание персонажа
character = Character(
    name="Арагорн",
    race=races["human"],
    character_class=classes["fighter"],
    background=backgrounds["soldier"]
)

# Настройка характеристик
character.set_ability_score("strength", 16)
character.set_ability_score("dexterity", 14)
character.set_ability_score("constitution", 15)
character.set_ability_score("intelligence", 10)
character.set_ability_score("wisdom", 12)
character.set_ability_score("charisma", 13)

# Добавление опыта
character.add_experience(300)

# Сохранение
save_manager = SaveManager()
save_manager.create_save(character, slot=1)
```

### Создание мода через API

```python
from dnd_mud.mods.manager import ModManager
from dnd_mud.mods.mod import Mod

# Создание менеджера модов
mod_manager = ModManager()

# Создание нового мода
mod_info = {
    "name": "Test Mod",
    "version": "1.0.0",
    "description": "Тестовый мод",
    "author": "Developer"
}

mod = Mod(mod_info)

# Добавление контента
mod.add_race({
    "name": "Тестовая раса",
    "description": "Раса для тестирования",
    "size": "medium",
    "speed": 30,
    "ability_bonuses": {"strength": 2}
})

# Валидация и сохранение
validation_result = mod.validate()
if validation_result.is_valid:
    mod_manager.save_mod(mod)
else:
    print(f"Ошибки валидации: {validation_result.errors}")
```

Этот API reference предоставляет полный обзор программного интерфейса D&D Text MUD для создания модов и расширений.
