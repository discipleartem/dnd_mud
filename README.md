# DnD MUD (переписывание с 0)

Текстовая однопользовательская MUD-игра на Python 3.13+ по мотивам D&D 5e (2023).

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

dnd-mud
```

## Структура

```
src/           # код игры
data/          # контент (yaml/json) и пользовательские расширения
tests/         # pytest
.cursor/       # правила Cursor/агентов (оставляем в репозитории)
```

