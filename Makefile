.PHONY: help venv-recreate venv install install-hooks reinstall clean lint format format-check typecheck check test

VENV      := .venv
PYTHON    := python3.12
PIP       := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python

$(VENV)/bin/python:
	$(PYTHON) -m venv $(VENV)

.PHONY: venv
venv: $(VENV)/bin/python

.PHONY: venv-recreate
venv-recreate:
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)

.PHONY: install
install: venv
	$(PIP) install -e ".[dev]"
	$(MAKE) install-hooks

.PHONY: install-hooks
install-hooks:
	chmod +x .githooks/pre-commit
	git config core.hooksPath .githooks

.PHONY: reinstall
reinstall:
	$(PIP) uninstall -y dnd_mud
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -e ".[dev]"
	$(MAKE) install-hooks

.PHONY: clean
clean:
	rm -rf .mypy_cache .ruff_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '*.pyo' -delete 2>/dev/null || true
	find . -type l -name '*.so' -delete 2>/dev/null || true

.PHONY: lint
lint:
	$(VENV)/bin/ruff check .

.PHONY: format
format:
	$(VENV)/bin/black .

.PHONY: format-check
format-check:
	$(VENV)/bin/black --check .

.PHONY: typecheck
typecheck:
	$(VENV)/bin/mypy .

.PHONY: check
check: lint format-check typecheck

.PHONY: test
test:
	$(VENV)/bin/pytest

.PHONY: help
help:
	@echo "Доступные команды:"
	@echo ""
	@echo "  make help            — показать эту справку"
	@echo "  make venv            — создать виртуальное окружение (если нет)"
	@echo "  make venv-recreate   — пересоздать виртуальное окружение"
	@echo "  make install         — зависимости + git pre-commit (check + test)"
	@echo "  make install-hooks   — подключить .githooks/pre-commit"
	@echo "  make reinstall       — переустановить все зависимости (с удалением)"
	@echo "  make clean           — очистить кеш и временные файлы"
	@echo "  make check           — полная проверка: ruff + black --check + mypy"
	@echo "  make format          — применить black (исправить форматирование)"
	@echo "  make test            — запустить тесты"
