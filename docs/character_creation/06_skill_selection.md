# Подзадача 6: Выбор навыков

## Цель
Финализация списка навыков персонажа

## Требования
- Учет навыков от класса, расы, предыстории
- Возможность выбора дополнительных навыков
- Расчет бонусов к навыкам
- Профессиональное владение

## Навыки D&D
- **Athletics** (Атлетика) - Сила
- **Acrobatics** (Акробатика) - Ловкость
- **Sleight of Hand** (Ловкость рук) - Ловкость
- **Stealth** (Скрытность) - Ловкость
- **Arcana** (Магия) - Интеллект
- **History** (История) - Интеллект
- **Investigation** (Расследование) - Интеллект
- **Nature** (Природа) - Интеллект
- **Religion** (Религия) - Интеллект
- **Animal Handling** (Уход за животными) - Мудрость
- **Insight** (Проницательность) - Мудрость
- **Medicine** (Медицина) - Мудрость
- **Perception** (Восприятие) - Мудрость
- **Survival** (Выживание) - Мудрость
- **Deception** (Обман) - Харизма
- **Intimidation** (Запугивание) - Харизма
- **Performance** (Выступление) - Харизма
- **Persuasion** (Убеждение) - Харизма

## Критерии выполнения
- Корректный подсчет бонусов
- Учет всех источников навыков
- Сохранение финального списка

## Техническая реализация

### Компоненты
- **SkillCalculator** - расчет бонусов
- **SkillSelector** - интерфейс выбора
- **SkillManager** - управление списком навыков

### Расчет бонуса к навыку
```python
def calculate_skill_bonus(ability_mod: int, proficiency_bonus: int, 
                        is_proficient: bool, has_expertise: bool) -> int:
    """Расчет бонуса к навыку"""
    bonus = ability_mod
    if is_proficient:
        bonus += proficiency_bonus
        if has_expertise:
            bonus += proficiency_bonus  # Двойной бонус
    return bonus
```

### Алгоритм
1. Сбор всех источников навыков (класс, раса, предыстория)
2. Расчет базовых бонусов от характеристик
3. Применение бонусов мастерства
4. Проверка на экспертизу (если применимо)
5. Выбор дополнительных навыков (если доступны)
6. Финальный расчет всех бонусов
7. Сохранение списка навыков

### Интеграция с архитектурой
```python
class SkillSelectionService:
    def __init__(self, abilities: AbilityScores, class_data: ClassData,
                 race_data: RaceData, background_data: BackgroundData):
        self.abilities = abilities
        self.class_data = class_data
        self.race_data = race_data
        self.background_data = background_data
    
    async def finalize_skills(self) -> SkillSet:
        # Реализация финализации навыков
        pass
```

### Тестирование
- Тесты расчета бонусов к навыкам
- Тесты учета всех источников
- Тесты выбора дополнительных навыков
- Тесты обработки экспертизы
