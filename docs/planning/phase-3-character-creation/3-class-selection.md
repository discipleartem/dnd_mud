# 3. Выбор класса

## Обзор

Третий этап - выбор класса и архетипа персонажа с проверкой соответствия характеристик и получением базовых навыков.

## Задачи

### TASK-3.5.1: Сервис классов (ClassService)

**Цель:** Управление данными классов и архетипов

**Функциональность:**
- Загрузка классов и архетипов из YAML
- Class и Subclass entities
- Проверка требований к характеристикам
- Расчет классовых навыков и особенностей

**Структура данных:**
```python
@dataclass
class Class:
    name: str
    description: str
    hit_die: str  # "d8", "d10", etc.
    primary_ability: str  # "STR", "DEX", etc.
    saving_throws: List[str]
    skills: List[str]  # доступные навыки для выбора
    features: List[str]
    subclasses: Optional[List['Subclass']] = None

@dataclass
class Subclass:
    name: str
    parent_class: str
    description: str
    level_required: int = 3
    features: List[str]
```

**Методы:**
- `load_classes() -> List[Class]`
- `get_class(name: str) -> Optional[Class]`
- `get_subclass(class_name: str, subclass_name: str) -> Optional[Subclass]`
- `check_requirements(abilities: Dict[str, int], class_name: str) -> bool`
- `get_available_skills(class_name: str, abilities: Dict[str, int]) -> List[str]`
- `get_class_features(class_name: str, level: int = 1) -> List[str]`

### TASK-3.5.2: UI выбора класса (ClassSelectionAdapter)

**Цель:** Интерфейс выбора класса с учетом характеристик

**Функциональность:**
- Выбор класса с учетом характеристик
- Выбор архетипа (если доступен)
- Отображение особенностей класса
- Интеграция с характеристиками из этапа 2

**UI Flow:**
1. Показать список доступных классов
2. Отобразить информацию о классе:
   - Hit Die, Primary Ability, Saving Throws
   - Требования к характеристикам (если есть)
   - Доступные навыки (количество для выбора)
3. Проверка соответствия характеристик:
   - Подсветка классов, доступных с текущими характеристиками
   - Предупреждения о нехватке характеристик
4. Выбор архетипа (для классов с подклассами)
5. Подтверждение выбора

**Примеры требований к характеристикам:**
- **Монах:** 13+ Wisdom и Dexterity
- **Паладин:** 13+ Charisma
- **Рейнджер:** 13+ Dexterity и Wisdom
- **Волшебник:** 13+ Intelligence

## Зависимости

- YAML файлы с данными классов (`data/classes/`)
- AbilitiesService для проверки характеристик
- CharacterCreationService для координации
- SkillsService для передачи доступных навыков

## Интеграция с навыками

После выбора класса:
- Передать список доступных навыков в SkillsService
- Учесть количество навыков для выбора (2 + Intellect modifier)
- Применить классовые бонусы к навыкам

## Следующий этап

Выбор навыков из доступных для класса и расы.
