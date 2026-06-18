.PHONY: help venv-recreate venv install reinstall clean check test

# -------------------------------------------
# Переменные
# -------------------------------------------
VENV      := .venv
PYTHON    := python3.12
PIP       := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python

# -------------------------------------------
# Виртуальное окружение
# -------------------------------------------

$(VENV)/bin/python:
	$(PYTHON) -m venv $(VENV)

.PHONY: venv
venv: $(VENV)/bin/python

.PHONY: venv-recreate
venv-recreate:
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)

# -------------------------------------------
# Установка зависимостей
# -------------------------------------------

.PHONY: install
install: venv
	$(PIP) install -e ".[dev]"

.PHONY: reinstall
reinstall:
	$(PIP) uninstall -y dnd_mud
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -e ".[dev]"

# -------------------------------------------
# Очистка
# -------------------------------------------

.PHONY: clean
clean:
	rm -rf .mypy_cache .ruff_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '*.pyo' -delete 2>/dev/null || true
	find . -type l -name '*.so' -delete 2>/dev/null || true

# -------------------------------------------
# Проверка кода
# -------------------------------------------

.PHONY: check
check: install
	@echo "=== ruff (fix) ==="
	$(VENV)/bin/ruff check --fix .
	@echo ""
	@echo "=== black ==="
	$(VENV)/bin/black .
	@echo ""
	@echo "=== mypy ==="
	$(VENV)/bin/mypy .

# -------------------------------------------
# Справка
# -------------------------------------------

.PHONY: help
help:
	@echo "Доступные команды:"
	@echo ""
	@echo "  make help            — показать эту справку"
	@echo "  make venv            — создать виртуальное окружение (если нет)"
	@echo "  make venv-recreate   — пересоздать виртуальное окружение"
	@echo "  make install         — установить/обновить зависимости"
	@echo "  make reinstall       — переустановить все зависимости (с удалением)"
	@echo "  make clean           — очистить кеш и временные файлы"
	@echo "  make check           — проверить и исправить код (ruff --fix + black + mypy)"
	@echo "  make test            — запустить тесты"


# -------------------------------------------
# Тесты
# -------------------------------------------

.PHONY: test
test: install
	$(VENV)/bin/pytest
