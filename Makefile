# Makefile для DnD MUD проекта
# Поддержка виртуального окружения и стандартных операций

.PHONY: help check clean coverage install test

# Переменные
PYTHON := python3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
PYTEST := $(VENV_PYTHON) -m pytest

# Цвета для вывода
GREEN := \033[0;32m
BLUE := \033[0;34m
RED := \033[0;31m
YELLOW := \033[1;33m
NC := \033[0m  # No Color

# Директории для очистки
CLEAN_DIRS := __pycache__ *.egg-info *.egg .pytest_cache .mypy_cache .ruff_cache htmlcov
CLEAN_FILES := *.pyc *.pyo *.pyd *.py~ .coverage

help: ## Показать доступные команды
	@echo "$(BLUE)DnD MUD - Доступные команды:$(NC)"
	@echo ""
	@echo "$(GREEN)Основные команды:$(NC)"
	@echo "  install                Установить зависимости в виртуальное окружение"
	@echo "  test                   Запустить все тесты"
	@echo "  coverage               Запустить тесты с покрытием"
	@echo "  check                  Проверка black, ruff, mypy"
	@echo "  clean                  Очистить временные файлы"
	@echo "  help                   Показать доступные команды"

install: ## Установить зависимости в виртуальное окружение
	@echo "$(BLUE)Установка зависимостей...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)Создание виртуального окружения...$(NC)"; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@echo "$(BLUE)Обновление pip...$(NC)"
	@$(VENV_PYTHON) -m pip install --upgrade pip
	@echo "$(BLUE)Установка зависимостей...$(NC)"
	@$(VENV_PYTHON) -m pip install -e .
	@echo "$(GREEN)Установка завершена$(NC)"

check: ## Проверка black, ruff, mypy
	@echo "$(BLUE)Проверка кода...$(NC)"
	@echo "$(BLUE)Black:$(NC)"
	@$(VENV_PYTHON) -m black --check src/ tests/
	@echo "$(BLUE)Ruff:$(NC)"
	@$(VENV_PYTHON) -m ruff check src/ tests/
	@echo "$(BLUE)MyPy:$(NC)"
	@$(VENV_PYTHON) -m mypy src/
	@echo "$(GREEN)Проверка завершена$(NC)"

test: ## Запустить все тесты
	@echo "$(BLUE)Запуск всех тестов...$(NC)"
	@$(PYTEST) tests/ -v

coverage: ## Запустить тесты с покрытием
	@echo "$(BLUE)Запуск тестов с покрытием...$(NC)"
	@$(VENV_PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term

clean: ## Очистить временные файлы
	@echo "$(BLUE)Очистка...$(NC)"
	@for dir in $(CLEAN_DIRS); do \
		find . -type d -name "$$dir" -exec rm -rf {} + 2>/dev/null || true; \
	done
	@for file in $(CLEAN_FILES); do \
		find . -type f -name "$$file" -delete; \
	done
	@echo "$(GREEN)Очистка завершена$(NC)"
