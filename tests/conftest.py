"""Конфигурация pytest для Clean Architecture тестов.

Следует принципам чистой архитектуры и правилам проекта.
"""

import os
import sys

import pytest

# Добавляем корень проекта в путь для импортов
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)


# Таймауты для всех тестов согласно правилам проекта
@pytest.fixture(autouse=True)
def timeout_fixture():
    """Применяет таймауты ко всем тестам для предотвращения зависания."""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError("Тест превысил допустимое время выполнения")

    # Устанавливаем таймаут в 30 секунд для всех тестов
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)

    yield

    # Сбрасываем таймаут после теста
    signal.alarm(0)


def pytest_configure(config):
    """Конфигурация pytest."""
    # Добавляем маркеры для Clean Architecture слоев
    config.addinivalue_line(
        "markers", "entity: Тесты слоя Entities (бизнес-правила)"
    )
    config.addinivalue_line(
        "markers", "use_case: Тесты слоя Use Cases (бизнес-логика)"
    )
    config.addinivalue_line(
        "markers", "controller: Тесты слоя Controllers (адаптеры)"
    )
    config.addinivalue_line(
        "markers", "dto: Тесты слоя DTO (объекты передачи данных)"
    )
    config.addinivalue_line("markers", "integration: Интеграционные тесты")


def pytest_collection_modifyitems(config, items):
    """Модификация тестов перед запуском."""
    for item in items:
        # Добавляем маркеры на основе пути к файлу
        if "entities" in str(item.fspath):
            item.add_marker(pytest.mark.entity)
        elif "use_cases" in str(item.fspath):
            item.add_marker(pytest.mark.use_case)
        elif "controllers" in str(item.fspath):
            item.add_marker(pytest.mark.controller)
        elif "dto" in str(item.fspath):
            item.add_marker(pytest.mark.dto)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
