# Система штрафов для навыков

## Обзор

Новая система штрафов заменяет старый атрибут `armor_penalty` на более гибкий атрибут `penalties`, который позволяет задавать список различных штрафов для каждого навыка.

## Структура

### YAML конфигурация

```yaml
skills:
  athletics:
    name: "athletics"
    display_name: "Атлетика"
    attribute: "strength"
    description: "Прыжки, плавание, лазание, силовые проверки"
    penalties: ["armor"]  # Штраф за броню
    
  arcana:
    name: "arcana"
    display_name: "Магия"
    attribute: "intelligence"
    description: "Знания о магических предметах, заклинаниях, существах"
    penalties: []  # Нет штрафов
```

### Возможные значения penalties

- `[]` - нет штрафов
- `["armor"]` - штраф за броню
- `["magic"]` - штраф за магические эффекты
- `["armor", "magic"]` - множественные штрафы
- Любые другие типы штрафов по мере необходимости

## Использование в коде

### Проверка штрафов

```python
from core.entities.skill import Skill

skill = Skill("athletics")

# Проверить наличие конкретного штрафа
has_armor_penalty = skill.has_penalty("armor")  # True
has_magic_penalty = skill.has_penalty("magic")  # False

# Получить список всех штрафов
penalties = skill.get_penalties()  # ["armor"]
```

### Расчёт бонусов с учётом штрафов

```python
# Характеристики персонажа
attributes = {"strength": 16, "dexterity": 14}
proficiency_bonus = 2

# Штрафы (например, от брони и заклинаний)
penalties = {
    "armor": -2,  # Штраф за тяжёлую бронь
    "magic": -1   # Штраф от проклятия
}

# Расчёт бонуса с учётом штрафов
total_bonus = skill.calculate_total_bonus(attributes, proficiency_bonus, penalties)
```

## Преимущества новой системы

1. **Гибкость** - можно добавлять любые типы штрафов
2. **Расширяемость** - легко добавить новые штрафы без изменения кода
3. **Комбинируемость** - можно применять несколько штрафов одновременно
4. **Обратная совместимость** - старый функционал сохранён через `penalties: ["armor"]`

## Миграция со старой системы

Старый формат:
```yaml
armor_penalty: true
```

Новый формат:
```yaml
penalties: ["armor"]
```

Старый формат:
```yaml
armor_penalty: false
```

Новый формат:
```yaml
penalties: []
```

## Примеры использования

### Навык с множественными штрафами
```yaml
stealth:
  name: "stealth"
  display_name: "Скрытность"
  attribute: "dexterity"
  description: "Скрытие, передвижение незаметно"
  penalties: ["armor", "noise"]  # Штраф за броню и шум
```

### Навык без штрафов
```yaml
persuasion:
  name: "persuasion"
  display_name: "Убеждение"
  attribute: "charisma"
  description: "Убеждение, переговоры, влияние на решения"
  penalties: []  # Нет штрафов
```

## API

### Skill

- `has_penalty(penalty_type: str) -> bool` - проверяет наличие штрафа
- `get_penalties() -> List[str]` - возвращает список штрафов
- `calculate_total_bonus(attributes, proficiency_bonus, penalties=None) -> int` - расчёт с учётом штрафов

### SkillsManager

- `has_penalty(skill_name: str, penalty_type: str) -> bool` - проверяет штраф для навыка
- `get_penalties(skill_name: str) -> List[str]` - возвращает штрафы навыка
