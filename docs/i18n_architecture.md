# Архитектура локализации (i18n)

## Обзор

Система локализации поддерживает модульную архитектуру, где каждый игровой модуль (расы, классы, навыки и т.д.) имеет собственный файл локализации, а UI элементы находятся в отдельной директории.

## Структура файлов

```
data/
├── races/
│   ├── races.yaml          # Данные рас (без *_key)
│   └── ru.yaml             # Локализация рас
├── classes/
│   ├── classes.yaml         # Данные классов (с *_key)
│   └── ru.yaml             # Локализация классов
├── skills/
│   ├── skills.yaml          # Данные навыков (без *_key)
│   └── ru.yaml             # Локализация навыков
├── backgrounds/
│   ├── backgrounds.yaml      # Данные предысторий
│   └── ru.yaml             # Локализация предысторий
├── abilities/
│   ├── abilities.yaml       # Данные характеристик
│   └── ru.yaml             # Локализация характеристик
├── sizes/
│   ├── sizes.yaml          # Данные размеров (без *_key)
│   └── ru.yaml             # Локализация размеров
├── languages/
│   ├── languages.yaml       # Данные языков (без *_key)
│   └── ru.yaml             # Локализация языков
└── i18n/
    ├── ru.yaml              # UI, меню, общие механики, диалоги
    └── en.yaml              # English UI and common elements
```

## Принципы работы

### 1. Разделение данных и локализации

- **Файлы данных** (`*.yaml`) содержат только игровые параметры:
  - Числовые значения
  - Механики
  - Списки
  - `*_key` ссылки на локализацию (где необходимо)

- **Файлы локализации** (`ru.yaml`) содержат переводы:
  - Названия и описания
  - UI тексты
  - Сообщения об ошибках
  - Диалоги

### 2. Использование ключей

```yaml
# В файле данных (data/classes/classes.yaml)
classes:
  fighter:
    name_key: "classes.fighter.name"
    description_key: "classes.fighter.description"

# В файле локализации (data/classes/ru.yaml)
classes:
  fighter:
    name: "Воин"
    description: "Мастер оружия и доспехов, эксперт в боевых искусствах."
```

### 3. Загрузка переводов

Система автоматически загружает:
1. Основной UI файл из `data/i18n/{lang}.yaml`
2. Модульные файлы из `data/{module}/{lang}.yaml`

## Примеры использования

### Базовый перевод

```python
from use_cases.i18n_manager import I18nManagerImpl
from pathlib import Path

# Инициализация
manager = I18nManagerImpl(Path("data"))
config = I18nConfig(default_language="ru")
manager.initialize(config)

# Получение переводчика
translator = manager.get_translator()

# Перевод строки
name = translator.translate("races.human.name")
description = translator.translate("races.human.description")
```

### Перевод с параметрами

```python
# В файле локализации
welcome_message: "Добро пожаловать, {name}!"

# В коде
message = translator.translate("welcome_message", name="Игрок")
# Результат: "Добро пожаловать, Игрок!"
```

### Перевод из модуля

```python
# Перевод названия расы
race_name = translator.translate("races.human.name")

# Перевод названия класса
class_name = translator.translate("classes.fighter.name")

# Перевод навыка
skill_name = translator.translate("skills.acrobatics.name")
```

## Интеграция с сущностями

### Character

```python
from entities.character import Character

character = Character(name="Воин")
character.set_translator(translator)

# Автоматическая локализация статуса
status = character.get_status()  # "Здоров", "Ранен" и т.д.
```

### User Interface

```python
from interfaces.user_interface import UserInterface

ui = UserInterface()
ui.set_translator(translator)

# Локализация UI элементов
title = ui.t("ui.main_menu.title")
new_game = ui.t("ui.main_menu.new_game")
```

## Добавление нового языка

1. Создать файл `data/i18n/{lang}.yaml` с UI переводами
2. Создать файлы `data/{module}/{lang}.yaml` для каждого модуля
3. Добавить язык в `get_available_languages()` метод

```python
# В SystemI18nDetector.get_available_languages()
languages["de"] = LanguageInfo("de", "German", "Deutsch")
```

## Валидация

Система включает валидацию:
- Проверка структуры YAML файлов
- Поиск отсутствующих ключей
- Валидация типов данных

```python
from use_cases.i18n_manager import DefaultI18nValidator

validator = DefaultI18nValidator()
missing_keys = validator.find_missing_keys(base_translations, target_translations)
```

## Кэширование

Переводы кэшируются для производительности:
- Автоматическая очистка кэша при перезагрузке
- Статистика использования кэша

## Автоопределение языка

Система автоматически определяет язык:
1. Из системной локали (`locale.getdefaultlocale()`)
2. Из переменных окружения (`LANG`, `LC_ALL`, `LC_MESSAGES`)
3. Fallback к языку по умолчанию

## Лучшие практики

1. **Используйте осмысленные ключи**: `races.human.name` вместо `race1`
2. **Группируйте переводы**: по модулям и функциональности
3. **Избегайте дублирования**: общие строки в `data/i18n/`
4. **Используйте параметры**: для динамического контента
5. **Тестируйте переводы**: проверьте все языки

## Тестирование

```python
# Запуск тестов локализации
pytest tests/test_i18n.py -v

# Проверка конкретного модуля
pytest tests/test_i18n.py::test_races_localization -v
```

Эта архитектура обеспечивает:
- ✅ Чистое разделение данных и локализации
- ✅ Масштабируемость для новых модулей
- ✅ Простоту добавления языков
- ✅ Эффективную загрузку и кэширование
- ✅ Гибкую систему переводов с параметрами
