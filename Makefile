# Makefile для D&D Text MUD
# Простая версия - только самое необходимое

.PHONY: help install test lint run clean

PYTHON := python3
VENV := .venv
PYTHON_VENV := $(VENV)/bin/python

help: ## Показать справку
	@echo "D&D Text MUD - Makefile"
	@echo ""
	@echo "Доступные команды:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Установить зависимости
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	$(VENV)/bin/pip install -e ".[dev]"

test: ## Запустить тесты
	$(VENV)/bin/pytest tests/ -v

lint: ## Проверить стиль кода
	$(VENV)/bin/ruff check src/ tests/
	$(VENV)/bin/mypy src/ tests/

run: ## Запустить приложение
	PYTHONPATH=src $(VENV)/bin/python src/main.py

clean: ## Очистить временные файлы
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
