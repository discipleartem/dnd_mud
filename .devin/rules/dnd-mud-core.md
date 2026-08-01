---
description: dnd_mud core/ui — слои, локализация, D&D механика
globs: "core/**,ui/**,main.py"
alwaysApply: false
---

# dnd_mud core and UI

Стиль и тесты: `dnd-mud-python.md`, `dnd-mud-tests.md`. Данные: `dnd-mud-data.md`.

## Слои

```
ui/  →  core/  →  database/ (YAML) + saves/ (JSON)
```

- **UI** (`ui/menus/`, `ui/input_handler.py`) — отображение и ввод; без бизнес-логики
- **Core** (`core/`) — модели, механика, загрузчики; не зависит от UI
- **Data** — core читает/пишет через свои модули (`core/platform/io.py`, loaders)

UI не читает и не пишет файлы данных напрямую.

## Локализация

Все пользовательские строки — через локализацию:

```python
from core.platform.localization import get_string, load_strings

strings = load_strings(language)
message = get_string(strings, "menu.new_game")  # ✅
message = "New Game"                            # ❌
```

Ключи: dot notation (`menu.new_game`). Обновлять `database/strings/ru.yaml` и `en.yaml` синхронно.

## D&D механика

Поиск правил — [`00-project.md`](00-project.md) §D&D 5e — источник истины и поиск правил (`docs/rules/` → веб, 5e до 2024).

- Модели в `core/character/models.py` — `dataclass` для `Character`, `Adventure`
- `class_id: CharacterClass` на `Character` (`core/types.py`, `StrEnum`); legacy JSON с `str` нормализуется в `__post_init__`
- Баланс из YAML — без magic numbers в Python
- Явные проверки условий; эффекты apply/remove явно
- Импорты в `core/` — leaf-only (`core.<pkg>.<module>`); пакетные `__init__.py` без фасадов
