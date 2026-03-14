# 1. Выбор расы

## Обзор

Первый этап создания персонажа - выбор расы и подрасы с применением соответствующих бонусов к характеристикам.

## Задачи

### TASK-3.3.1: Сервис рас (RaceService)

**Цель:** Управление данными рас и применение бонусов

**Функциональность:**
- Загрузка рас и подрас из YAML файлов
- Race и Subrace entities
- Применение расовых бонусов к характеристикам
- Валидация выбора расы/подрасы

**Структура данных:**
```python
@dataclass
class Race:
    name: str
    description: str
    speed: int
    size: str
    ability_bonuses: Dict[str, int]  # STR, DEX, etc.
    traits: List[str]
    languages: List[str]
    subraces: Optional[List['Subrace']] = None

@dataclass  
class Subrace:
    name: str
    parent_race: str
    description: str
    ability_bonuses: Dict[str, int]
    traits: List[str]
```

**Методы:**
- `load_races() -> List[Race]`
- `get_race(name: str) -> Optional[Race]`
- `get_subrace(race_name: str, subrace_name: str) -> Optional[Subrace]`
- `apply_race_bonuses(abilities: Dict[str, int], race: Race, subrace: Optional[Subrace]) -> Dict[str, int]`

### TASK-3.3.2: UI выбора расы (RaceSelectionAdapter)

**Цель:** Интерфейс выбора расы и подрасы

**Функциональность:**
- Многоуровневое меню (раса → подраса)
- Отображение бонусов и особенностей расы
- Интеграция с CharacterCreationAdapter
- Валидация выбора

**UI Flow:**
1. Показать список доступных рас
2. При выборе расы с подрасами - показать подменю
3. Отобразить детали: бонусы, черты, языки, скорость
4. Подтверждение выбора
5. Применение бонусов к характеристикам

**Интеграция:**
- Вызов RaceService для получения данных
- Передача выбранной расы в CharacterCreationService
- Обновление UI с примененными бонусами

## Зависимости

- YAML файлы с данными рас (`data/races/`)
- CharacterCreationService для координации
- AbilitiesService для применения бонусов

## Следующий этап

Генерация характеристик с учетом расовых бонусов.
