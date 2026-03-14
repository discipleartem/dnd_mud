# 4. Выбор навыков

## Обзор

Четвертый этап - выбор навыков персонажа на основе класса, расы и характеристик с финальным расчетом модификаторов владения.

## Задачи

### TASK-3.7.1: Сервис навыков (SkillsService)

**Цель:** Управление навыками и расчет финальных модификаторов

**Функциональность:**
- Расчет доступных навыков на основе класса
- Применение бонусов от расы/класса/предыстории
- Валидация количества выбираемых навыков
- Расчет итоговых модификаторов навыков

**Структура данных:**
```python
@dataclass
class Skill:
    name: str
    ability: str  # "STR", "DEX", "CON", "INT", "WIS", "CHA"
    description: str

@dataclass
class SkillProficiency:
    skill: str
    proficiency_bonus: int  # 0 = none, 2 = proficient, 4 = expert
    total_modifier: int  # ability_mod + proficiency_bonus
```

**Список навыков D&D 5e:**
- **Strength:** Athletics
- **Dexterity:** Acrobatics, Sleight of Hand, Stealth
- **Intelligence:** Arcana, History, Investigation, Nature, Religion
- **Wisdom:** Animal Handling, Insight, Medicine, Perception, Survival
- **Charisma:** Deception, Intimidation, Performance, Persuasion

**Методы:**
- `get_all_skills() -> List[Skill]`
- `get_class_skills(class_name: str) -> List[str]`
- `apply_race_bonuses(skills: List[str], race_bonuses: Dict[str, List[str]]) -> List[str]`
- `calculate_skill_modifier(skill: str, ability_mod: int, proficiency: bool = False, expertise: bool = False) -> int`
- `validate_skill_selection(selected_skills: List[str], class_skills: List[str], max_count: int) -> bool`

### TASK-3.7.2: UI выбора навыков (SkillsSelectionAdapter)

**Цель:** Интерактивный выбор навыков с учетом бонусов

**Функциональность:**
- Интерактивный выбор с учетом бонусов
- Отображение доступных и выбранных навыков
- Показ итоговых владений с модификаторами
- Валидация количества выбранных навыков

**UI Flow:**
1. Расчет доступных навыков:
   - Базовые навыки класса
   - Расовые бонусы (например, у эльфов + Perception)
   - Количество для выбора: 2 + Intelligence modifier
2. Отображение интерфейса выбора:
   - Список всех навыков с характеристиками
   - Подсветка уже выбранных
   - Счетчик выбранных/доступных
3. Показ модификаторов для каждого навыка:
   - Ability modifier
   - Proficiency bonus (если выбран)
   - Total modifier
4. Валидация и подтверждение выбора

**Пример расчета модификатора:**
```
Персонаж: DEX 14 (+2), выбрал Stealth
- DEX modifier: +2
- Proficiency bonus: +2 (уровень 1)
- Total Stealth: +4
```

## Правила D&D 5e

- **Количество навыков:** 2 + Intelligence modifier (минимум 2)
- **Профессиональный бонус:** +2 на 1 уровне, растет с уровнем
- **Расовые бонусы:** Некоторые расы дают владение определенными навыками
- **Экспертиза:** Некоторые классы могут выбрать экспертизу (double proficiency)

## Зависимости

- YAML файлы с данными навыков (`data/skills/`)
- AbilitiesService для получения модификаторов характеристик
- ClassService для получения классовых навыков
- RaceService для получения расовых бонусов
- CharacterCreationService для координации

## Финальный результат

После этого этапа персонаж имеет:
- Выбранную расу с бонусами
- Сгенерированные характеристики
- Выбранный класс с особенностями
- Выбранные навыки с финальными модификаторами

## Следующие этапы

- Предыстория (TASK-3.6)
- Черты (TASK-3.8)
- Языки (TASK-3.9)
- Заклинания (TASK-3.10)
- Снаряжение (TASK-3.11)
