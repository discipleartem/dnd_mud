# API Reference — dnd_mud Core

## core.character — Модель персонажа

### Character

```python
@dataclass
class Character:
    name: str
    race: str
    class_name: str
    level: int = 1
    stats: dict[str, int] = field(default_factory=dict)
    current_hp: int = 0
    experience: int = 0
```

**Методы:**
- `to_dict() -> dict[str, Any]` — сериализация в словарь для YAML
- `from_dict(data: dict[str, Any]) -> Character` — десериализация из словаря
- `_calculate_hp() -> int` — расчёт хитов 1-го уровня (con_mod)

### Константы

```python
STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]  # Стандартный массив D&D 5e
STAT_NAMES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
CHARACTERS_FILE = Path("database/characters.yaml")
RACES_FILE = Path("database/races.yaml")
CLASSES_FILE = Path("database/classes.yaml")
```

### Функции

```python
# Создание и сохранение
create_character(name, race_id, class_id) -> Character
character_exists(name) -> bool

# Загрузка данных
load_characters() -> list[Character]
save_characters(characters: list[Character]) -> None
load_races() -> list[dict]
load_classes() -> list[dict]

# Характеристики
get_race_bonuses(race_id) -> dict[str, int]
generate_stats(race_id) -> dict[str, int]
ability_modifier(score) -> int
get_stat_display_name(stat_key, loc=None) -> str
```

### Примеры

```python
# Создание
char = create_character("Арагорн", "human", "fighter")
print(char.name, char.stats)

# Загрузка
chars = load_characters()
for c in chars:
    print(c.name, c.level)

# Проверка существования
if character_exists("Арагорн"):
    print("Персонаж существует")

# Генерация характеристик с расовыми бонусами
stats = generate_stats("elf")
# {'strength': 8, 'dexterity': 17, 'constitution': 13, 'intelligence': 14, 'wisdom': 12, 'charisma': 10}
```

---

## core.dice — Броски кубиков

### Типы

```python
DiceType = Literal[4, 6, 8, 10, 12, 20, 100]
```

### Функции

```python
roll(count=1, sides=20, modifier=0) -> int
roll_d20(advantage=False, disadvantage=False) -> int
roll_with_mods(count, sides, modifier, advantage, disadvantage) -> tuple[int, list[int]]
ability_modifier(score) -> int
critical_hit(extra_dice=0) -> tuple[int, list[int]]
```

### Исключения

- `ValueError` — если указаны и advantage, и disadvantage одновременно

### Примеры

```python
# Бросок 1к20
result = roll_d20()
print(f"Результат: {result}")

# Бросок с преимуществом
result = roll_d20(advantage=True)

# Бросок 2к6+3
result = roll(2, 6, 3)
print(f"Урон: {result}")

# Модификатор характеристики
mod = ability_modifier(18)  # 4

# Критическое попадание
total, rolls = critical_hit(extra_dice=2)
print(f"Крит: {total}, броски: {rolls}")

# Детальный бросок с помехой
total, rolls = roll_with_mods(1, 20, 0, disadvantage=True)
```

---

## core.adventure — Приключения

### Константы

```python
ADVENTURES_FILE = Path("database/adventures.yaml")
```

### Функции

```python
load_adventures() -> list[dict]
get_adventure_display_name(adventure, language='ru') -> str
get_adventure_difficulty_name(difficulty, language='ru') -> str
```

### Примеры

```python
adventures = load_adventures()
for adv in adventures:
    name = get_adventure_display_name(adv, 'ru')
    diff = get_adventure_difficulty_name(adv['difficulty'], 'ru')
    print(f"{name} ({diff})")
```

---

## core.localization — Локализация

### Класс Localization

```python
loc = Localization(language='ru')

# Использование
text = loc('menu.new_game')  # "Новая игра"
text = loc('welcome.version', version='0.1.0')  # "Версия: 0.1.0"

# Переключение языка
loc.load('en')
text = loc('menu.new_game')  # "New Game"

# Свойства
print(loc.language)  # 'en' — текущий язык
```

**Методы:**
- `load(language: str) -> None` — загрузить YAML-словарь для языка + fallback en
- `get(key: str, **kwargs) -> str` — получить строку по ключу (точечная нотация)
- `__call__(key: str, **kwargs) -> str` — сокращённый вызов

**Формат ключей:** точечная нотация для вложенных словарей.

```
'database/strings/ru.yaml':
  menu:
    new_game: "Новая игра"
    exit: "Выход"

loc('menu.new_game') -> "Новая игра"
```

**Fallback:** если ключ не найден в текущем языке, поиск идёт в английском словаре. Если не найдено — возвращается сам ключ.

---

## core.settings — Настройки

### Класс Settings

```python
settings = Settings()

# Загрузка/сохранение
settings.load()
settings.save()

# Удобный конструктор
settings = Settings.from_file()

# Доступ к полям
settings.language = 'en'
settings.hardcore = True

# Преобразование
data = settings.to_dict()  # {'language': 'en', 'hardcore': True}
```

**Поля:**
- `language: str` — код языка ('ru' по умолчанию)
- `hardcore: bool` — режим Hard Core (False по умолчанию)
- `_loaded: bool` — флаг загрузки

**Константы:**
```python
DEFAULT_LANGUAGE = "ru"
SETTINGS_PATH: Path = Path.cwd().resolve() / "database" / "settings.yaml"
```

---

## core.mod_loader — Моды

### Константы

```python
MODS_DIR = Path("mods")
MODS_STATE_FILE = Path("database/mods_state.yaml")
```

### Функции

```python
scan_mods() -> list[dict]
load_mods_state() -> dict[str, bool]
save_mods_state(state: dict[str, bool]) -> None
toggle_mod(mod_name) -> bool
is_mod_enabled(mod_name) -> bool
```

### Формат мода

```yaml
name: "Новая раса - Драконорожденный"
version: "1.0"
type: "addon"   # addon — добавляет новые данные, mod — изменяет
description: "Добавляет расу Dragonborn"
files:
  - target: "database/races.yaml"
    action: "append"   # append, replace, delete
    data:
      - id: dragonborn
        name:
          ru: "Драконорожденный"
          en: "Dragonborn"
        ability_bonuses:
          str: 2
          cha: 1
```

---

## core.game_engine — Игровой движок

### Класс GameEngine

```python
engine = GameEngine(character_dict, adventure_dict)

engine.process_command("help")           # -> str
engine.process_command("stats")          # -> str (характеристики)
engine.process_command("exit")           # -> str, engine.running = False
engine.ability_check("strength", dc=15)  # -> (success, total, desc)
```

**Поля:**
- `character: dict[str, Any]` — данные персонажа (словарь)
- `adventure: dict[str, Any]` — данные приключения
- `running: bool` — флаг работы цикла
- `current_node: str` — текущий узел сценария (по умолчанию "start")

**Примечание:** Движок пока в базовой стадии. Полноценный цикл приключений будет добавлен в следующих версиях.

---


---

## ui.input_handler — Ввод

### Функции

```python
get_int_input(prompt, min_val, max_val, loc=None) -> int
get_str_input(prompt, min_length=1, validator=None, error_msg='') -> str
get_choice(options, prompt, back_option=False, back_label='', loc=None) -> int
```

### Примеры

```python
# Числовой ввод
choice = get_int_input("Выберите [1-8]: ", 1, 8)

# Строковый ввод
name = get_str_input("Введите имя: ", min_length=2)

# Выбор из списка
idx = get_choice(["Да", "Нет"], "Ваш выбор: ")

# Выбор с пунктом "Назад"
idx = get_choice(["Опция A", "Опция B"], "Выберите: ", back_option=True, back_label="Назад")
```

**Возвращаемое значение `get_choice`:**
- 0-based индекс выбранной опции (0 = первый элемент)
- `-1` если `back_option=True` и пользователь выбрал пункт 0

---

## main.py — Точка входа

### Константы

```python
VERSION = "0.1.0"
```

### Функции

```python
main() -> int                                     # Запуск игры
handle_menu_choice(choice, loc, settings)         # Обработка выбора меню
_handle_settings(loc, settings)                   # Обработка настроек
```

### Текущие пункты главного меню

| № | Пункт | Описание |
|---|-------|----------|
| 1 | Настройки | Язык и Hard Core режим |
| 2 | Выход | Завершение программы |

> **Примечание:** Пока реализованы только 2 пункта из 8 запланированных.
> Остальные пункты (Новая игра, Создать персонажа, Languages, Модификации, Приключения)
> будут добавлены в следующих итерациях.