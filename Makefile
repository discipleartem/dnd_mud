# Makefile для D&D MUD - основные команды
.PHONY: help check-all test test-coverage install-dev clean

# Переменные
VENV := .venv
PYTHON := $(VENV)/bin/python
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy

# Цвета
BLUE := \033[0;34m
YELLOW := \033[1;33m
NC := \033[0m

help: ## Показать справку
	@echo "$(BLUE)D&D MUD - основные команды$(NC)"
	@echo "$(YELLOW)make check-all    Black + Ruff + MyPy$(NC)"
	@echo "$(YELLOW)make test         Запустить все тесты$(NC)"
	@echo "$(YELLOW)make test-coverage Тесты с покрытием$(NC)"
	@echo "$(YELLOW)make install-dev  Установка зависимостей$(NC)"
	@echo "$(YELLOW)make clean        Очистка временных файлов$(NC)"

check-venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)Создание виртуального окружения...$(NC)"; \
		python3 -m venv $(VENV); \
	fi

check-all: check-venv ## Black + Ruff + MyPy
	@echo "$(BLUE)� Полная проверка кода$(NC)"
	@echo "$(YELLOW)1/3 Black - форматирование$(NC)"
	$(BLACK) src/
	@echo "$(YELLOW)2/3 Ruff - проверка стиля$(NC)"
	$(RUFF) check src/
	@echo "$(YELLOW)3/3 MyPy - проверка типов$(NC)"
	$(MYPY) src/

test: check-venv ## Запустить все тесты
	@echo "$(BLUE)🧪 Запуск всех тестов$(NC)"
	$(PYTEST) tests/ -v

test-coverage: check-venv ## Тесты с покрытием
	@echo "$(BLUE)🧪 Запуск тестов с покрытием$(NC)"
	$(PYTEST) tests/ --cov=src --cov-report=term-missing

install-dev: ## Установка зависимостей
	@echo "$(BLUE)📦 Установка зависимостей$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
	fi
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -e ".[dev]"

clean: ## Очистка временных файлов
	@echo "$(BLUE)🧹 Очистка$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
