# Makefile для D&D MUD проекта
# Основные команды для разработки

.PHONY: help install run test lint format clean

# Переменные
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
SRC_DIR := src
TESTS_DIR := tests
MAIN_FILE := main.py

# Цвета для вывода
GREEN := \033[0;32m
BLUE := \033[0;34m
NC := \033[0m

help: ## Показать доступные команды
	@echo "$(BLUE)D&D MUD - Основные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(BLUE)Установка зависимостей...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	@$(VENV_BIN)/pip install --upgrade pip
	@$(VENV_BIN)/pip install -e ".[dev]"
	@echo "$(GREEN)Готово!$(NC)"

run: ## Запустить приложение
	@echo "$(BLUE)Запуск D&D MUD...$(NC)"
	@$(VENV_BIN)/$(PYTHON) $(MAIN_FILE)

test: ## Запустить все тесты
	@echo "$(BLUE)Запуск тестов...$(NC)"
	@$(VENV_BIN)/pytest $(TESTS_DIR) -v --maxfail=5

lint: ## Проверить код
	@echo "$(BLUE)Проверка кода...$(NC)"
	@$(VENV_BIN)/ruff check $(SRC_DIR) $(TESTS_DIR)
	@$(VENV_BIN)/mypy $(SRC_DIR)

format: ## Отформатировать код
	@echo "$(BLUE)Форматирование кода...$(NC)"
	@$(VENV_BIN)/black $(SRC_DIR) $(TESTS_DIR)
	@$(VENV_BIN)/ruff format $(SRC_DIR) $(TESTS_DIR)

clean: ## Очистить временные файлы
	@echo "$(BLUE)Очистка...$(NC)"
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache htmlcov .coverage .ruff_cache
	@find . -name "dnd_*test*" -type d -exec rm -rf {} + 2>/dev/null || true
	@find /tmp -name "dnd_*test*" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Очистка завершена$(NC)"


