# Подзадача 8: Выбор Заговоров и Заклинаний

## Цель
Выбор магических способностей для заклинателей

## Требования
- Проверка на наличие заклинаний у класса
- Выбор заговоров (cantrips)
- Выбор заклинаний 1-го уровня
- Учет способностей для подготовки заклинаний
- Расчет DC для заклинаний и атаковых бонусов

## Классы с магией
- **Wizard** (Волшебник)
- **Sorcerer** (Чародей)
- **Warlock** (Колдун)
- **Bard** (Бард)
- **Cleric** (Жрец)
- **Druid** (Друид)
- **Paladin** (Паладин)
- **Ranger** (Следопыт)
- **Artificer** (Изобретатель)

## Критерии выполнения
- Корректная работа только с магическими классами
- Правильный расчет spell DC и attack bonus
- Сохранение списка заклинаний

## Техническая реализация

### Компоненты
- **SpellDataLoader** - загрузка заклинаний
- **SpellSelector** - интерфейс выбора
- **SpellCalculator** - расчет параметров

### Расчет параметров заклинаний
```python
def calculate_spell_dc(ability_mod: int, proficiency_bonus: int) -> int:
    """Расчет сложности спасброска от заклинания"""
    return 8 + ability_mod + proficiency_bonus

def calculate_spell_attack(ability_mod: int, proficiency_bonus: int) -> int:
    """Расчет атакового бонуса заклинаний"""
    return ability_mod + proficiency_bonus
```

### Структура данных заклинания
```python
@dataclass
class Spell:
    name: str
    name_ru: str
    level: int
    school: str
    casting_time: str
    range: str
    components: str
    duration: str
    description: str
    classes: List[str]
    ritual: bool = False
```

### Алгоритм
1. Проверка на наличие магии у класса
2. Определение доступных заговоров и заклинаний
3. Расчет количества заклинаний для выбора
4. Выбор заговоров (cantrips)
5. Выбор заклинаний 1-го уровня
6. Расчет spell DC и attack bonus
7. Определение подготовленных заклинаний (если применимо)
8. Сохранение списка заклинаний

### Правила для разных классов
- **Wizard**: 3 заговора, 6 заклинаний в книге, готовит 3-4
- **Cleric**: 0 заговоров, знает все заклинания, готовит 4-5
- **Sorcerer**: 4 заговора, 2 заклинания известных
- **Warlock**: 2 заговора, 2 заклинания известных
- **Bard**: 2 заговора, 4 заклинания известных

### Интеграция с архитектурой
```python
class SpellSelectionService:
    def __init__(self, class_data: ClassData, abilities: AbilityScores):
        self.class_data = class_data
        self.abilities = abilities
    
    async def select_spells(self) -> SpellSet:
        # Реализация выбора заклинаний
        pass
```

### Тестирование
- Тесты проверки магических классов
- Тесты расчета spell DC и attack bonus
- Тесты выбора заклинаний для разных классов
- Тесты подготовки заклинаний
