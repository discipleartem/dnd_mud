# Makefile для DnD MUD проекта
# Поддержка виртуального окружения и стандартных операций

.PHONY: help check test clean

# Переменные
PYTHON := python3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

# Цвета для вывода
GREEN := \033[0;32m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Показать доступные команды
	@echo "$(BLUE)DnD MUD - Makefile команды:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

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
	@echo "$(BLUE)Запуск тестов...$(NC)"
	@$(VENV_PYTHON) -m pytest tests/ -v

clean: ## Очистить временные файлы
	@echo "$(BLUE)Очистка...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name "*.py~" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Очистка завершена$(NC)"
