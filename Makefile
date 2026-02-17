# Makefile для D&D MUD проекта
# Предоставляет удобные команды для разработки, тестирования и развертывания

.PHONY: help install install-dev test test-cov test-watch lint format clean run docs build publish

# Переменные
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
SRC_DIR := src
TESTS_DIR := tests
MAIN_FILE := main.py

# Цвета для вывода
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

help: ## Показать доступные команды
	@echo "$(CYAN)D&D MUD - Доступные команды:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости проекта
	@echo "$(BLUE)Установка зависимостей...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)Создание виртуального окружения...$(NC)"; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@$(VENV_BIN)/pip install --upgrade pip
	@$(VENV_BIN)/pip install -e .
	@echo "$(GREEN)Зависимости установлены!$(NC)"

install-dev: ## Установить зависимости для разработки
	@echo "$(BLUE)Установка зависимостей для разработки...$(NC)"
	@$(MAKE) install
	@$(VENV_BIN)/pip install -e ".[dev]"
	@echo "$(GREEN)Зависимости для разработки установлены!$(NC)"

run: ## Запустить приложение
	@echo "$(BLUE)Запуск D&D MUD...$(NC)"
	@$(VENV_BIN)/$(PYTHON) $(MAIN_FILE)

test: ## Запустить все тесты
	@echo "$(BLUE)Запуск тестов...$(NC)"
	@$(VENV_BIN)/pytest $(TESTS_DIR) -v

test-cov: ## Запустить тесты с покрытием кода
	@echo "$(BLUE)Запуск тестов с покрытием кода...$(NC)"
	@$(VENV_BIN)/pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)Отчет о покрытии создан в htmlcov/index.html$(NC)"

test-watch: ## Запустить тесты в режиме отслеживания изменений
	@echo "$(BLUE)Запуск тестов в режиме отслеживания...$(NC)"
	@$(VENV_BIN)/pytest-watch $(TESTS_DIR)

test-unit: ## Запустить только unit тесты
	@echo "$(BLUE)Запуск unit тестов...$(NC)"
	@$(VENV_BIN)/pytest $(TESTS_DIR) -m "unit" -v

test-integration: ## Запустить только интеграционные тесты
	@echo "$(BLUE)Запуск интеграционных тестов...$(NC)"
	@$(VENV_BIN)/pytest $(TESTS_DIR) -m "integration" -v

test-ui: ## Запустить только UI тесты
	@echo "$(BLUE)Запуск UI тестов...$(NC)"
	@$(VENV_BIN)/pytest $(TESTS_DIR) -m "ui" -v

test-specific: ## Запустить конкретный тест (использование: make test-specific TEST=test_main.py)
	@echo "$(BLUE)Запуск теста $(TEST)...$(NC)"
	@$(VENV_BIN)/pytest $(TESTS_DIR)/$(TEST) -v

lint: ## Проверить код с помощью линтеров
	@echo "$(BLUE)Проверка кода...$(NC)"
	@echo "$(YELLOW)Ruff...$(NC)"
	@$(VENV_BIN)/ruff check $(SRC_DIR) $(TESTS_DIR)
	@echo "$(YELLOW)MyPy...$(NC)"
	@$(VENV_BIN)/mypy $(SRC_DIR)
	@echo "$(GREEN)Проверка завершена!$(NC)"

format: ## Отформатировать код
	@echo "$(BLUE)Форматирование кода...$(NC)"
	@echo "$(YELLOW)Black...$(NC)"
	@$(VENV_BIN)/black $(SRC_DIR) $(TESTS_DIR)
	@echo "$(YELLOW)Ruff...$(NC)"
	@$(VENV_BIN)/ruff format $(SRC_DIR) $(TESTS_DIR)
	@echo "$(GREEN)Код отформатирован!$(NC)"

format-check: ## Проверить форматирование кода
	@echo "$(BLUE)Проверка форматирования...$(NC)"
	@$(VENV_BIN)/black --check $(SRC_DIR) $(TESTS_DIR)
	@$(VENV_BIN)/ruff format --check $(SRC_DIR) $(TESTS_DIR)

clean: ## Очистить временные файлы
	@echo "$(BLUE)Очистка временных файлов...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type f -name ".coverage" -delete
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf dist/
	@rm -rf build/
	@echo "$(GREEN)Очистка завершена!$(NC)"

clean-all: clean ## Полная очистка включая виртуальное окружение
	@echo "$(BLUE)Полная очистка...$(NC)"
	@rm -rf $(VENV)/
	@echo "$(GREEN)Полная очистка завершена!$(NC)"

docs: ## Сгенерировать документацию
	@echo "$(BLUE)Генерация документации...$(NC)"
	@mkdir -p docs/_build
	@echo "$(YELLOW)Сбор документации из исходников...$(NC)"
	@$(VENV_BIN)/sphinx-apidoc -o docs/_build $(SRC_DIR)
	@echo "$(GREEN)Документация сгенерирована в docs/_build$(NC)"

docs-serve: ## Запустить сервер документации
	@echo "$(BLUE)Запуск сервера документации...$(NC)"
	@cd docs/_build && $(VENV_BIN)/python -m http.server 8000

build: ## Собрать проект
	@echo "$(BLUE)Сборка проекта...$(NC)"
	@$(VENV_BIN)/python -m build
	@echo "$(GREEN)Проект собран!$(NC)"

publish-test: ## Опубликовать в тестовый PyPI
	@echo "$(BLUE)Публикация в тестовый PyPI...$(NC)"
	@$(VENV_BIN)/python -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)Опубликовано в тестовый PyPI!$(NC)"

publish: ## Опубликовать в PyPI
	@echo "$(BLUE)Публикация в PyPI...$(NC)"
	@$(VENV_BIN)/python -m twine upload dist/*
	@echo "$(GREEN)Опубликовано в PyPI!$(NC)"

dev-setup: ## Настроить среду разработки
	@echo "$(BLUE)Настройка среды разработки...$(NC)"
	@$(MAKE) install-dev
	@$(MAKE) pre-commit-install
	@echo "$(GREEN)Среда разработки настроена!$(NC)"

pre-commit-install: ## Установить pre-commit hooks
	@echo "$(BLUE)Установка pre-commit hooks...$(NC)"
	@$(VENV_BIN)/pre-commit install
	@echo "$(GREEN)Pre-commit hooks установлены!$(NC)"

check-all: ## Запустить все проверки (lint + test)
	@echo "$(BLUE)Запуск всех проверок...$(NC)"
	@$(MAKE) lint
	@$(MAKE) test
	@echo "$(GREEN)Все проверки пройдены!$(NC)"

ci: ## Запустить CI/CD проверки
	@echo "$(BLUE)Запуск CI/CD проверок...$(NC)"
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) test-cov
	@echo "$(GREEN)CI/CD проверки пройдены!$(NC)"

profile: ## Запустить профилирование приложения
	@echo "$(BLUE)Запуск профилирования...$(NC)"
	@$(VENV_BIN)/python -m cProfile -o profile.stats $(MAIN_FILE)
	@echo "$(GREEN)Профилирование завершено! Результаты в profile.stats$(NC)"

benchmark: ## Запустить бенчмарки
	@echo "$(BLUE)Запуск бенчмарков...$(NC)"
	@$(VENV_BIN)/python -m pytest $(TESTS_DIR) --benchmark-only
	@echo "$(GREEN)Бенчмарки завершены!$(NC)"

security: ## Проверить безопасность кода
	@echo "$(BLUE)Проверка безопасности...$(NC)"
	@$(VENV_BIN)/bandit -r $(SRC_DIR)
	@$(VENV_BIN)/safety check
	@echo "$(GREEN)Проверка безопасности завершена!$(NC)"

deps-update: ## Обновить зависимости
	@echo "$(BLUE)Обновление зависимостей...$(NC)"
	@$(VENV_BIN)/pip list --outdated
	@$(VENV_BIN)/pip install --upgrade pip setuptools wheel
	@$(VENV_BIN)/pip install --upgrade -e ".[dev]"
	@echo "$(GREEN)Зависимости обновлены!$(NC)"

tree: ## Показать структуру проекта
	@echo "$(BLUE)Структура проекта:$(NC)"
	@tree -I '__pycache__|*.pyc|.venv|htmlcov|.pytest_cache' --dirsfirst

stats: ## Показать статистику проекта
	@echo "$(BLUE)Статистика проекта:$(NC)"
	@echo "$(YELLOW)Строк кода:$(NC)"
	@find $(SRC_DIR) -name "*.py" | xargs wc -l | tail -1
	@echo "$(YELLOW)Строк тестов:$(NC)"
	@find $(TESTS_DIR) -name "*.py" | xargs wc -l | tail -1
	@echo "$(YELLOW)Количество файлов:$(NC)"
	@find $(SRC_DIR) -name "*.py" | wc -l

# Команды для работы с данными
init-data: ## Инициализировать структуру данных
	@echo "$(BLUE)Инициализация структуры данных...$(NC)"
	@mkdir -p data/saves
	@mkdir -p data/config
	@mkdir -p data/yaml
	@mkdir -p data/mods
	@mkdir -p data/adventures
	@echo "$(GREEN)Структура данных создана!$(NC)"

backup: ## Создать резервную копию данных
	@echo "$(BLUE)Создание резервной копии...$(NC)"
	@tar -czf backup_$$(date +%Y%m%d_%H%M%S).tar.gz data/
	@echo "$(GREEN)Резервная копия создана!$(NC)"

# Команды для разработки
watch: ## Отслеживать изменения и перезапускать приложение
	@echo "$(BLUE)Запуск в режиме отслеживания...$(NC)"
	@$(VENV_BIN)/watchdog --patterns="*.py" --recursive --command='make run' $(SRC_DIR)

debug: ## Запустить приложение в режиме отладки
	@echo "$(BLUE)Запуск в режиме отладки...$(NC)"
	@$(VENV_BIN)/python -m pdb $(MAIN_FILE)

# Полезные алиасы
t: test ## Алиас для test
tc: test-cov ## Алиас для test-cov
l: lint ## Алиас для lint
f: format ## Алиас для format
c: clean ## Алиас для clean
