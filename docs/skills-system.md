# Система навыков D&D MUD

## Обзор

Система навыков представляет собой полноценную реализацию механики навыков D&D 5e, включая:

- **18 навыков** с привязкой к характеристикам
- **Спасброски** для всех 6 характеристик  
- **Мастерство и экспертиза** в навыках
- **Локализацию** на русский язык
- **Гибкую конфигурацию** через YAML

## Архитектура

### Основные компоненты

1. **`SkillConfig`** (`src/core/mechanics/skills.py`) - конфигурация навыка
2. **`Skill`** (`src/core/entities/skill.py`) - класс навыка персонажа
3. **`SkillsManager`** (`src/core/mechanics/skills.py`) - менеджер навыков
4. **`Character.skills`** - навыки персонажа с ленивой инициализацией

### Файлы конфигурации

- **`data/yaml/attributes/skills.yaml`** - основные навыки и спасброски
- **`data/yaml/localization/ru.yaml`** - локализация на русский язык

## Использование

### Создание персонажа с навыками

```python
from src.core.entities.character import Character

# Создаем персонажа
character = Character(name="Воин", level=5)

# Навыки создаются автоматически при первом обращении
skills = character.skills  # Ленивая загрузка всех 18 навыков
```

### Работа с навыками

```python
# Получение навыка
athletics = character.get_skill('athletics')
print(athletics.localized_name)  # "атлетика"

# Расчет бонуса навыка
bonus = character.get_skill_bonus('athletics')
print(f"Бонус атлетики: {bonus:+d}")  # Например: +5

# Добавление мастерства
character.add_skill_proficiency('athletics')
character.add_skill_expertise('perception')  # Двойной бонус

# Удаление мастерства
character.remove_skill_proficiency('athletics')
```

### Броски навыков и спасбросков

```python
# Бросок навыка
d20, total, crit_success, crit_fail = character.roll_skill_check('athletics')
print(f"Атлетика: d20={d20} + бонус={character.get_skill_bonus('athletics')} = {total}")

# Спасбросок
d20, total, crit_success, crit_fail = character.roll_saving_throw('strength')
print(f"Спасбросок Силы: {total}")
```

### Фильтрация навыков

```python
# Навыки по характеристике
strength_skills = character.get_skills_by_attribute('strength')
for name, skill in strength_skills.items():
    bonus = character.get_skill_bonus(name)
    print(f"{skill.localized_name}: {bonus:+d}")

# Все бонусы навыков
all_bonuses = character.get_all_skill_bonuses()
all_saves = character.get_all_save_bonuses()
```

## Конфигурация навыков

### Структура YAML файла

```yaml
skills:
  athletics:
    name: "athletics"           # Внутреннее имя
    display_name: "Атлетика"    # Отображаемое имя
    attribute: "strength"       # Связанная характеристика
    description: "Прыжки, плавание..."
    armor_penalty: true        # Штраф за броню

saving_throws:
  strength:
    name: "strength_save"
    display_name: "Спасбросок Силы"
    attribute: "strength"
    description: "Сопротивление силовым эффектам"
```

### Добавление нового навыка

1. Добавить навык в `skills.yaml`
2. Добавить локализацию в `ru.yaml`
3. Перезапустить приложение (конфиг загружается автоматически)

## Механика расчетов

### Бонус навыка

```
Бонус навыка = Модификатор характеристики + Бонус мастерства + Бонус экспертизы + Пользовательский бонус
```

- **Модификатор характеристики**: `(значение - 10) // 2`
- **Бонус мастерства**: `1 + (уровень // 4)` (+2 на 1-4 уровне, +3 на 5-8, и т.д.)
- **Бонус экспертизы**: Обычно двойной бонус мастерства
- **Пользовательский бонус**: От предметов, заклинаний и т.д.

### Спасброски

```
Бонус спасброска = Модификатор характеристики + Бонус мастерства (если есть)
```

## Локализация

### Поддерживаемые языки

- **Русский** (`ru`) - основной язык
- Расширение на другие языки через добавление YAML файлов

### Структура локализации

```yaml
skills:
  athletics:
    name: "атлетика"
    description: "Прыжки, плавание..."

saving_throws:
  strength_save:
    name: "спасбросок силы"
    description: "Сопротивление силовым эффектам"
```

## Примеры использования

### Пример 1: Создание следопыта

```python
ranger = Character(name="Элара", level=3)
ranger.dexterity.value = 16
ranger.wisdom.value = 14

# Добавляем мастерство следопыта
ranger.add_skill_proficiency('stealth')
ranger.add_skill_proficiency('perception')
ranger.add_skill_proficiency('survival')

# Проверяем бонусы
print(f"Скрытность: {ranger.get_skill_bonus('stealth'):+d}")  # +5 (2+3)
print(f"Восприятие: {ranger.get_skill_bonus('perception'):+d}")  # +4 (2+2)
print(f"Выживание: {ranger.get_skill_bonus('survival'):+d}")    # +4 (2+2)
```

### Пример 2: Бросок с преимуществом

```python
# TODO: Реализовать механику advantage/disadvantage
d20, total, crit_success, crit_fail = ranger.roll_skill_check(
    'stealth', advantage='advantage'
)
```

## Расширение системы

### Добавение новых характеристик бонусов

1. Расширить `Skill` класс новыми полями
2. Обновить YAML конфигурацию
3. Модифицировать методы расчета бонусов

### Интеграция с классами и расами

```python
# TODO: Добавить мастерство от класса
def apply_class_proficiencies(self):
    """Применяет мастерство от класса персонажа."""
    for skill_name in self.character_class.skill_proficiencies:
        self.add_skill_proficiency(skill_name)
```

## Тестирование

Запуск тестов системы навыков:

```bash
python test_skills.py
```

Тест проверяет:
- Загрузку всех 18 навыков
- Расчет бонусов
- Мастерство и экспертизу
- Броски навыков и спасбросков
- Локализацию

## Спасброски

### Механика спасбросков

Спасброски отражают попытку персонажа сопротивляться заклинанию, ловушке, яду, болезни или другой угрозе. В отличие от навыков, спасброски обычно инициируются внешними эффектами.

### Расчет бонуса спасброска

```
Бонус спасброска = Модификатор характеристики + Бонус мастерства (если есть владение)
```

### Владение спасбросками

Классы дают владение как минимум двумя спасбросками:
- **Воин**: Сила, Телосложение
- **Волшебник**: Интеллект, Мудрость  
- **Жрец**: Мудрость, Харизма
- **Плут**: Ловкость, Интеллект
- **Следопыт**: Сила, Ловкость
- **Паладин**: Мудрость, Харизма

### Использование спасбросков

```python
# Обычный спасбросок
d20, total, crit_success, crit_fail = character.roll_saving_throw('strength')

# С преимуществом/помехой
d20, total, crit_success, crit_fail = character.roll_saving_throw(
    'dexterity', advantage='advantage'
)

# С ситуационным бонусом
d20, total, crit_success, crit_fail = character.roll_saving_throw(
    'constitution', situational_bonus=2
)

# Управление владениями
character.add_save_proficiency('wisdom')  # Добавить владение
character.has_save_proficiency('wisdom')  # Проверить владение
character.remove_save_proficiency('wisdom')  # Удалить владение
```

### Сложность спасброска заклинания

Для заклинаний рассчитывается СЛ (Сложность):

```python
# СЛ = 8 + мод. характеристики заклинателя + бонус мастерства
spell_dc = wizard.calculate_spell_save_dc('intelligence')

# Заставить цель совершить спасбросок
save_dc, roll_result, save_success = wizard.make_target_save(
    target_character, 'intelligence'
)
```

### Преимущества и помехи

```python
# Преимущество - бросаем 2d20 и берем лучший
d20, total, _, _ = character.roll_saving_throw('dexterity', advantage='advantage')

# Помеха - бросаем 2d20 и берем худший  
d20, total, _, _ = character.roll_saving_throw('dexterity', advantage='disadvantage')
```

## Будущие улучшения

- [x] Advantage/Disadvantage механика
- [x] Владение спасбросками от классов
- [x] Сложность спасброска заклинаний
- [x] Ситуационные бонусы/штрафы
- [ ] Штрафы за броню для некоторых навыков
- [ ] Мастерство от рас
- [ ] Временные бонусы от заклинаний
- [ ] Пассивные проверки навыков
- [ ] Групповые проверки навыков
