# 2. Генерация характеристик

## Обзор

Второй этап - генерация шести основных характеристик персонажа D&D 5e с учетом расовых бонусов от предыдущего этапа.

## Задачи

### TASK-3.4.1: Сервис характеристик (AbilitiesService)

**Цель:** Генерация и расчет характеристик персонажа

**Функциональность:**
- Три метода генерации характеристик
- Расчет модификаторов способности
- Применение расовых бонусов
- Валидация характеристик

**Структура данных:**
```python
@dataclass
class Abilities:
    strength: int = 10
    dexterity: int = 10  
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    def get_modifier(self, ability: str) -> int:
        """Расчет модификатора: (ability - 10) // 2"""
        value = getattr(self, ability.lower())
        return (value - 10) // 2

class GenerationMethod(Enum):
    STANDARD = "standard"      # 4d6 drop lowest
    POINT_BUY = "point_buy"    # 27 points
    RANDOM = "random"          # 3d6 for each
```

**Методы:**
- `generate_standard() -> Abilities` - 4d6 drop lowest для каждой характеристики
- `generate_point_buy(points: int = 27) -> Abilities` - распределение очков
- `generate_random() -> Abilities` - 3d6 для каждой характеристики
- `apply_race_bonuses(abilities: Abilities, race_bonuses: Dict[str, int]) -> Abilities`
- `calculate_modifiers(abilities: Abilities) -> Dict[str, int]`
- `validate_abilities(abilities: Abilities) -> bool`

### TASK-3.4.2: UI характеристик (AbilitiesGenerationAdapter)

**Цель:** Интерфейс выбора метода генерации и визуализации результатов

**Функциональность:**
- Интерактивный выбор метода генерации
- Визуализация результатов и модификаторов
- Валидация сумм и ограничений
- Интеграция с расовыми бонусами

**UI Flow:**
1. Выбор метода генерации:
   - **Standard:** Показать dice rolls для каждой характеристики
   - **Point Buy:** Интерактивное распределение 27 очков
   - **Random:** Показать результаты 3d6
2. Отображение базовых значений + расовые бонусы
3. Показ финальных значений и модификаторов
4. Подтверждение результатов

**Point Buy Interface:**
- Таблица характеристик с текущими значениями
- Кнопки +1/-1 для каждой характеристики
- Счетчик оставшихся очков
- Мин/макс значения (8-15 стандартно)

## Зависимости

- RaceService для получения расовых бонусов
- CharacterCreationService для координации
- Система random для генерации

## Правила D&D 5e

- **Standard:** 4d6, отбрасываем наименьший, повторяем 6 раз
- **Point Buy:** 27 очков, стоимость зависит от значения (8=0, 14=7)
- **Модификаторы:** (значение - 10) // 2
- **Мин/макс:** 3-18 (естественные ограничения)

## Следующий этап

Выбор класса с учетом сгенерированных характеристик.
