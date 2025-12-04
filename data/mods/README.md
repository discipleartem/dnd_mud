# Моды для DnD MUD Game

Эта директория предназначена для пользовательских модификаций игры.

## Структура мода

Каждый мод должен быть в отдельной поддиректории и содержать файл `mod.yaml`:

```
data/mods/
└── my_awesome_mod/
    ├── mod.yaml          # Метаданные мода
    ├── items.yaml        # Новые предметы (опционально)
    ├── quests.yaml       # Новые квесты (опционально)
    └── scripts/          # Скрипты мода (опционально)
```

## Пример mod.yaml

```yaml
name: "My Awesome Mod"
version: "1.0.0"
author: "Your Name"
description: "Описание мода"
compatible_version: "0.1.0"  # Минимальная версия игры

# Что добавляет мод
adds:
  items: true
  quests: true
  locations: false
```

## Разработка модов

Документация по API для создания модов будет доступна позже.