# Python 3.12 — справочник для dnd_mud

Краткий обзор возможностей **Python 3.12** (релиз 2 октября 2023) для разработчиков проекта dnd_mud. Проект требует Python ≥ 3.12 (`pyproject.toml`, `requires-python`); toolchain настроен на `py312` (ruff, black, mypy).

Полный канон — официальный документ [What's New In Python 3.12](https://docs.python.org/3/whatsnew/3.12.html) и [PEP 693 — Release Schedule](https://peps.python.org/pep-0693/).

## Аудитория

- **Разработчики dnd_mud** — какие фичи 3.12 доступны в коде и в инструментах.
- **Новые участники** — почему выбрана эта версия и на что обратить внимание при миграции с 3.11.

См. также: [DEVELOPMENT.md](DEVELOPMENT.md) (установка venv), [ARCHITECTURE.md](ARCHITECTURE.md) (слои проекта).

## Краткая сводка

| Область | PEP / изменение | Суть |
|---------|-----------------|------|
| Generics | [PEP 695](https://peps.python.org/pep-0695/) | Синтаксис `def f[T](...)` и `type Alias = ...` |
| f-strings | [PEP 701](https://peps.python.org/pep-0701/) | Любые выражения внутри `{}`, вложенные кавычки |
| Comprehensions | [PEP 709](https://peps.python.org/pep-0709/) | Инлайн list/dict/set comprehensions (~до 2× быстрее) |
| Типизация `**kwargs` | [PEP 692](https://peps.python.org/pep-0692/) | `Unpack[TypedDict]` для именованных kwargs |
| Override | [PEP 698](https://peps.python.org/pep-0698/) | Декоратор `@override` для type checker'ов |
| Мониторинг | [PEP 669](https://peps.python.org/pep-0669/) | `sys.monitoring` — низкозатратные хуки для отладчиков |
| Buffer protocol | [PEP 688](https://peps.python.org/pep-0688/) | `__buffer__`, `collections.abc.Buffer` |
| Per-interpreter GIL | [PEP 684](https://peps.python.org/pep-0684/) | Отдельный GIL на sub-interpreter (пока C-API) |
| Удалено | [PEP 632](https://peps.python.org/pep-0632/) | Пакет `distutils` из stdlib |
| Производительность | — | Оценка ~5% ускорения; BOLT, инлайн comprehensions |

---

## Синтаксис языка

### PEP 695: параметры типов и `type`

Компактное объявление generic-функций, классов и псевдонимов типов без `TypeVar` в отдельной строке:

```python
def first[T](items: list[T]) -> T:
    return items[0]


class Stack[T]:
    def push(self, item: T) -> None: ...


type StatMap = dict[str, int]
type Point[T] = tuple[T, T]
```

Параметры типа видны в области объявления и вложенных scope, но не в модуле после класса/функции. Оценка bounds/constraints — ленивая (можно ссылаться на типы, объявленные ниже по файлу).

**В dnd_mud:** пока используется классический стиль `list[str]`, `dict[str, int]`, `str | None` (PEP 604, доступен с 3.10). PEP 695 — опциональное упрощение для новых generic-абстракций.

### PEP 701: f-strings без прежних ограничений

В 3.11 нельзя было повторять кавычки f-string внутри `{}`, использовать `\` и многострочные выражения. В 3.12 — можно:

```python
name = "Арагорн"
# Повтор кавычек внутри выражения
msg = f"Персонаж: {name!r}"

# Многострочное выражение
lines = f"Статы:\n{chr(10).join(f'{k}: {v}' for k, v in stats.items())}"
```

Ошибки парсинга f-string точнее указывают позицию в строке.

**В dnd_mud:** UI-строки в основном из YAML (`database/strings/`); f-strings в коде — для форматирования и тестов. PEP 701 упрощает сложные inline-шаблоны без конкатенации.

### Прочие изменения языка

- **Улучшенные подсказки** при `NameError`, `ImportError`, `SyntaxError` («Did you mean …», забытый `import sys`, `self.attr` в методах).
- **`slice` хешируем** — можно использовать как ключ `dict` / элемент `set`.
- **`sum()` для float** — алгоритм Neumaier (точнее и коммутативнее).
- **Невалидные escape** в обычных строках (`"\d"`) → `SyntaxWarning` (в будущем станет `SyntaxError`); для regex — raw-строки `r"\d"`.
- **Источник с `null` байтами** → `SyntaxError` (раньше в `ast.parse` был `ValueError`).

---

## Типизация (typing)

### PEP 692: TypedDict для `**kwargs`

```python
from typing import TypedDict, Unpack


class SaveOptions(TypedDict, total=False):
    subrace_id: str
    stats: dict[str, int]


def save_character(name: str, **options: Unpack[SaveOptions]) -> None: ...
```

Позволяет описать имена и типы kwargs, а не один общий тип для всех.

### PEP 698: `@override`

```python
from typing import override


class BaseMenu:
    def run(self) -> None: ...


class MainMenu(BaseMenu):
    @override
    def run(self) -> None: ...
```

mypy/ruff (UP) могут ловить опечатки в имени переопределяемого метода.

### Прочее

- `isinstance()` против runtime-checkable `Protocol` — быстрее (2–20× в типичных случаях), иная семантика lookup атрибутов (`getattr_static` вместо `hasattr`).
- У `TypedDict` / `NamedTuple` появился `__orig_bases__`.

**В dnd_mud:** `mypy` с `python_version = "3.12"`, `strict = true` в `pyproject.toml`. Аннотации в стиле 3.10+ (`X | Y`, builtin generics `list[str]`).

---

## Производительность и интерпретатор

| Механизм | Эффект |
|----------|--------|
| PEP 709 — инлайн comprehensions | До ~2× на list/dict/set comprehensions |
| BOLT (опционально при сборке CPython) | +1–5% на бинарник |
| `LOAD_SUPER_ATTR`, оптимизации `asyncio` | Ускорение отдельных hot path |
| Удаление `wstr` у `str` (PEP 623) | −8 байт на объект строки (C-уровень) |
| tokenize (PEP 701) | До +64% на `tokenize.tokenize()` |

**В dnd_mud:** comprehensions и генераторы активно в `core/stats.py`, загрузчиках YAML; выигрыш PEP 709 — автоматический, без изменений кода.

### PEP 669: `sys.monitoring`

API для профайлеров и coverage с оплатой «только за подписанные события». Модуль `sys.monitoring` — альтернатива тяжёлым глобальным trace-хукам.

### Linux `perf`

Флаги `-X perf`, переменная `PYTHONPERFSUPPORT`, функции `sys.activate_stack_trampoline()` — имена Python-функций в трассах `perf`.

---

## Стандартная библиотека (выборочно)

Полный список — в [What's New § Improved Modules](https://docs.python.org/3/whatsnew/3.12.html#improved-modules).

| Модуль | Новое / важное |
|--------|----------------|
| `itertools` | `itertools.batched()` — чанки фиксированного размера |
| `pathlib` | `Path.walk()`, подклассы `PurePath`/`Path`, `is_junction()` |
| `sqlite3` | CLI, `autocommit`, `getconfig`/`setconfig` |
| `uuid` | CLI |
| `tarfile` / `shutil` | Фильтры извлечения (PEP 706) — безопасность path traversal |
| `asyncio` | Eager tasks, быстрее сокеты, `loop_factory` в `asyncio.run()` |
| `math` | `sumprod()`, расширенный `nextafter()` |
| `statistics` | `correlation(..., method="ranked")` — ранговая корреляция |
| `sys` | `sys.last_exc` (вместо устаревших `last_type`/`last_value`/`last_traceback`) |
| `threading` | `settrace_all_threads()`, `setprofile_all_threads()` |
| `venv` | `setuptools` **не** предустанавливается — нужен `pip install setuptools` при необходимости |

**В dnd_mud:** `pathlib` (`saves/`, `database/`), `json`, `yaml` (PyYAML), `dataclasses` — без asyncio в runtime. `itertools.batched` пригоден для пакетной обработки списков в UI/engine.

---

## Удаления и deprecations

| Что | Замена / действие |
|-----|-------------------|
| `distutils` | `setuptools` или современная упаковка (`pyproject.toml`) |
| `asynchat`, `asyncore`, `imp` | Удалены |
| Ряд алиасов `unittest.TestCase` | Удалены (deprecated с 3.1–3.2) |
| `smtpd` | Удалён (PEP 594) |
| `wstr` в C-API Unicode | Удалён (PEP 623) |

Проект собирается через **setuptools** (`[build-system]` в `pyproject.toml`) — удаление `distutils` не затрагивает dnd_mud.

---

## Что уже использует dnd_mud

Синтаксис и типы, задействованные в кодовой базе (не обязательно уникальные для 3.12, но закреплённые минимальной версией):

```python
# PEP 604 — union types
def adventure_unavailable_reason(...) -> str | None: ...

# PEP 585 — builtin generics
stats: dict[str, int] = field(default_factory=dict)
characters: list[Character] = load_characters()

# match / case — доступен с 3.10; в проекте по необходимости
```

Конфигурация инструментов под 3.12:

```toml
# pyproject.toml
requires-python = ">=3.12"

[tool.mypy]
python_version = "3.12"

[tool.ruff]
target-version = "py312"

[tool.black]
target-version = ["py312"]
```

---

## Рекомендации для разработки

1. **venv на 3.12:** `python3.12 -m venv .venv` (см. [DEVELOPMENT.md](DEVELOPMENT.md)).
2. **Не полагаться на distutils** в скриптах и CI.
3. **Regex** — только raw-строки `r"..."`, чтобы избежать `SyntaxWarning` на невалидных escape.
4. **Новый generic-код** — можно постепенно вводить PEP 695 (`type`, `class Foo[T]`) там, где это читабельнее `TypeVar`.
5. **Проверка:** `make check` (ruff + black + mypy) и `make test` после изменений типов и синтаксиса.

---

## Ссылки

- [What's New In Python 3.12](https://docs.python.org/3/whatsnew/3.12.html) — полный обзор
- [Python 3.12 Release Notes](https://docs.python.org/3/whatsnew/changelog.html#python-3-12-0) — changelog
- [Porting to Python 3.12](https://docs.python.org/3/whatsnew/3.12.html#porting-to-python-3-12) — миграция с 3.11
- [PEP index — 3.12](https://peps.python.org/topic/3.12/) — все PEP релиза
